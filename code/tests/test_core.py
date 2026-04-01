"""Tests for core utilities."""

import pytest
from core.circuit_breaker import CircuitBreaker, CircuitBreakerError, CircuitState
from core.retry import retry

# ── Circuit Breaker ────────────────────────────────────────────────────────────


def test_circuit_breaker_closed_on_success():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
    result = cb.call(lambda: "ok")
    assert result == "ok"
    assert cb.state == CircuitState.CLOSED


def test_circuit_breaker_opens_after_threshold():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

    def failing():
        raise ValueError("fail")

    for _ in range(3):
        try:
            cb.call(failing)
        except ValueError:
            pass

    assert cb.state == CircuitState.OPEN


def test_circuit_breaker_raises_when_open():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)

    def failing():
        raise ValueError("fail")

    try:
        cb.call(failing)
    except ValueError:
        pass

    with pytest.raises(CircuitBreakerError):
        cb.call(lambda: "should not run")


def test_circuit_breaker_uses_fallback():
    cb = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout=60,
        fallback_function=lambda: "fallback",
    )

    def failing():
        raise ValueError("fail")

    # First call fails but returns fallback
    result = cb.call(failing)
    assert result == "fallback"
    # Now open – fallback used immediately
    result2 = cb.call(lambda: "never")
    assert result2 == "fallback"


def test_circuit_breaker_reset():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
    try:
        cb.call(lambda: (_ for _ in ()).throw(ValueError()))
    except ValueError:
        pass
    cb.reset()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


# ── Retry Decorator ────────────────────────────────────────────────────────────


def test_retry_succeeds_on_first_attempt():
    call_count = {"n": 0}

    @retry(max_attempts=3)
    def always_ok():
        call_count["n"] += 1
        return "done"

    result = always_ok()
    assert result == "done"
    assert call_count["n"] == 1


def test_retry_retries_on_failure():
    call_count = {"n": 0}

    @retry(max_attempts=3, base_delay=0.0, retry_exceptions=(ValueError,))
    def fails_twice():
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise ValueError("retry me")
        return "success"

    result = fails_twice()
    assert result == "success"
    assert call_count["n"] == 3


def test_retry_exhausts_attempts():
    @retry(max_attempts=3, base_delay=0.0, retry_exceptions=(ValueError,))
    def always_fails():
        raise ValueError("always")

    with pytest.raises(ValueError):
        always_fails()
