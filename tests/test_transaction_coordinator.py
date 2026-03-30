from typing import Any
import os
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from code.core.transaction_coordinator import (
    TransactionCoordinator,
    TransactionParticipant,
    TransactionStatus,
)


class TestTransactionCoordinator(unittest.TestCase):

    def setUp(self) -> Any:
        self.coordinator = TransactionCoordinator()

    def test_create_transaction(self) -> Any:
        """Test that create_transaction returns a valid transaction ID"""
        transaction_id = self.coordinator.create_transaction()
        self.assertIsNotNone(transaction_id)
        self.assertIsInstance(transaction_id, str)
        self.assertTrue(len(transaction_id) > 0)

    def test_register_participant(self) -> Any:
        """Test that register_participant adds a participant to the transaction"""
        transaction_id = self.coordinator.create_transaction()
        participant = Mock(spec=TransactionParticipant)
        participant.prepare.return_value = True
        participant.commit.return_value = True
        participant.abort.return_value = True
        self.coordinator.register_participant(transaction_id, participant)
        self.assertIn(transaction_id, self.coordinator.transactions)
        self.assertIn(
            participant, self.coordinator.transactions[transaction_id]["participants"]
        )

    def test_prepare_transaction_success(self) -> Any:
        """Test that prepare_transaction prepares all participants"""
        transaction_id = self.coordinator.create_transaction()
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True
        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = True
        participant2.commit.return_value = True
        participant2.abort.return_value = True
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)
        result = self.coordinator.prepare_transaction(transaction_id)
        self.assertTrue(result)
        participant1.prepare.assert_called_once_with(transaction_id)
        participant2.prepare.assert_called_once_with(transaction_id)
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.PREPARED,
        )

    def test_prepare_transaction_failure(self) -> Any:
        """Test that prepare_transaction aborts if any participant fails to prepare"""
        transaction_id = self.coordinator.create_transaction()
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True
        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = False
        participant2.commit.return_value = True
        participant2.abort.return_value = True
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)
        result = self.coordinator.prepare_transaction(transaction_id)
        self.assertFalse(result)
        participant1.prepare.assert_called_once_with(transaction_id)
        participant2.prepare.assert_called_once_with(transaction_id)
        participant1.abort.assert_called_once_with(transaction_id)
        participant2.abort.assert_called_once_with(transaction_id)
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.ABORTED,
        )

    def test_commit_transaction_success(self) -> Any:
        """Test that commit_transaction commits all participants"""
        transaction_id = self.coordinator.create_transaction()
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True
        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = True
        participant2.commit.return_value = True
        participant2.abort.return_value = True
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)
        self.coordinator.transactions[transaction_id][
            "status"
        ] = TransactionStatus.PREPARED
        result = self.coordinator.commit_transaction(transaction_id)
        self.assertTrue(result)
        participant1.commit.assert_called_once_with(transaction_id)
        participant2.commit.assert_called_once_with(transaction_id)
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.COMMITTED,
        )

    def test_commit_transaction_not_prepared(self) -> Any:
        """Test that commit_transaction fails if the transaction is not prepared"""
        transaction_id = self.coordinator.create_transaction()
        participant = Mock(spec=TransactionParticipant)
        participant.prepare.return_value = True
        participant.commit.return_value = True
        participant.abort.return_value = True
        self.coordinator.register_participant(transaction_id, participant)
        result = self.coordinator.commit_transaction(transaction_id)
        self.assertFalse(result)
        participant.commit.assert_not_called()
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.CREATED,
        )

    def test_abort_transaction(self) -> Any:
        """Test that abort_transaction aborts all participants"""
        transaction_id = self.coordinator.create_transaction()
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True
        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = True
        participant2.commit.return_value = True
        participant2.abort.return_value = True
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)
        result = self.coordinator.abort_transaction(transaction_id)
        self.assertTrue(result)
        participant1.abort.assert_called_once_with(transaction_id)
        participant2.abort.assert_called_once_with(transaction_id)
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.ABORTED,
        )

    def test_get_transaction_status(self) -> Any:
        """Test that get_transaction_status returns the correct status"""
        transaction_id = self.coordinator.create_transaction()
        status = self.coordinator.get_transaction_status(transaction_id)
        self.assertEqual(status, TransactionStatus.CREATED)
        self.coordinator.transactions[transaction_id][
            "status"
        ] = TransactionStatus.PREPARED
        status = self.coordinator.get_transaction_status(transaction_id)
        self.assertEqual(status, TransactionStatus.PREPARED)

    def test_get_transaction_status_invalid_id(self) -> Any:
        """Test that get_transaction_status returns None for invalid transaction ID"""
        status = self.coordinator.get_transaction_status("invalid_id")
        self.assertIsNone(status)

    def test_execute_transaction_success(self) -> Any:
        """Test that execute_transaction successfully executes a transaction"""
        transaction_id = self.coordinator.create_transaction()
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True
        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = True
        participant2.commit.return_value = True
        participant2.abort.return_value = True
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)
        result = self.coordinator.execute_transaction(transaction_id)
        self.assertTrue(result)
        participant1.prepare.assert_called_once_with(transaction_id)
        participant2.prepare.assert_called_once_with(transaction_id)
        participant1.commit.assert_called_once_with(transaction_id)
        participant2.commit.assert_called_once_with(transaction_id)
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.COMMITTED,
        )

    def test_execute_transaction_prepare_failure(self) -> Any:
        """Test that execute_transaction aborts if prepare fails"""
        transaction_id = self.coordinator.create_transaction()
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True
        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = False
        participant2.commit.return_value = True
        participant2.abort.return_value = True
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)
        result = self.coordinator.execute_transaction(transaction_id)
        self.assertFalse(result)
        participant1.prepare.assert_called_once_with(transaction_id)
        participant2.prepare.assert_called_once_with(transaction_id)
        participant1.abort.assert_called_once_with(transaction_id)
        participant2.abort.assert_called_once_with(transaction_id)
        participant1.commit.assert_not_called()
        participant2.commit.assert_not_called()
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.ABORTED,
        )


if __name__ == "__main__":
    unittest.main()
