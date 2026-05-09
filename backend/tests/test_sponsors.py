import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.sponsor_lead import SponsorLead
from app.models.sponsor_package import SponsorPackage
from app.repositories.sponsor_repository import SponsorRepository
from app.schemas.sponsor import SponsorLeadCreateRequest
from app.services.sponsor_service import SponsorService


def _build_test_client() -> tuple[TestClient, sessionmaker[Session], Engine, str]:
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), testing_session_local, engine, db_path


def _build_db_session() -> tuple[sessionmaker[Session], Engine, str]:
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    Base.metadata.create_all(bind=engine)
    return testing_session_local, engine, db_path


# ---------------------------------------------------------------------------
# API-level tests: GET /api/v1/sponsors/packages
# ---------------------------------------------------------------------------


def test_get_sponsor_packages_returns_active_only() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            db.add(SponsorPackage(name="Bronze", slug="bronze", monthly_request_limit=1000, is_active=True))
            db.add(SponsorPackage(name="Hidden", slug="hidden", monthly_request_limit=1000, is_active=False))
            db.commit()

        response = client.get("/api/v1/sponsors/packages")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 1
        assert payload[0]["slug"] == "bronze"
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_get_sponsor_packages_returns_empty_list_when_no_active_packages() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            db.add(SponsorPackage(name="Inactive", slug="inactive", monthly_request_limit=5000, is_active=False))
            db.commit()

        response = client.get("/api/v1/sponsors/packages")
        assert response.status_code == 200
        assert response.json() == []
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_get_sponsor_packages_returns_empty_list_when_no_packages_exist() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.get("/api/v1/sponsors/packages")
        assert response.status_code == 200
        assert response.json() == []
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_get_sponsor_packages_ordered_by_monthly_request_limit_ascending() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            db.add(SponsorPackage(name="Gold", slug="gold", monthly_request_limit=100000, is_active=True))
            db.add(SponsorPackage(name="Bronze", slug="bronze", monthly_request_limit=5000, is_active=True))
            db.add(SponsorPackage(name="Silver", slug="silver", monthly_request_limit=25000, is_active=True))
            db.commit()

        response = client.get("/api/v1/sponsors/packages")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 3
        limits = [item["monthly_request_limit"] for item in payload]
        assert limits == sorted(limits)
        assert payload[0]["slug"] == "bronze"
        assert payload[1]["slug"] == "silver"
        assert payload[2]["slug"] == "gold"
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_get_sponsor_packages_response_has_all_required_fields() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            db.add(
                SponsorPackage(
                    name="Bronze",
                    slug="bronze",
                    monthly_request_limit=5000,
                    price_label="Starter sponsorship",
                    description="Help local communities.",
                    is_active=True,
                )
            )
            db.commit()

        response = client.get("/api/v1/sponsors/packages")
        assert response.status_code == 200
        item = response.json()[0]

        assert "id" in item
        assert "name" in item
        assert "slug" in item
        assert "monthly_request_limit" in item
        assert "price_label" in item
        assert "description" in item
        assert "is_active" in item
        assert "created_at" in item
        assert "updated_at" in item

        assert item["name"] == "Bronze"
        assert item["slug"] == "bronze"
        assert item["monthly_request_limit"] == 5000
        assert item["price_label"] == "Starter sponsorship"
        assert item["description"] == "Help local communities."
        assert item["is_active"] is True
        # id should be a valid UUID
        uuid.UUID(item["id"])
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_get_sponsor_packages_optional_fields_can_be_null() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            db.add(
                SponsorPackage(
                    name="Basic",
                    slug="basic",
                    monthly_request_limit=1000,
                    price_label=None,
                    description=None,
                    is_active=True,
                )
            )
            db.commit()

        response = client.get("/api/v1/sponsors/packages")
        assert response.status_code == 200
        item = response.json()[0]
        assert item["price_label"] is None
        assert item["description"] is None
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_get_sponsor_packages_inactive_not_included_when_mixed() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        with testing_session_local() as db:
            db.add(SponsorPackage(name="Active A", slug="active-a", monthly_request_limit=1000, is_active=True))
            db.add(SponsorPackage(name="Inactive B", slug="inactive-b", monthly_request_limit=500, is_active=False))
            db.add(SponsorPackage(name="Active C", slug="active-c", monthly_request_limit=2000, is_active=True))
            db.add(SponsorPackage(name="Inactive D", slug="inactive-d", monthly_request_limit=3000, is_active=False))
            db.commit()

        response = client.get("/api/v1/sponsors/packages")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 2
        slugs = {item["slug"] for item in payload}
        assert slugs == {"active-a", "active-c"}
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


# ---------------------------------------------------------------------------
# API-level tests: POST /api/v1/sponsors/leads
# ---------------------------------------------------------------------------


def test_post_sponsor_lead_creates_record() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Kathmandu Tech Initiative",
                "contact_name": "Asha Rana",
                "email": "asha@example.com",
                "message": "Interested in district-level partnership",
            },
        )
        assert response.status_code == 201
        payload = response.json()
        assert payload["message"] == "Sponsor interest submitted successfully"
        assert payload["id"]
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_validation_error() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "X",
                "contact_name": "",
                "email": "bad-email",
            },
        )
        assert response.status_code == 422
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_with_all_optional_fields() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Nepal Education Foundation",
                "contact_name": "Ram Bahadur",
                "email": "ram@nef.org",
                "phone": "+977-9800000001",
                "sponsor_type": "district program",
                "budget_range": "5k-10k USD",
                "target_group": "public schools in Kathmandu",
                "message": "We want to sponsor the Silver package for our district.",
            },
        )
        assert response.status_code == 201
        payload = response.json()
        assert payload["message"] == "Sponsor interest submitted successfully"
        # Verify persisted to DB
        with testing_session_local() as db:
            lead = db.scalar(select(SponsorLead).where(SponsorLead.email == "ram@nef.org"))
            assert lead is not None
            assert lead.phone == "+977-9800000001"
            assert lead.sponsor_type == "district program"
            assert lead.budget_range == "5k-10k USD"
            assert lead.target_group == "public schools in Kathmandu"
            assert lead.message == "We want to sponsor the Silver package for our district."
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_response_id_is_valid_uuid() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Tech Org",
                "contact_name": "Jane Doe",
                "email": "jane@techorg.io",
            },
        )
        assert response.status_code == 201
        returned_id = response.json()["id"]
        parsed = uuid.UUID(returned_id)
        assert str(parsed) == returned_id
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_missing_required_fields_returns_422() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        # Missing organization_name, contact_name, and email
        response = client.post("/api/v1/sponsors/leads", json={})
        assert response.status_code == 422
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_missing_email_returns_422() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Valid Org",
                "contact_name": "Valid Contact",
            },
        )
        assert response.status_code == 422
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_organization_name_too_short_returns_422() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "X",
                "contact_name": "Valid Name",
                "email": "valid@example.com",
            },
        )
        assert response.status_code == 422
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_contact_name_too_short_returns_422() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Valid Organization",
                "contact_name": "J",
                "email": "valid@example.com",
            },
        )
        assert response.status_code == 422
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_email_with_no_at_symbol_returns_422() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Valid Organization",
                "contact_name": "Valid Contact",
                "email": "notanemail",
            },
        )
        assert response.status_code == 422
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_email_leading_at_returns_422() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Valid Organization",
                "contact_name": "Valid Contact",
                "email": "@domain.com",
            },
        )
        assert response.status_code == 422
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_email_trailing_at_returns_422() -> None:
    client, _, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Valid Organization",
                "contact_name": "Valid Contact",
                "email": "user@",
            },
        )
        assert response.status_code == 422
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_strips_whitespace_from_names() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "  Padded Org Name  ",
                "contact_name": "  Padded Contact  ",
                "email": "contact@padded.org",
            },
        )
        assert response.status_code == 201

        with testing_session_local() as db:
            lead = db.scalar(select(SponsorLead).where(SponsorLead.email == "contact@padded.org"))
            assert lead is not None
            assert lead.organization_name == "Padded Org Name"
            assert lead.contact_name == "Padded Contact"
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_status_defaults_to_new() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Status Test Org",
                "contact_name": "Status Test Contact",
                "email": "status@test.org",
            },
        )
        assert response.status_code == 201

        with testing_session_local() as db:
            lead = db.scalar(select(SponsorLead).where(SponsorLead.email == "status@test.org"))
            assert lead is not None
            assert lead.status == "new"
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_optional_fields_default_to_none_in_db() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Minimal Org",
                "contact_name": "Minimal Contact",
                "email": "minimal@example.com",
            },
        )
        assert response.status_code == 201

        with testing_session_local() as db:
            lead = db.scalar(select(SponsorLead).where(SponsorLead.email == "minimal@example.com"))
            assert lead is not None
            assert lead.phone is None
            assert lead.sponsor_type is None
            assert lead.budget_range is None
            assert lead.target_group is None
            assert lead.message is None
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_email_normalized_by_stripping_whitespace() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        response = client.post(
            "/api/v1/sponsors/leads",
            json={
                "organization_name": "Email Strip Org",
                "contact_name": "Email Strip Contact",
                "email": "  trimmed@example.com  ",
            },
        )
        assert response.status_code == 201

        with testing_session_local() as db:
            lead = db.scalar(select(SponsorLead).where(SponsorLead.email == "trimmed@example.com"))
            assert lead is not None
            assert lead.email == "trimmed@example.com"
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_post_sponsor_lead_multiple_submissions_create_separate_records() -> None:
    client, testing_session_local, engine, db_path = _build_test_client()

    try:
        for i in range(3):
            response = client.post(
                "/api/v1/sponsors/leads",
                json={
                    "organization_name": f"Org {i}",
                    "contact_name": f"Contact {i}",
                    "email": f"contact{i}@example.com",
                },
            )
            assert response.status_code == 201

        with testing_session_local() as db:
            count = db.query(SponsorLead).count()
            assert count == 3
    finally:
        client.close()
        engine.dispose()
        app.dependency_overrides.clear()
        if os.path.exists(db_path):
            os.remove(db_path)


# ---------------------------------------------------------------------------
# Schema-level tests: SponsorLeadCreateRequest (pure Pydantic, no DB)
# ---------------------------------------------------------------------------


def test_schema_valid_email_is_accepted() -> None:
    req = SponsorLeadCreateRequest(
        organization_name="Valid Org",
        contact_name="Valid Contact",
        email="user@example.com",
    )
    assert req.email == "user@example.com"


def test_schema_email_with_leading_whitespace_is_stripped() -> None:
    req = SponsorLeadCreateRequest(
        organization_name="Valid Org",
        contact_name="Valid Contact",
        email="  user@example.com  ",
    )
    assert req.email == "user@example.com"


def test_schema_email_without_at_symbol_raises_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SponsorLeadCreateRequest(
            organization_name="Valid Org",
            contact_name="Valid Contact",
            email="notanemail",
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("email",) for e in errors)


def test_schema_email_with_leading_at_raises_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SponsorLeadCreateRequest(
            organization_name="Valid Org",
            contact_name="Valid Contact",
            email="@domain.com",
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("email",) for e in errors)


def test_schema_email_with_trailing_at_raises_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SponsorLeadCreateRequest(
            organization_name="Valid Org",
            contact_name="Valid Contact",
            email="user@",
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("email",) for e in errors)


def test_schema_email_too_short_raises_validation_error() -> None:
    # min_length=5; "a@bc" is 4 chars
    with pytest.raises(ValidationError) as exc_info:
        SponsorLeadCreateRequest(
            organization_name="Valid Org",
            contact_name="Valid Contact",
            email="a@bc",
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("email",) for e in errors)


def test_schema_email_at_minimum_length_is_accepted() -> None:
    # "a@b.c" is 5 chars — meets min_length=5 and passes validator
    req = SponsorLeadCreateRequest(
        organization_name="Valid Org",
        contact_name="Valid Contact",
        email="a@b.c",
    )
    assert req.email == "a@b.c"


def test_schema_organization_name_single_char_raises_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SponsorLeadCreateRequest(
            organization_name="X",
            contact_name="Valid Contact",
            email="valid@example.com",
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("organization_name",) for e in errors)


def test_schema_organization_name_min_length_two_chars_is_accepted() -> None:
    req = SponsorLeadCreateRequest(
        organization_name="XY",
        contact_name="Valid Contact",
        email="valid@example.com",
    )
    assert req.organization_name == "XY"


def test_schema_contact_name_single_char_raises_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SponsorLeadCreateRequest(
            organization_name="Valid Org",
            contact_name="J",
            email="valid@example.com",
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("contact_name",) for e in errors)


def test_schema_contact_name_min_length_two_chars_is_accepted() -> None:
    req = SponsorLeadCreateRequest(
        organization_name="Valid Org",
        contact_name="Jo",
        email="valid@example.com",
    )
    assert req.contact_name == "Jo"


def test_schema_optional_fields_default_to_none() -> None:
    req = SponsorLeadCreateRequest(
        organization_name="Valid Org",
        contact_name="Valid Contact",
        email="valid@example.com",
    )
    assert req.phone is None
    assert req.sponsor_type is None
    assert req.budget_range is None
    assert req.target_group is None
    assert req.message is None


def test_schema_all_optional_fields_accepted() -> None:
    req = SponsorLeadCreateRequest(
        organization_name="Full Org",
        contact_name="Full Contact",
        email="full@example.com",
        phone="+977-9800000000",
        sponsor_type="district",
        budget_range="10k-20k",
        target_group="rural schools",
        message="Interested in gold package",
    )
    assert req.phone == "+977-9800000000"
    assert req.sponsor_type == "district"
    assert req.budget_range == "10k-20k"
    assert req.target_group == "rural schools"
    assert req.message == "Interested in gold package"


def test_schema_message_max_length_enforced() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SponsorLeadCreateRequest(
            organization_name="Valid Org",
            contact_name="Valid Contact",
            email="valid@example.com",
            message="x" * 3001,
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("message",) for e in errors)


def test_schema_message_at_max_length_is_accepted() -> None:
    req = SponsorLeadCreateRequest(
        organization_name="Valid Org",
        contact_name="Valid Contact",
        email="valid@example.com",
        message="x" * 3000,
    )
    assert len(req.message) == 3000  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Repository-level tests: SponsorRepository
# ---------------------------------------------------------------------------


def test_repository_list_active_packages_filters_inactive() -> None:
    session_factory, engine, db_path = _build_db_session()

    try:
        with session_factory() as db:
            db.add(SponsorPackage(name="Active", slug="active", monthly_request_limit=5000, is_active=True))
            db.add(SponsorPackage(name="Inactive", slug="inactive", monthly_request_limit=5000, is_active=False))
            db.commit()

        with session_factory() as db:
            repo = SponsorRepository(db)
            packages = repo.list_active_packages()
            assert len(packages) == 1
            assert packages[0].slug == "active"
    finally:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_repository_list_active_packages_ordered_by_monthly_request_limit_asc() -> None:
    session_factory, engine, db_path = _build_db_session()

    try:
        with session_factory() as db:
            db.add(SponsorPackage(name="Gold", slug="gold", monthly_request_limit=100000, is_active=True))
            db.add(SponsorPackage(name="Bronze", slug="bronze", monthly_request_limit=5000, is_active=True))
            db.add(SponsorPackage(name="Silver", slug="silver", monthly_request_limit=25000, is_active=True))
            db.commit()

        with session_factory() as db:
            repo = SponsorRepository(db)
            packages = repo.list_active_packages()
            limits = [p.monthly_request_limit for p in packages]
            assert limits == sorted(limits)
            assert packages[0].slug == "bronze"
    finally:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_repository_list_active_packages_returns_empty_when_none_active() -> None:
    session_factory, engine, db_path = _build_db_session()

    try:
        with session_factory() as db:
            repo = SponsorRepository(db)
            packages = repo.list_active_packages()
            assert packages == []
    finally:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_repository_create_lead_persists_and_returns_with_id() -> None:
    session_factory, engine, db_path = _build_db_session()

    try:
        with session_factory() as db:
            repo = SponsorRepository(db)
            lead = SponsorLead(
                organization_name="Test Org",
                contact_name="Test Contact",
                email="test@example.com",
                status="new",
            )
            result = repo.create_lead(lead)
            assert result.id is not None
            assert isinstance(result.id, uuid.UUID)
            assert result.organization_name == "Test Org"
            assert result.email == "test@example.com"

        with session_factory() as db:
            persisted = db.scalar(select(SponsorLead).where(SponsorLead.email == "test@example.com"))
            assert persisted is not None
            assert persisted.organization_name == "Test Org"
    finally:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_repository_create_lead_with_all_optional_fields() -> None:
    session_factory, engine, db_path = _build_db_session()

    try:
        with session_factory() as db:
            repo = SponsorRepository(db)
            lead = SponsorLead(
                organization_name="Full Org",
                contact_name="Full Contact",
                email="full@example.com",
                phone="+1-555-0000",
                sponsor_type="corporate",
                budget_range="20k-50k",
                target_group="university students",
                message="Looking for a multi-year partnership.",
                status="new",
            )
            result = repo.create_lead(lead)
            assert result.phone == "+1-555-0000"
            assert result.sponsor_type == "corporate"
            assert result.budget_range == "20k-50k"
            assert result.target_group == "university students"
            assert result.message == "Looking for a multi-year partnership."
    finally:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)


# ---------------------------------------------------------------------------
# Service-level tests: SponsorService
# ---------------------------------------------------------------------------


def test_service_get_active_packages_delegates_to_repository() -> None:
    session_factory, engine, db_path = _build_db_session()

    try:
        with session_factory() as db:
            db.add(SponsorPackage(name="Bronze", slug="bronze", monthly_request_limit=5000, is_active=True))
            db.add(SponsorPackage(name="Archived", slug="archived", monthly_request_limit=1000, is_active=False))
            db.commit()

        with session_factory() as db:
            service = SponsorService(db)
            packages = service.get_active_packages()
            assert len(packages) == 1
            assert packages[0].slug == "bronze"
    finally:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_service_create_lead_strips_whitespace_from_org_and_contact_name() -> None:
    session_factory, engine, db_path = _build_db_session()

    try:
        with session_factory() as db:
            service = SponsorService(db)
            payload = SponsorLeadCreateRequest(
                organization_name="  Spaced Org  ",
                contact_name="  Spaced Contact  ",
                email="spaced@example.com",
            )
            result = service.create_lead(payload)
            assert result.organization_name == "Spaced Org"
            assert result.contact_name == "Spaced Contact"
    finally:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_service_create_lead_sets_status_to_new() -> None:
    session_factory, engine, db_path = _build_db_session()

    try:
        with session_factory() as db:
            service = SponsorService(db)
            payload = SponsorLeadCreateRequest(
                organization_name="Status Org",
                contact_name="Status Contact",
                email="status@example.com",
            )
            result = service.create_lead(payload)
            assert result.status == "new"
    finally:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_service_create_lead_passes_optional_fields_through() -> None:
    session_factory, engine, db_path = _build_db_session()

    try:
        with session_factory() as db:
            service = SponsorService(db)
            payload = SponsorLeadCreateRequest(
                organization_name="Options Org",
                contact_name="Options Contact",
                email="options@example.com",
                phone="+977-0000000",
                sponsor_type="ngo",
                budget_range="1k-5k",
                target_group="rural communities",
                message="NGO sponsorship enquiry",
            )
            result = service.create_lead(payload)
            assert result.phone == "+977-0000000"
            assert result.sponsor_type == "ngo"
            assert result.budget_range == "1k-5k"
            assert result.target_group == "rural communities"
            assert result.message == "NGO sponsorship enquiry"
    finally:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_service_create_lead_stores_normalized_email() -> None:
    session_factory, engine, db_path = _build_db_session()

    try:
        with session_factory() as db:
            service = SponsorService(db)
            # Email is pre-normalized by the schema validator (strip)
            payload = SponsorLeadCreateRequest(
                organization_name="Email Org",
                contact_name="Email Contact",
                email="  email@example.com  ",
            )
            result = service.create_lead(payload)
            assert result.email == "email@example.com"
    finally:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_service_create_lead_none_optional_fields_stored_as_none() -> None:
    session_factory, engine, db_path = _build_db_session()

    try:
        with session_factory() as db:
            service = SponsorService(db)
            payload = SponsorLeadCreateRequest(
                organization_name="Minimal Org",
                contact_name="Minimal Contact",
                email="minimal@example.com",
            )
            result = service.create_lead(payload)
            assert result.phone is None
            assert result.sponsor_type is None
            assert result.budget_range is None
            assert result.target_group is None
            assert result.message is None
    finally:
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)
