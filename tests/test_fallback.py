from typing import Any
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from code.core.fallback import (
    CachedDataFallback,
    ChainedFallback,
    DefaultValueFallback,
    FallbackStrategy,
    with_fallback,
)


class TestFallback(unittest.TestCase):

    def test_fallback_strategy_base_class(self) -> Any:
        """Test that the base FallbackStrategy class requires implementation"""
        strategy = FallbackStrategy()
        with self.assertRaises(NotImplementedError):
            strategy.execute()

    def test_cached_data_fallback(self) -> Any:
        """Test that CachedDataFallback returns cached data"""
        cache_provider = lambda: {"data": "cached"}
        strategy = CachedDataFallback(cache_provider)
        result = strategy.execute()
        self.assertEqual(result, {"data": "cached"})

    def test_default_value_fallback(self) -> Any:
        """Test that DefaultValueFallback returns the default value"""
        default_value = "default"
        strategy = DefaultValueFallback(default_value)
        result = strategy.execute()
        self.assertEqual(result, "default")

    def test_chained_fallback_first_succeeds(self) -> Any:
        """Test that ChainedFallback returns the result of the first successful strategy"""
        strategy1 = DefaultValueFallback("first")
        strategy2 = DefaultValueFallback("second")
        chained = ChainedFallback([strategy1, strategy2])
        result = chained.execute()
        self.assertEqual(result, "first")

    def test_chained_fallback_first_fails(self) -> Any:
        """Test that ChainedFallback tries the next strategy if the first fails"""

        class FailingStrategy(FallbackStrategy):

            def execute(self, *args, **kwargs):
                raise Exception("Failed")

        strategy1 = FailingStrategy()
        strategy2 = DefaultValueFallback("second")
        chained = ChainedFallback([strategy1, strategy2])
        result = chained.execute()
        self.assertEqual(result, "second")

    def test_chained_fallback_all_fail(self) -> Any:
        """Test that ChainedFallback raises an exception if all strategies fail"""

        class FailingStrategy(FallbackStrategy):

            def execute(self, *args, **kwargs):
                raise Exception("Failed")

        strategy1 = FailingStrategy()
        strategy2 = FailingStrategy()
        chained = ChainedFallback([strategy1, strategy2])
        with self.assertRaises(Exception):
            chained.execute()

    def test_with_fallback_decorator_success(self) -> Any:
        """Test that with_fallback decorator returns the function result on success"""
        fallback = DefaultValueFallback("fallback")

        @with_fallback(fallback)
        def success_func():
            return "success"

        result = success_func()
        self.assertEqual(result, "success")

    def test_with_fallback_decorator_failure(self) -> Any:
        """Test that with_fallback decorator returns the fallback result on failure"""
        fallback = DefaultValueFallback("fallback")

        @with_fallback(fallback)
        def failing_func():
            raise Exception("Failed")

        result = failing_func()
        self.assertEqual(result, "fallback")

    def test_with_fallback_decorator_args(self) -> Any:
        """Test that with_fallback decorator works with function arguments"""
        fallback = DefaultValueFallback("fallback")

        @with_fallback(fallback)
        def func_with_args(arg1, arg2=None):
            if arg2 is None:
                raise Exception("arg2 is None")
            return f"{arg1}-{arg2}"

        result1 = func_with_args("test", "value")
        self.assertEqual(result1, "test-value")
        result2 = func_with_args("test")
        self.assertEqual(result2, "fallback")


if __name__ == "__main__":
    unittest.main()
