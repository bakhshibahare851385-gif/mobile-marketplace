"""CORS tests for the Vite dev server origin."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PREFLIGHT_HEADERS = {
    "Origin": "http://localhost:5173",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type",
}


def test_preflight_allows_vite_origin():
    response = client.options("/api/v1/auth/register", headers=PREFLIGHT_HEADERS)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_preflight_rejects_unknown_origin():
    headers = dict(PREFLIGHT_HEADERS, Origin="http://evil.example")
    response = client.options("/api/v1/auth/register", headers=headers)

    assert "access-control-allow-origin" not in response.headers
