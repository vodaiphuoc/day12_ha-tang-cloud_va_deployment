from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure imports work when pytest is run from repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import main  # noqa: E402


@pytest.fixture(autouse=True)
def reset_app_state() -> None:
    """Reset mutable globals/settings to keep tests independent."""
    main._rate_windows.clear()
    main._daily_cost = 0.0
    main._cost_reset_day = time.strftime("%Y-%m-%d")
    main._request_count = 0
    main._error_count = 0
    main._is_ready = False

    main.settings.agent_api_key = "test-api-key"
    main.settings.rate_limit_per_minute = 2
    main.settings.daily_budget_usd = 5.0


@pytest.fixture()
def client() -> TestClient:
    with TestClient(main.app) as test_client:
        yield test_client


def test_root_returns_basic_app_info(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["app"] == main.settings.app_name
    assert payload["version"] == main.settings.app_version
    assert "ask" in payload["endpoints"]


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["environment"] == main.settings.environment
    assert payload["checks"]["llm"] in {"mock", "openai"}


def test_ready_returns_true_after_startup(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"ready": True}


def test_ask_requires_api_key(client: TestClient) -> None:
    response = client.post("/ask", json={"question": "What is deployment?"})

    assert response.status_code == 401
    assert "API key" in response.json()["detail"]


def test_ask_validates_body(client: TestClient) -> None:
    response = client.post(
        "/ask",
        headers={"X-API-Key": main.settings.agent_api_key},
        json={"question": ""},
    )

    assert response.status_code == 422


def test_ask_success_returns_response_model_fields(client: TestClient) -> None:
    question = "What is deployment?"
    response = client.post(
        "/ask",
        headers={"X-API-Key": main.settings.agent_api_key},
        json={"question": question},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["question"] == question
    assert isinstance(payload["answer"], str) and payload["answer"]
    assert payload["model"] == main.settings.llm_model
    assert isinstance(payload["timestamp"], str) and payload["timestamp"]


def test_ask_enforces_rate_limit(client: TestClient) -> None:
    headers = {"X-API-Key": main.settings.agent_api_key}
    body = {"question": "rate limit test"}

    first = client.post("/ask", headers=headers, json=body)
    second = client.post("/ask", headers=headers, json=body)
    third = client.post("/ask", headers=headers, json=body)

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert "Rate limit exceeded" in third.json()["detail"]
    assert third.headers["Retry-After"] == "60"


def test_ask_blocks_when_daily_budget_exhausted(client: TestClient) -> None:
    main.settings.daily_budget_usd = 0.0001
    main._daily_cost = main.settings.daily_budget_usd

    response = client.post(
        "/ask",
        headers={"X-API-Key": main.settings.agent_api_key},
        json={"question": "Can you answer this?"},
    )

    assert response.status_code == 503
    assert "Daily budget exhausted" in response.json()["detail"]


def test_metrics_requires_api_key(client: TestClient) -> None:
    response = client.get("/metrics")

    assert response.status_code == 401


def test_metrics_returns_basic_numbers_when_authenticated(client: TestClient) -> None:
    response = client.get("/metrics", headers={"X-API-Key": main.settings.agent_api_key})

    assert response.status_code == 200
    payload = response.json()
    assert "uptime_seconds" in payload
    assert "total_requests" in payload
    assert "error_count" in payload
    assert "daily_cost_usd" in payload
    assert "budget_used_pct" in payload


def test_security_headers_are_present(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
