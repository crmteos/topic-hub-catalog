"""Примітиви стійкості для безключового вебпошуку (беклог T3).

Немає ключів, токенів, емейлів і жодних секретів. Усі компоненти
детерміновані за параметрами й приймають clock/sleep/rng через аргументи,
щоб їх можна було перевірити unit-тестами без мережі.

Використання в web_search_server.py:

    limiter = RateLimiter()
    breaker = CircuitBreaker(threshold=3, cooldown_s=60.0)
    cache = TTLCache(ttl_s=300.0)
    key = f"{query_id(query)}|{limit}|{','.join(sorted(names))}"
    cached = cache.get(key)
    ...
    fetch_guarded(name, lambda: fn(query, limit), rps, limiter, breaker)

HTTP 429 ніколи не ретраїться: він одразу піднімає RateLimited, щоб причина
потрапила в `sources_failed` без каскаду повторів.
"""

from __future__ import annotations

import hashlib
import random
import threading
import time
from typing import Any, Callable


class RateLimited(Exception):
    """Джерело відповіло 429. Повтор не виконується."""


class CircuitOpen(Exception):
    """Circuit breaker тимчасово закрив джерело."""


def query_id(query: str) -> str:
    """Канонічний ID запиту, ідентичний до hub_server._query_id."""
    normalized = " ".join(str(query).split()).casefold()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def http_status(exc: BaseException) -> int | None:
    code = getattr(exc, "code", None)
    try:
        return int(code) if code is not None else None
    except (TypeError, ValueError):
        return None


class RateLimiter:
    """Per-source мінімальний інтервал між записами запитів."""

    def __init__(self) -> None:
        self._last: dict[str, float] = {}
        self._lock = threading.Lock()

    @staticmethod
    def interval(rps: float) -> float:
        try:
            value = float(rps)
        except (TypeError, ValueError):
            return 0.0
        return 1.0 / value if value > 0 else 0.0

    def wait(
        self,
        name: str,
        rps: float,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        interval = self.interval(rps)
        if interval <= 0:
            return
        with self._lock:
            now = clock()
            previous = self._last.get(name)
            delay = previous + interval - now if previous is not None else 0.0
        if delay > 0:
            sleep(delay)
        with self._lock:
            self._last[name] = clock()


class CircuitBreaker:
    """Тимчасово вимикає джерело після повторюваних помилок."""

    def __init__(self, threshold: int = 3, cooldown_s: float = 60.0) -> None:
        self.threshold = max(1, int(threshold))
        self.cooldown_s = max(0.0, float(cooldown_s))
        self._state: dict[str, dict[str, float]] = {}
        self._lock = threading.Lock()

    def _slot(self, name: str) -> dict[str, float]:
        return self._state.setdefault(name, {"failures": 0.0, "open_until": 0.0})

    def allow(self, name: str, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else now
        with self._lock:
            slot = self._slot(name)
            if slot["open_until"] > current:
                return False
            if slot["open_until"]:
                # half-open: один пробний запит, стан скинуто
                slot["open_until"] = 0.0
                slot["failures"] = 0.0
            return True

    def record_ok(self, name: str) -> None:
        with self._lock:
            slot = self._slot(name)
            slot["failures"] = 0.0
            slot["open_until"] = 0.0

    def record_error(self, name: str, now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        with self._lock:
            slot = self._slot(name)
            slot["failures"] += 1.0
            if slot["failures"] >= self.threshold:
                slot["open_until"] = current + self.cooldown_s

    def state(self, name: str, now: float | None = None) -> str:
        current = time.monotonic() if now is None else now
        with self._lock:
            slot = self._slot(name)
            if slot["open_until"] > current:
                return "open"
            if slot["failures"]:
                return "half-open"
            return "closed"


class TTLCache:
    """КешFUL ключ→відповідь із часом життя. Дані не пишуться на диск."""

    def __init__(self, ttl_s: float = 300.0) -> None:
        self.ttl_s = max(0.0, float(ttl_s))
        self._data: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str, now: float | None = None) -> Any | None:
        current = time.monotonic() if now is None else now
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            stamp, value = entry
            if self.ttl_s <= 0 or current - stamp >= self.ttl_s:
                self._data.pop(key, None)
                return None
            return value

    def put(self, key: str, value: Any, now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        with self._lock:
            self._data[key] = (current, value)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)


def backoff_delay(
    attempt: int,
    base: float = 0.5,
    cap: float = 8.0,
    jitter: float = 0.25,
    rng: Callable[[], float] = random.random,
) -> float:
    """Експоненційний backoff із симетричним jitter (0..1)."""
    raw = min(cap, base * (2 ** max(0, int(attempt))))
    spread = max(0.0, min(1.0, float(jitter)))
    return raw * (1.0 - spread + 2.0 * spread * float(rng()))


def fetch_guarded(
    name: str,
    call: Callable[[], Any],
    rps: float,
    limiter: RateLimiter,
    breaker: CircuitBreaker,
    *,
    retries: int = 2,
    sleep: Callable[[float], None] = time.sleep,
    rng: Callable[[], float] = random.random,
    now: float | None = None,
) -> Any:
    """Один захищений виклик джерела.

    - pps/rps обмежується пер-source RateLimiter;
    - 429 → RateLimited без жодного повтору;
    - інші 4xx → помилка без повтору;
    - 408/5xx/мережеві помилки → backoff із jitter, не більше `retries`;
    - після `threshold` помилок джерело тимчасово open.
    """
    limiter.wait(name, rps)
    if not breaker.allow(name, now):
        raise CircuitOpen(f"CircuitOpen: {name}")

    attempts = max(0, int(retries)) + 1
    for attempt in range(attempts):
        try:
            value = call()
        except Exception as exc:
            status = http_status(exc)
            if status == 429:
                breaker.record_error(name, now)
                raise RateLimited(f"RateLimited: HTTP 429 ({name})") from exc
            if status is not None and 400 <= status < 500 and status != 408:
                breaker.record_error(name, now)
                raise
            if attempt < attempts - 1:
                sleep(backoff_delay(attempt, rng=rng))
                continue
            breaker.record_error(name, now)
            raise
        breaker.record_ok(name)
        return value
    raise RuntimeError(f"Недосяжний стан для {name}")
