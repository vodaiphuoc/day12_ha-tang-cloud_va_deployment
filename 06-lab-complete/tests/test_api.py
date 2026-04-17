import time

import pytest
from fastapi.testclient import TestClient

import app.main as main


@pytest.fixture(autouse=True)
def reset_app_state(monkeypatch):
    """Reset in-memory globals so tests are isolated."""
    main._rate_windows.clear()
    main._daily_cost = 0.0
    main._cost_reset_day = time.strftime("%Y-%m-%d")
    main._request_count = 0
    main._error_count = 0

    # Keep tests deterministic and fast
    monkeypatch.setattr(main, "llm_ask", lambda question: f"mock answer: {question}")

    # Stable defaults for tests
    monkeypatch.setattr(main.settings, "agent_api_key", "test-api-key")
    monkeypatch.setattr(main.settings, "rate_limit_per_minute", 20)
    monkeypatch.setattr(main.settings, "daily_budget_usd", 5.0)


@pytest.fixture
def client():
    with TestClient(main.app) as test_client:
        yield test_client


def test_root_returns_app_info(client):
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert "endpoints" in data
    assert "ask" in data["endpoints"]


def test_health_returns_operational_status(client):
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data
    assert "checks" in data
    assert "timestamp" in data


def test_ready_returns_true_after_startup(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"ready": True}


def test_ask_requires_api_key(client):
    response = client.post("/ask", json={"question": "What is deployment?"})

    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]


def test_ask_rejects_invalid_api_key(client):
    response = client.post(
        "/ask",
        headers={"X-API-Key": "wrong-key"},
        json={"question": "What is deployment?"},
    )

    assert response.status_code == 401


def test_ask_returns_answer_when_authenticated(client):
    response = client.post(
        "/ask",
        headers={"X-API-Key": "test-api-key"},
        json={"question": "What is deployment?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is deployment?"
    assert data["answer"].startswith("mock answer:")
    assert data["model"] == main.settings.llm_model
    assert "timestamp" in data


def test_ask_validates_question_not_empty(client):
    response = client.post(
        "/ask",
        headers={"X-API-Key": "test-api-key"},
        json={"question": ""},
    )

    assert response.status_code == 422


def test_ask_validates_question_max_length(client):
    response = client.post(
        "/ask",
        headers={"X-API-Key": "test-api-key"},
        json={"question": "a" * 2001},
    )

    assert response.status_code == 422


def test_rate_limit_returns_429_when_exceeded(client, monkeypatch):
    monkeypatch.setattr(main.settings, "rate_limit_per_minute", 2)
    headers = {"X-API-Key": "test-api-key"}

    assert client.post("/ask", headers=headers, json={"question": "q1"}).status_code == 200
    assert client.post("/ask", headers=headers, json={"question": "q2"}).status_code == 200

    response = client.post("/ask", headers=headers, json={"question": "q3"})
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]
    assert response.headers.get("Retry-After") == "60"


def test_budget_guard_returns_503_when_daily_budget_exhausted(client):
    main._daily_cost = main.settings.daily_budget_usd

    response = client.post(
        "/ask",
        headers={"X-API-Key": "test-api-key"},
        json={"question": "hello"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Daily budget exhausted. Try tomorrow."


def test_metrics_requires_api_key(client):
    response = client.get("/metrics")
    assert response.status_code == 401


def test_metrics_returns_protected_stats(client):
    response = client.get("/metrics", headers={"X-API-Key": "test-api-key"})

    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "total_requests" in data
    assert "error_count" in data
    assert "daily_cost_usd" in data
    assert "daily_budget_usd" in data
    assert "budget_used_pct" in data


def test_security_headers_are_set(client):
    response = client.get("/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
