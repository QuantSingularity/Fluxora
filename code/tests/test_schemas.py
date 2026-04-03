"""Tests for Pydantic schemas validation."""

import pytest
from pydantic import ValidationError


class TestEnergyDataSchema:
    def test_valid_create(self):
        from schemas.data import EnergyDataCreate

        record = EnergyDataCreate(consumption_kwh=50.0)
        assert record.consumption_kwh == 50.0
        assert record.cost_usd is None

    def test_negative_consumption_rejected(self):
        from schemas.data import EnergyDataCreate

        with pytest.raises(ValidationError):
            EnergyDataCreate(consumption_kwh=-1.0)

    def test_zero_consumption_allowed(self):
        from schemas.data import EnergyDataCreate

        record = EnergyDataCreate(consumption_kwh=0.0)
        assert record.consumption_kwh == 0.0

    def test_humidity_out_of_range_rejected(self):
        from schemas.data import EnergyDataCreate

        with pytest.raises(ValidationError):
            EnergyDataCreate(consumption_kwh=10.0, humidity_percent=101.0)

        with pytest.raises(ValidationError):
            EnergyDataCreate(consumption_kwh=10.0, humidity_percent=-1.0)

    def test_valid_humidity_edge_values(self):
        from schemas.data import EnergyDataCreate

        r1 = EnergyDataCreate(consumption_kwh=10.0, humidity_percent=0.0)
        r2 = EnergyDataCreate(consumption_kwh=10.0, humidity_percent=100.0)
        assert r1.humidity_percent == 0.0
        assert r2.humidity_percent == 100.0

    def test_optional_fields_default_to_none(self):
        from schemas.data import EnergyDataCreate

        record = EnergyDataCreate(consumption_kwh=20.0)
        assert record.generation_kwh is None
        assert record.cost_usd is None
        assert record.temperature_c is None
        assert record.humidity_percent is None

    def test_energy_data_update_all_optional(self):
        from schemas.data import EnergyDataUpdate

        update = EnergyDataUpdate()
        assert update.consumption_kwh is None
        assert update.cost_usd is None

    def test_energy_data_update_partial(self):
        from schemas.data import EnergyDataUpdate

        update = EnergyDataUpdate(consumption_kwh=99.0)
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {"consumption_kwh": 99.0}


class TestUserSchema:
    def test_valid_user_create(self):
        from schemas.user import UserCreate

        user = UserCreate(email="test@example.com", password="secret123")
        assert user.email == "test@example.com"

    def test_invalid_email_rejected(self):
        from schemas.user import UserCreate

        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", password="secret123")

    def test_token_schema_fields(self):
        from schemas.user import Token

        token = Token(access_token="abc", refresh_token="def", token_type="bearer")
        assert token.access_token == "abc"
        assert token.refresh_token == "def"
        assert token.token_type == "bearer"

    def test_token_refresh_schema(self):
        from schemas.user import TokenRefresh

        tr = TokenRefresh(refresh_token="some_token")
        assert tr.refresh_token == "some_token"

    def test_token_data_optional_email(self):
        from schemas.user import TokenData

        td = TokenData()
        assert td.email is None

        td2 = TokenData(email="user@example.com")
        assert td2.email == "user@example.com"
