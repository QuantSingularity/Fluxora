"""Integration tests for CRUD operations against the test database."""

from datetime import datetime

from app.core.security import get_password_hash
from app.crud.data import (
    count_data_records,
    create_data_record,
    delete_data_record,
    get_data_by_time_range,
    get_data_record,
    get_data_records,
    update_data_record,
)
from app.crud.user import (
    activate_user,
    create_user,
    deactivate_user,
    delete_user,
    get_user,
    get_user_by_email,
    get_users,
    update_user,
)
from app.models.data import EnergyData
from app.models.user import User
from app.schemas.data import EnergyDataCreate, EnergyDataUpdate
from app.schemas.user import UserCreate, UserUpdate

# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------


class TestUserCRUD:
    def test_create_user(self, db_session):
        user = create_user(
            db_session, UserCreate(email="a@example.com", password="pass1234")
        )
        assert user.id is not None
        assert user.email == "a@example.com"
        assert user.is_active is True
        assert user.is_superuser is False

    def test_get_user_by_id(self, db_session):
        user = create_user(
            db_session, UserCreate(email="b@example.com", password="pass1234")
        )
        fetched = get_user(db_session, user.id)
        assert fetched is not None
        assert fetched.email == "b@example.com"

    def test_get_user_by_email(self, db_session):
        create_user(db_session, UserCreate(email="c@example.com", password="pass1234"))
        fetched = get_user_by_email(db_session, "c@example.com")
        assert fetched is not None

    def test_get_nonexistent_user_returns_none(self, db_session):
        assert get_user(db_session, 99999) is None

    def test_get_nonexistent_email_returns_none(self, db_session):
        assert get_user_by_email(db_session, "nobody@example.com") is None

    def test_get_users_list(self, db_session):
        create_user(db_session, UserCreate(email="d@example.com", password="pass1234"))
        create_user(db_session, UserCreate(email="e@example.com", password="pass1234"))
        users = get_users(db_session)
        assert len(users) >= 2

    def test_update_user_email(self, db_session):
        user = create_user(
            db_session, UserCreate(email="f@example.com", password="pass1234")
        )
        updated = update_user(
            db_session, user.id, UserUpdate(email="updated@example.com")
        )
        assert updated is not None
        assert updated.email == "updated@example.com"

    def test_update_user_password(self, db_session):
        from app.core.security import verify_password

        user = create_user(
            db_session, UserCreate(email="g@example.com", password="oldpass123")
        )
        update_user(db_session, user.id, UserUpdate(password="newpass123"))
        refreshed = get_user(db_session, user.id)
        assert verify_password("newpass123", refreshed.hashed_password)

    def test_delete_user(self, db_session):
        user = create_user(
            db_session, UserCreate(email="h@example.com", password="pass1234")
        )
        result = delete_user(db_session, user.id)
        assert result is True
        assert get_user(db_session, user.id) is None

    def test_delete_nonexistent_user_returns_false(self, db_session):
        assert delete_user(db_session, 99999) is False

    def test_deactivate_user(self, db_session):
        user = create_user(
            db_session, UserCreate(email="i@example.com", password="pass1234")
        )
        deactivated = deactivate_user(db_session, user.id)
        assert deactivated is not None
        assert deactivated.is_active is False

    def test_activate_user(self, db_session):
        user = User(
            email="j@example.com",
            hashed_password=get_password_hash("pass1234"),
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()
        activated = activate_user(db_session, user.id)
        assert activated is not None
        assert activated.is_active is True

    def test_update_nonexistent_user_returns_none(self, db_session):
        result = update_user(db_session, 99999, UserUpdate(email="x@x.com"))
        assert result is None


# ---------------------------------------------------------------------------
# Data CRUD
# ---------------------------------------------------------------------------


class TestDataCRUD:
    def _make_user(self, db_session, email="owner@example.com"):
        user = User(
            email=email,
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_create_record(self, db_session):
        user = self._make_user(db_session)
        record = create_data_record(
            db_session,
            EnergyDataCreate(consumption_kwh=50.0, cost_usd=5.0),
            user_id=user.id,
        )
        assert record.id is not None
        assert record.consumption_kwh == 50.0
        assert record.user_id == user.id
        assert record.timestamp is not None

    def test_get_record(self, db_session):
        user = self._make_user(db_session, "r2@example.com")
        record = create_data_record(
            db_session, EnergyDataCreate(consumption_kwh=10.0), user_id=user.id
        )
        fetched = get_data_record(db_session, record.id, user.id)
        assert fetched is not None
        assert fetched.id == record.id

    def test_get_record_wrong_user_returns_none(self, db_session):
        user = self._make_user(db_session, "r3@example.com")
        record = create_data_record(
            db_session, EnergyDataCreate(consumption_kwh=10.0), user_id=user.id
        )
        assert get_data_record(db_session, record.id, user_id=99999) is None

    def test_get_records_list(self, db_session):
        user = self._make_user(db_session, "r4@example.com")
        for i in range(3):
            create_data_record(
                db_session, EnergyDataCreate(consumption_kwh=float(i)), user_id=user.id
            )
        records = get_data_records(db_session, user_id=user.id)
        assert len(records) == 3

    def test_get_records_pagination(self, db_session):
        user = self._make_user(db_session, "r5@example.com")
        for i in range(5):
            create_data_record(
                db_session, EnergyDataCreate(consumption_kwh=float(i)), user_id=user.id
            )
        records = get_data_records(db_session, user_id=user.id, skip=2, limit=2)
        assert len(records) == 2

    def test_update_record(self, db_session):
        user = self._make_user(db_session, "r6@example.com")
        record = create_data_record(
            db_session, EnergyDataCreate(consumption_kwh=10.0), user_id=user.id
        )
        updated = update_data_record(
            db_session, record.id, user.id, EnergyDataUpdate(consumption_kwh=99.0)
        )
        assert updated is not None
        assert updated.consumption_kwh == 99.0

    def test_update_nonexistent_record_returns_none(self, db_session):
        result = update_data_record(
            db_session, 99999, 1, EnergyDataUpdate(consumption_kwh=10.0)
        )
        assert result is None

    def test_delete_record(self, db_session):
        user = self._make_user(db_session, "r7@example.com")
        record = create_data_record(
            db_session, EnergyDataCreate(consumption_kwh=10.0), user_id=user.id
        )
        result = delete_data_record(db_session, record.id, user.id)
        assert result is True
        assert get_data_record(db_session, record.id, user.id) is None

    def test_delete_nonexistent_record_returns_false(self, db_session):
        assert delete_data_record(db_session, 99999, 1) is False

    def test_count_records(self, db_session):
        user = self._make_user(db_session, "r8@example.com")
        for _ in range(3):
            create_data_record(
                db_session, EnergyDataCreate(consumption_kwh=1.0), user_id=user.id
            )
        assert count_data_records(db_session, user_id=user.id) == 3

    def test_get_by_time_range(self, db_session):
        user = self._make_user(db_session, "r9@example.com")
        record = EnergyData(
            user_id=user.id,
            consumption_kwh=42.0,
            timestamp=datetime(2024, 6, 15, 12, 0, 0),
        )
        db_session.add(record)
        db_session.commit()

        results = get_data_by_time_range(
            db_session,
            user_id=user.id,
            start_time=datetime(2024, 6, 1),
            end_time=datetime(2024, 6, 30),
        )
        assert len(results) == 1
        assert results[0].consumption_kwh == 42.0

    def test_get_by_time_range_no_results(self, db_session):
        user = self._make_user(db_session, "r10@example.com")
        results = get_data_by_time_range(
            db_session,
            user_id=user.id,
            start_time=datetime(2000, 1, 1),
            end_time=datetime(2000, 1, 2),
        )
        assert results == []
