"""Unit-тести примітивів стійкості T3. Без мережі, без секретів, stdlib only.

Запуск: py -3 -m unittest discover -s . -p 'test_resilience.py' -v
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import unittest

from resilience import (
    CircuitBreaker,
    CircuitOpen,
    RateLimited,
    RateLimiter,
    TTLCache,
    backoff_delay,
    fetch_guarded,
    query_id,
)


class FakeError(Exception):
    def __init__(self, code: int):
        super().__init__(f"HTTP {code}")
        self.code = code


class QueryIdTests(unittest.TestCase):
    def test_matches_hub_formula(self):
        import hashlib

        raw = "  arXiv:0711.0770  "
        expected = hashlib.sha256(" ".join(raw.split()).casefold().encode("utf-8")).hexdigest()[:16]
        self.assertEqual(query_id(raw), expected)

    def test_case_and_whitespace_normalized(self):
        self.assertEqual(query_id("  Hello   WORLD "), query_id("hello world"))
        self.assertNotEqual(query_id("a"), query_id("b"))


class CacheTests(unittest.TestCase):
    def test_hit_within_ttl_and_miss_after(self):
        cache = TTLCache(ttl_s=10.0)
        cache.put("k", "value", now=100.0)
        self.assertEqual(cache.get("k", now=105.0), "value")
        self.assertIsNone(cache.get("k", now=111.0))
        self.assertEqual(len(cache), 0)

    def test_zero_ttl_never_hits(self):
        cache = TTLCache(ttl_s=0.0)
        cache.put("k", "value", now=100.0)
        self.assertIsNone(cache.get("k", now=100.0))


class RateLimiterTests(unittest.TestCase):
    def test_interval_math(self):
        self.assertAlmostEqual(RateLimiter.interval(2.0), 0.5)
        self.assertAlmostEqual(RateLimiter.interval(0.33), 1 / 0.33)
        self.assertEqual(RateLimiter.interval(0), 0.0)

    def test_second_call_sleeps(self):
        limiter = RateLimiter()
        clock = [0.0]
        slept = []
        limiter.wait("a", 1.0, clock=lambda: clock[0], sleep=slept.append)
        clock[0] = 0.25
        limiter.wait("a", 1.0, clock=lambda: clock[0], sleep=slept.append)
        self.assertEqual(len(slept), 1)
        self.assertAlmostEqual(slept[0], 0.75, places=5)

    def test_per_source_isolation(self):
        limiter = RateLimiter()
        slept = []
        limiter.wait("a", 1.0, clock=lambda: 0.0, sleep=slept.append)
        limiter.wait("b", 1.0, clock=lambda: 0.0, sleep=slept.append)
        self.assertEqual(slept, [])


class CircuitBreakerTests(unittest.TestCase):
    def test_opens_after_threshold_and_recovers(self):
        cb = CircuitBreaker(threshold=2, cooldown_s=10.0)
        self.assertTrue(cb.allow("s", now=0.0))
        cb.record_error("s", now=0.0)
        self.assertEqual(cb.state("s", now=0.0), "half-open")
        cb.record_error("s", now=1.0)
        self.assertEqual(cb.state("s", now=1.0), "open")
        self.assertFalse(cb.allow("s", now=2.0))
        self.assertTrue(cb.allow("s", now=12.0))  # half-open пробний запит
        self.assertEqual(cb.state("s", now=12.0), "closed")

    def test_success_resets(self):
        cb = CircuitBreaker(threshold=2)
        cb.record_error("s")
        cb.record_ok("s")
        self.assertEqual(cb.state("s"), "closed")


class BackoffTests(unittest.TestCase):
    def test_bounded_jitter(self):
        self.assertAlmostEqual(backoff_delay(0, rng=lambda: 0.0), 0.5 * 0.75)
        self.assertAlmostEqual(backoff_delay(0, rng=lambda: 1.0), 0.5 * 1.25)
        self.assertLessEqual(backoff_delay(20, base=1.0, cap=8.0, rng=lambda: 1.0), 10.0)


class FetchGuardedTests(unittest.TestCase):
    def setUp(self):
        self.limiter = RateLimiter()
        self.cb = CircuitBreaker(threshold=3)

    def test_429_no_retry_cascade(self):
        calls = []

        def boom():
            calls.append(1)
            raise FakeError(429)

        with self.assertRaises(RateLimited):
            fetch_guarded("s", boom, 0, self.limiter, self.cb, retries=3)
        self.assertEqual(len(calls), 1, "429 не має викликати повторів")

    def test_5xx_retries_then_succeeds(self):
        calls = []

        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise FakeError(500)
            return ["ok"]

        value = fetch_guarded(
            "s", flaky, 0, self.limiter, self.cb, retries=2, sleep=lambda _: None, rng=lambda: 0.5
        )
        self.assertEqual(value, ["ok"])
        self.assertEqual(len(calls), 3)

    def test_4xx_no_retry(self):
        calls = []

        def bad():
            calls.append(1)
            raise FakeError(404)

        with self.assertRaises(FakeError):
            fetch_guarded("s", bad, 0, self.limiter, self.cb, retries=3, sleep=lambda _: None)
        self.assertEqual(len(calls), 1)

    def test_open_circuit_does_not_call_source(self):
        calls = []
        self.cb.record_error("s", now=0.0)
        self.cb.record_error("s", now=1.0)
        self.cb.record_error("s", now=2.0)  # threshold=3 → open

        def should_not_run():
            calls.append(1)
            return []

        with self.assertRaises(CircuitOpen):
            fetch_guarded("s", should_not_run, 0, self.limiter, self.cb, now=3.0)
        self.assertEqual(calls, [])


class AccessProfileTests(unittest.TestCase):
    def test_only_keyless_active(self):
        import access_profiles

        active = [key for key, value in access_profiles.PROFILES.items() if value["active"]]
        self.assertEqual(active, ["keyless"])

    def test_inactive_profiles_never_resolve(self):
        import os

        import access_profiles

        os.environ["TOPIC_CONTACT_MAILTO"] = "someone@example.invalid"
        os.environ["TOPIC_OPENALEX_API_KEY"] = "fake-value-not-a-secret"
        try:
            self.assertEqual(access_profiles.resolve("polite-mailto"), {})
            self.assertEqual(access_profiles.resolve("api-key-env"), {})
            self.assertEqual(access_profiles.resolve("keyless"), {})
            self.assertEqual(access_profiles.resolve("unknown"), {})
        finally:
            os.environ.pop("TOPIC_CONTACT_MAILTO", None)
            os.environ.pop("TOPIC_OPENALEX_API_KEY", None)

    def test_describe_has_no_values(self):
        import access_profiles

        for row in access_profiles.describe():
            self.assertNotIn("credential_env", row)
            self.assertNotIn("value", row)


if __name__ == "__main__":
    unittest.main(verbosity=2)
