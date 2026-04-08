"""Unit tests for fallback strategies."""

import pytest
from app.core.fallback import (
    CachedDataFallback,
    ChainedFallback,
    DefaultValueFallback,
    FallbackStrategy,
    with_fallback,
)


class TestCachedDataFallback:
    def test_returns_cached_value(self):
        fb = CachedDataFallback(cache_provider=lambda: {"cached": True})
        assert fb.execute() == {"cached": True}

    def test_calls_provider_each_time(self):
        call_count = {"n": 0}

        def provider():
            call_count["n"] += 1
            return call_count["n"]

        fb = CachedDataFallback(cache_provider=provider)
        assert fb.execute() == 1
        assert fb.execute() == 2


class TestDefaultValueFallback:
    def test_returns_default_value(self):
        fb = DefaultValueFallback(default_value=42)
        assert fb.execute() == 42

    def test_returns_none_default(self):
        fb = DefaultValueFallback(default_value=None)
        assert fb.execute() is None

    def test_returns_dict_default(self):
        default = {"key": "value"}
        fb = DefaultValueFallback(default_value=default)
        assert fb.execute() == default


class TestChainedFallback:
    def test_uses_first_strategy(self):
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

    def test_falls_through_to_second(self):
        class AlwaysFails(FallbackStrategy):
            def execute(self, *args, **kwargs):
                raise RuntimeError("fail")

        fb = ChainedFallback([AlwaysFails(), DefaultValueFallback("safe")])
        assert fb.execute() == "safe"

    def test_raises_if_all_fail(self):
        class AlwaysFails(FallbackStrategy):
            def execute(self, *args, **kwargs):
                raise RuntimeError("fail")

        fb = ChainedFallback([AlwaysFails(), AlwaysFails()])
        with pytest.raises(RuntimeError):
            fb.execute()

    def test_empty_chain_raises(self):
        fb = ChainedFallback([])
        with pytest.raises((RuntimeError, Exception)):
            fb.execute()


class TestWithFallbackDecorator:
    def test_returns_function_result_on_success(self):
        @with_fallback(DefaultValueFallback("default"))
        def ok():
            return "real_value"

        assert ok() == "real_value"

    def test_uses_fallback_on_exception(self):
        @with_fallback(DefaultValueFallback("default"))
        def risky():
            raise IOError("network gone")

        assert risky() == "default"

    def test_fallback_with_cached_provider(self):
        @with_fallback(CachedDataFallback(lambda: "cached"))
        def broken():
            raise RuntimeError("broken")

        assert broken() == "cached"

    def test_fallback_not_called_on_success(self):
        called = {"n": 0}

        def provider():
            called["n"] += 1
            return "cache"

        @with_fallback(CachedDataFallback(provider))
        def ok():
            return "ok"

        result = ok()
        assert result == "ok"
        assert called["n"] == 0


class TestFallbackStrategyABC:
    def test_base_raises_not_implemented(self):
        fb = FallbackStrategy()
        with pytest.raises(NotImplementedError):
            fb.execute()
