"""Tests for core utilities: CircuitBreaker, retry, fallback, data validation."""

import time

import pytest
from core.circuit_breaker import CircuitBreaker, CircuitBreakerError, CircuitState
from core.retry import NonRetryableError, RetryableError, retry

# ===========================================================================
# Circuit Breaker
# ===========================================================================


class TestCircuitBreakerClosed:
    def test_successful_call_returns_value(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
        assert cb.call(lambda: "ok") == "ok"

    def test_state_remains_closed_after_success(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
        cb.call(lambda: 42)
        assert cb.state == CircuitState.CLOSED

    def test_failure_count_increments(self):
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

        def fail():
            raise ValueError("boom")

        for i in range(3):
            with pytest.raises(ValueError):
                cb.call(fail)

        assert cb.failure_count == 3
        assert cb.state == CircuitState.CLOSED

    def test_opens_exactly_at_threshold(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

        def fail():
            raise ValueError("fail")

        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(fail)

        assert cb.state == CircuitState.OPEN

    def test_does_not_open_before_threshold(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

        def fail():
            raise ValueError("fail")

        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail)

        assert cb.state == CircuitState.CLOSED


class TestCircuitBreakerOpen:
    def test_raises_circuit_breaker_error_when_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)

        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError()))

        with pytest.raises(CircuitBreakerError):
            cb.call(lambda: "should not run")

    def test_uses_fallback_when_open(self):
        cb = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=60,
            fallback_function=lambda: "fallback_value",
        )

        def fail():
            raise RuntimeError("service down")

        result = cb.call(fail)
        assert result == "fallback_value"

        result2 = cb.call(lambda: "never")
        assert result2 == "fallback_value"

    def test_fallback_also_used_on_first_failure(self):
        cb = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=60,
            fallback_function=lambda: "fb",
        )
        assert cb.call(lambda: (_ for _ in ()).throw(IOError())) == "fb"


class TestCircuitBreakerHalfOpen:
    def test_transitions_to_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0)

        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError()))

        time.sleep(0.01)
        assert cb.state == CircuitState.OPEN

        # Next call should probe (half-open) then succeed → closed
        result = cb.call(lambda: "recovered")
        assert result == "recovered"
        assert cb.state == CircuitState.CLOSED

    def test_reopens_on_half_open_failure(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0)

        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError()))

        time.sleep(0.01)

        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError()))

        assert cb.state == CircuitState.OPEN


class TestCircuitBreakerReset:
    def test_reset_clears_all_state(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)

        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError()))

        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.last_failure_time == 0.0

    def test_works_normally_after_reset(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)

        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError()))

        cb.reset()
        assert cb.call(lambda: "works") == "works"


class TestCircuitBreakerGetState:
    def test_get_state_returns_dict(self):
        cb = CircuitBreaker(failure_threshold=3)
        state = cb.get_state()
        assert isinstance(state, dict)
        assert "state" in state
        assert "failure_count" in state
        assert "last_failure_time" in state

    def test_get_state_reflects_current_state(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60)

        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError()))

        state = cb.get_state()
        assert state["failure_count"] == 1
        assert state["state"] == CircuitState.CLOSED.value


class TestCircuitBreakerDecorator:
    def test_used_as_decorator(self):
        cb = CircuitBreaker(failure_threshold=3)

        @cb
        def my_func(x):
            return x * 2

        assert my_func(5) == 10

    def test_decorator_propagates_exception(self):
        cb = CircuitBreaker(failure_threshold=5)

        @cb
        def broken():
            raise ValueError("boom")

        with pytest.raises(ValueError):
            broken()


# ===========================================================================
# Retry Decorator
# ===========================================================================


class TestRetrySuccess:
    def test_returns_on_first_attempt(self):
        call_count = {"n": 0}

        @retry(max_attempts=3)
        def always_ok():
            call_count["n"] += 1
            return "done"

        assert always_ok() == "done"
        assert call_count["n"] == 1

    def test_succeeds_after_transient_failures(self):
        call_count = {"n": 0}

        @retry(max_attempts=3, base_delay=0.0, retry_exceptions=(ValueError,))
        def flaky():
            call_count["n"] += 1
            if call_count["n"] < 3:
                raise ValueError("not yet")
            return "success"

        assert flaky() == "success"
        assert call_count["n"] == 3

    def test_single_attempt_allowed(self):
        @retry(max_attempts=1, base_delay=0.0)
        def ok():
            return "fine"

        assert ok() == "fine"


class TestRetryFailure:
    def test_raises_after_exhausting_attempts(self):
        call_count = {"n": 0}

        @retry(max_attempts=3, base_delay=0.0, retry_exceptions=(ValueError,))
        def always_fails():
            call_count["n"] += 1
            raise ValueError("always")

        with pytest.raises(ValueError, match="always"):
            always_fails()

        assert call_count["n"] == 3

    def test_does_not_retry_non_matching_exception(self):
        call_count = {"n": 0}

        @retry(max_attempts=5, base_delay=0.0, retry_exceptions=(IOError,))
        def wrong_exc():
            call_count["n"] += 1
            raise ValueError("not an IOError")

        with pytest.raises(ValueError):
            wrong_exc()

        assert call_count["n"] == 1

    def test_re_raises_last_exception(self):
        errors = []

        @retry(max_attempts=2, base_delay=0.0)
        def track_and_fail():
            err = RuntimeError("attempt")
            errors.append(err)
            raise err

        with pytest.raises(RuntimeError):
            track_and_fail()

        assert len(errors) == 2


class TestRetryBackoff:
    def test_respects_max_delay(self):
        """No sleep should exceed max_delay even with large backoff."""
        sleeps = []
        import core.retry as retry_mod

        original_sleep = retry_mod.time.sleep

        def mock_sleep(s):
            sleeps.append(s)

        retry_mod.time.sleep = mock_sleep
        try:

            @retry(
                max_attempts=5,
                base_delay=1.0,
                max_delay=2.0,
                backoff_factor=10.0,
                jitter=False,
            )
            def fail():
                raise ValueError()

            with pytest.raises(ValueError):
                fail()
        finally:
            retry_mod.time.sleep = original_sleep

        assert all(s <= 2.0 for s in sleeps)

    def test_no_sleep_on_last_attempt(self):
        sleeps = []
        import core.retry as retry_mod

        original_sleep = retry_mod.time.sleep
        retry_mod.time.sleep = lambda s: sleeps.append(s)
        try:

            @retry(max_attempts=3, base_delay=1.0, jitter=False)
            def fail():
                raise ValueError()

            with pytest.raises(ValueError):
                fail()
        finally:
            retry_mod.time.sleep = original_sleep

        # 3 attempts → 2 sleeps (between attempt 1→2 and 2→3, not after 3)
        assert len(sleeps) == 2


class TestRetryExceptionClasses:
    def test_retryable_error_is_exception(self):
        assert issubclass(RetryableError, Exception)

    def test_non_retryable_error_is_exception(self):
        assert issubclass(NonRetryableError, Exception)

    def test_retry_on_retryable_error(self):
        call_count = {"n": 0}

        @retry(max_attempts=3, base_delay=0.0, retry_exceptions=(RetryableError,))
        def flaky():
            call_count["n"] += 1
            if call_count["n"] < 3:
                raise RetryableError("try again")
            return "ok"

        assert flaky() == "ok"
        assert call_count["n"] == 3


# ===========================================================================
# Data Validation
# ===========================================================================


class TestDataValidation:
    def test_valid_dataframe_passes(self):
        import pandas as pd
        from data.data_validator import validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
                "consumption_kwh": [10.0, 20.0, 15.0, 30.0, 25.0],
            }
        )
        result = validate_raw_data(df)
        assert result.success is True
        assert result.errors == []

    def test_missing_required_column_raises(self):
        import pandas as pd
        from data.data_validator import DataValidationError, validate_raw_data

        df = pd.DataFrame(
            {"timestamp": pd.date_range("2024-01-01", periods=3, freq="h")}
        )
        with pytest.raises(DataValidationError, match="consumption_kwh"):
            validate_raw_data(df)

    def test_negative_consumption_raises(self):
        import pandas as pd
        from data.data_validator import DataValidationError, validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
                "consumption_kwh": [10.0, -5.0, 20.0],
            }
        )
        with pytest.raises(DataValidationError, match="negative"):
            validate_raw_data(df)

    def test_null_consumption_raises(self):
        import pandas as pd
        from data.data_validator import DataValidationError, validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
                "consumption_kwh": [10.0, None, 20.0],
            }
        )
        with pytest.raises(DataValidationError, match="null"):
            validate_raw_data(df)

    def test_humidity_out_of_range_raises(self):
        import pandas as pd
        from data.data_validator import DataValidationError, validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=2, freq="h"),
                "consumption_kwh": [10.0, 20.0],
                "humidity_percent": [50.0, 150.0],
            }
        )
        with pytest.raises(DataValidationError, match="humidity"):
            validate_raw_data(df)

    def test_temperature_out_of_range_raises(self):
        import pandas as pd
        from data.data_validator import DataValidationError, validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=2, freq="h"),
                "consumption_kwh": [10.0, 20.0],
                "temperature_c": [20.0, 999.0],
            }
        )
        with pytest.raises(DataValidationError, match="temperature"):
            validate_raw_data(df)

    def test_validate_energy_dataframe_empty(self):
        import pandas as pd
        from data.data_validator import validate_energy_dataframe

        result = validate_energy_dataframe(pd.DataFrame())
        assert result["valid"] is False
        assert result["row_count"] == 0

    def test_validate_energy_dataframe_valid(self):
        import pandas as pd
        from data.data_validator import validate_energy_dataframe

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=4, freq="h"),
                "consumption_kwh": [10.0, 20.0, 15.0, 25.0],
            }
        )
        result = validate_energy_dataframe(df)
        assert result["valid"] is True
        assert result["row_count"] == 4


# ===========================================================================
# Fallback Strategies
# ===========================================================================


class TestFallbackStrategies:
    def test_cached_data_fallback(self):
        from core.fallback import CachedDataFallback

        fb = CachedDataFallback(cache_provider=lambda: {"cached": True})
        assert fb.execute() == {"cached": True}

    def test_default_value_fallback(self):
        from core.fallback import DefaultValueFallback

        fb = DefaultValueFallback(default_value=42)
        assert fb.execute() == 42

    def test_chained_fallback_uses_first_success(self):
        from core.fallback import (
            CachedDataFallback,
            ChainedFallback,
            DefaultValueFallback,
        )

        call_log = []

        def provider():
            call_log.append("cached")
            return "from_cache"

        fb = ChainedFallback(
            [
                CachedDataFallback(provider),
                DefaultValueFallback("default"),
            ]
        )
        assert fb.execute() == "from_cache"
        assert call_log == ["cached"]

    def test_chained_fallback_falls_through(self):
        from core.fallback import ChainedFallback, FallbackStrategy

        class AlwaysFails(FallbackStrategy):
            def execute(self, *args, **kwargs):
                raise RuntimeError("fail")

        from core.fallback import DefaultValueFallback

        fb = ChainedFallback([AlwaysFails(), DefaultValueFallback("safe")])
        assert fb.execute() == "safe"

    def test_chained_fallback_raises_if_all_fail(self):
        from core.fallback import ChainedFallback, FallbackStrategy

        class AlwaysFails(FallbackStrategy):
            def execute(self, *args, **kwargs):
                raise RuntimeError("fail")

        fb = ChainedFallback([AlwaysFails(), AlwaysFails()])
        with pytest.raises(RuntimeError):
            fb.execute()

    def test_with_fallback_decorator(self):
        from core.fallback import DefaultValueFallback, with_fallback

        @with_fallback(DefaultValueFallback("default"))
        def risky():
            raise IOError("network gone")

        assert risky() == "default"

    def test_with_fallback_does_not_intercept_success(self):
        from core.fallback import DefaultValueFallback, with_fallback

        @with_fallback(DefaultValueFallback("default"))
        def ok():
            return "real_value"

        assert ok() == "real_value"
