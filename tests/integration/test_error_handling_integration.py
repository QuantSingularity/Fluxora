import os
import sys
import time
import unittest
from typing import Any
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from code.core.circuit_breaker import CircuitBreaker, CircuitState
from code.core.fallback import DefaultValueFallback, with_fallback
from code.core.retry import RetryableError, retry
from code.core.transaction_coordinator import TransactionCoordinator, TransactionStatus


class TestErrorHandlingIntegration(unittest.TestCase):
    """
    Integration tests for error handling components working together
    """

    def test_circuit_breaker_with_retry_and_fallback(self) -> Any:
        """Test that circuit breaker, retry, and fallback work together"""
        mock = Mock()
        fallback = DefaultValueFallback("fallback_result")
        circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)

        @circuit_breaker
        @retry(max_attempts=2, retry_exceptions=RetryableError)
        @with_fallback(fallback)
        def unstable_service(fail_count=0):
            mock()
            if mock.call_count <= fail_count:
                raise RetryableError("Temporary failure")
            return "success"

        result = unstable_service(fail_count=0)
        self.assertEqual(result, "success")
        self.assertEqual(mock.call_count, 1)
        mock.reset_mock()
        result = unstable_service(fail_count=1)
        self.assertEqual(result, "success")
        self.assertEqual(mock.call_count, 2)
        mock.reset_mock()
        result = unstable_service(fail_count=2)
        self.assertEqual(result, "fallback_result")
        self.assertEqual(mock.call_count, 2)
        mock.reset_mock()
        for _ in range(3):
            result = unstable_service(fail_count=2)
            self.assertEqual(result, "fallback_result")
        self.assertEqual(circuit_breaker.state, CircuitState.OPEN)
        mock.reset_mock()
        result = unstable_service(fail_count=0)
        self.assertEqual(result, "fallback_result")
        mock.assert_not_called()
        time.sleep(0.2)
        mock.reset_mock()
        result = unstable_service(fail_count=0)
        self.assertEqual(result, "success")
        mock.assert_called_once()
        self.assertEqual(circuit_breaker.state, CircuitState.CLOSED)


class TestTransactionWithErrorHandling(unittest.TestCase):
    """
    Integration tests for distributed transactions with error handling
    """

    def test_transaction_with_retry_and_circuit_breaker(self) -> Any:
        """Test that transactions work with retry and circuit breaker"""
        coordinator = TransactionCoordinator()
        mock = Mock()
        circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)

        class TestParticipant:

            def __init__(self, name, fail_prepare=False, fail_commit=False):
                self.name = name
                self.fail_prepare = fail_prepare
                self.fail_commit = fail_commit
                self.prepared_txns = set()
                self.committed_txns = set()
                self.aborted_txns = set()

            @circuit_breaker
            @retry(max_attempts=2, retry_exceptions=RetryableError)
            def prepare(self, transaction_id):
                mock(f"{self.name}_prepare")
                if self.fail_prepare:
                    raise RetryableError(f"{self.name} prepare failed")
                self.prepared_txns.add(transaction_id)
                return True

            @circuit_breaker
            @retry(max_attempts=2, retry_exceptions=RetryableError)
            def commit(self, transaction_id):
                mock(f"{self.name}_commit")
                if self.fail_commit:
                    raise RetryableError(f"{self.name} commit failed")
                if transaction_id not in self.prepared_txns:
                    return False
                self.committed_txns.add(transaction_id)
                return True

            @circuit_breaker
            def abort(self, transaction_id):
                mock(f"{self.name}_abort")
                self.aborted_txns.add(transaction_id)
                return True

        transaction_id = coordinator.create_transaction()
        participant1 = TestParticipant("p1")
        participant2 = TestParticipant("p2")
        coordinator.register_participant(transaction_id, participant1)
        coordinator.register_participant(transaction_id, participant2)
        result = coordinator.execute_transaction(transaction_id)
        self.assertTrue(result)
        self.assertEqual(
            coordinator.get_transaction_status(transaction_id),
            TransactionStatus.COMMITTED,
        )
        mock.assert_any_call("p1_prepare")
        mock.assert_any_call("p2_prepare")
        mock.assert_any_call("p1_commit")
        mock.assert_any_call("p2_commit")
        mock.reset_mock()
        transaction_id = coordinator.create_transaction()
        participant1 = TestParticipant("p1")
        participant2 = TestParticipant("p2", fail_prepare=True)
        coordinator.register_participant(transaction_id, participant1)
        coordinator.register_participant(transaction_id, participant2)
        result = coordinator.execute_transaction(transaction_id)
        self.assertFalse(result)
        self.assertEqual(
            coordinator.get_transaction_status(transaction_id),
            TransactionStatus.ABORTED,
        )
        mock.assert_any_call("p1_prepare")
        mock.assert_any_call("p2_prepare")
        mock.assert_any_call("p2_prepare")
        mock.assert_any_call("p1_abort")
        mock.assert_any_call("p2_abort")
        self.assertNotIn("p1_commit", [call[0][0] for call in mock.call_args_list])
        self.assertNotIn("p2_commit", [call[0][0] for call in mock.call_args_list])


if __name__ == "__main__":
    unittest.main()
