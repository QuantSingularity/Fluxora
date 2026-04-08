"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError


class TestEnergyDataSchema:
    def test_valid_create(self):
        from app.schemas.data import EnergyDataCreate

        record = EnergyDataCreate(consumption_kwh=50.0)
        assert record.consumption_kwh == 50.0
        assert record.cost_usd is None

    def test_negative_consumption_rejected(self):
        from app.schemas.data import EnergyDataCreate

        with pytest.raises(ValidationError):
            EnergyDataCreate(consumption_kwh=-1.0)

    def test_zero_consumption_allowed(self):
        from app.schemas.data import EnergyDataCreate

        record = EnergyDataCreate(consumption_kwh=0.0)
        assert record.consumption_kwh == 0.0

    def test_negative_generation_rejected(self):
        from app.schemas.data import EnergyDataCreate

        with pytest.raises(ValidationError):
            EnergyDataCreate(consumption_kwh=10.0, generation_kwh=-1.0)

    def test_zero_generation_allowed(self):
        from app.schemas.data import EnergyDataCreate

        record = EnergyDataCreate(consumption_kwh=10.0, generation_kwh=0.0)
        assert record.generation_kwh == 0.0

    def test_negative_cost_rejected(self):
        from app.schemas.data import EnergyDataCreate

        with pytest.raises(ValidationError):
            EnergyDataCreate(consumption_kwh=10.0, cost_usd=-0.01)

    def test_humidity_out_of_range_high_rejected(self):
        from app.schemas.data import EnergyDataCreate

        with pytest.raises(ValidationError):
            EnergyDataCreate(consumption_kwh=10.0, humidity_percent=101.0)

    def test_humidity_out_of_range_low_rejected(self):
        from app.schemas.data import EnergyDataCreate

        with pytest.raises(ValidationError):
            EnergyDataCreate(consumption_kwh=10.0, humidity_percent=-1.0)

    def test_humidity_edge_values(self):
        from app.schemas.data import EnergyDataCreate

        r1 = EnergyDataCreate(consumption_kwh=10.0, humidity_percent=0.0)
        r2 = EnergyDataCreate(consumption_kwh=10.0, humidity_percent=100.0)
        assert r1.humidity_percent == 0.0
        assert r2.humidity_percent == 100.0

    def test_temperature_too_high_rejected(self):
        from app.schemas.data import EnergyDataCreate

        with pytest.raises(ValidationError):
            EnergyDataCreate(consumption_kwh=10.0, temperature_c=101.0)

    def test_temperature_too_low_rejected(self):
        from app.schemas.data import EnergyDataCreate

        with pytest.raises(ValidationError):
            EnergyDataCreate(consumption_kwh=10.0, temperature_c=-101.0)

    def test_temperature_edge_values_allowed(self):
        from app.schemas.data import EnergyDataCreate

        r1 = EnergyDataCreate(consumption_kwh=10.0, temperature_c=-100.0)
        r2 = EnergyDataCreate(consumption_kwh=10.0, temperature_c=100.0)
        assert r1.temperature_c == -100.0
        assert r2.temperature_c == 100.0

    def test_optional_fields_default_none(self):
        from app.schemas.data import EnergyDataCreate

        record = EnergyDataCreate(consumption_kwh=20.0)
        assert record.generation_kwh is None
        assert record.cost_usd is None
        assert record.temperature_c is None
        assert record.humidity_percent is None

    def test_update_all_optional(self):
        from app.schemas.data import EnergyDataUpdate

        update = EnergyDataUpdate()
        assert update.consumption_kwh is None
        assert update.cost_usd is None

    def test_update_partial_model_dump(self):
        from app.schemas.data import EnergyDataUpdate

        update = EnergyDataUpdate(consumption_kwh=99.0)
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {"consumption_kwh": 99.0}

    def test_update_negative_consumption_rejected(self):
        from app.schemas.data import EnergyDataUpdate

        with pytest.raises(ValidationError):
            EnergyDataUpdate(consumption_kwh=-5.0)


class TestUserSchema:
    def test_valid_user_create(self):
        from app.schemas.user import UserCreate

        user = UserCreate(email="test@example.com", password="secret123")
        assert user.email == "test@example.com"

    def test_invalid_email_rejected(self):
        from app.schemas.user import UserCreate

        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", password="secret123")

    def test_token_schema(self):
        from app.schemas.user import Token

        token = Token(access_token="abc", refresh_token="def", token_type="bearer")
        assert token.access_token == "abc"
        assert token.token_type == "bearer"

    def test_token_refresh_schema(self):
        from app.schemas.user import TokenRefresh

        tr = TokenRefresh(refresh_token="some_token")
        assert tr.refresh_token == "some_token"

    def test_token_data_optional_email(self):
        from app.schemas.user import TokenData

        td = TokenData()
        assert td.email is None
        td2 = TokenData(email="user@example.com")
        assert td2.email == "user@example.com"

    def test_user_update_all_optional(self):
        from app.schemas.user import UserUpdate

        update = UserUpdate()
        assert update.email is None
        assert update.password is None
        assert update.is_active is None

    def test_user_update_partial(self):
        from app.schemas.user import UserUpdate

        update = UserUpdate(is_active=False)
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {"is_active": False}
