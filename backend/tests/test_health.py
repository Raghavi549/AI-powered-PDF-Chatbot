import logging
import socket

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.main import create_app

ORIGIN = "http://localhost:5173"
OTHER_ORIGIN = "http://evil.example"
# Distinctive throwaway value so accidental substring matches are impossible.
# Assembled at runtime so no key-like string exists in the source file (keeps
# secret scanners and "no key in tracked files" searches clean).
TEST_KEY = "".join(["Zq9v", "Xk2L", "mW8p", "R4tY"])


def make_client(key=None, origin=ORIGIN) -> TestClient:
    # _env_file=None keeps a developer's real backend/.env out of the tests.
    settings = Settings(_env_file=None, groq_api_key=key, frontend_origin=origin)
    return TestClient(create_app(settings))


# --- service-health -------------------------------------------------------

def test_health_with_key():
    response = make_client(key=TEST_KEY).get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "groq_configured": True}


def test_health_without_key():
    response = make_client(key=None).get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "groq_configured": False}


@pytest.mark.parametrize("blank", ["", "   ", "\t\n"])
def test_blank_key_counts_as_not_configured(blank):
    response = make_client(key=blank).get("/api/health")
    assert response.json()["groq_configured"] is False


def test_response_never_contains_key_or_long_fragments():
    response = make_client(key=TEST_KEY).get("/api/health")
    haystack = response.text + str(dict(response.headers))
    fragments = {TEST_KEY[i : i + 5] for i in range(len(TEST_KEY) - 4)}
    assert not any(fragment in haystack for fragment in fragments)


def test_key_not_in_logs_or_output(caplog, capsys):
    with caplog.at_level(logging.DEBUG):
        client = make_client(key=TEST_KEY)
        client.get("/api/health")
    captured = capsys.readouterr()
    assert TEST_KEY not in caplog.text
    assert TEST_KEY not in captured.out + captured.err


def test_key_not_exposed_by_settings_repr():
    settings = Settings(_env_file=None, groq_api_key=TEST_KEY)
    assert TEST_KEY not in repr(settings)
    assert TEST_KEY not in str(settings)


def test_health_makes_no_external_network_calls(monkeypatch):
    real_connect = socket.socket.connect

    def refuse_external(self, address, *args, **kwargs):
        # The event loop uses loopback sockets internally; only outside hosts matter.
        if isinstance(address, tuple) and address[0] not in ("127.0.0.1", "::1"):
            raise AssertionError(f"health endpoint tried to reach {address[0]}")
        return real_connect(self, address, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", refuse_external)
    response = make_client(key=TEST_KEY).get("/api/health")
    assert response.status_code == 200


def test_post_to_health_is_405():
    assert make_client().post("/api/health").status_code == 405


# --- local-security-baseline: CORS ----------------------------------------

def test_cors_allows_configured_origin():
    response = make_client().get("/api/health", headers={"Origin": ORIGIN})
    assert response.headers.get("access-control-allow-origin") == ORIGIN


def test_cors_denies_other_origin():
    response = make_client().get("/api/health", headers={"Origin": OTHER_ORIGIN})
    assert "access-control-allow-origin" not in response.headers


def test_cors_preflight_from_configured_origin():
    response = make_client().options(
        "/api/health",
        headers={"Origin": ORIGIN, "Access-Control-Request-Method": "GET"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == ORIGIN
    assert "GET" in response.headers.get("access-control-allow-methods", "")


def test_cors_preflight_from_other_origin_is_refused():
    response = make_client().options(
        "/api/health",
        headers={"Origin": OTHER_ORIGIN, "Access-Control-Request-Method": "GET"},
    )
    assert "access-control-allow-origin" not in response.headers


def test_custom_origin_is_honored_and_default_is_not():
    client = make_client(origin="http://localhost:4000")
    allowed = client.get("/api/health", headers={"Origin": "http://localhost:4000"})
    denied = client.get("/api/health", headers={"Origin": ORIGIN})
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:4000"
    assert "access-control-allow-origin" not in denied.headers


def test_trailing_slash_in_origin_is_normalized():
    client = make_client(origin=ORIGIN + "/")
    response = client.get("/api/health", headers={"Origin": ORIGIN})
    assert response.headers.get("access-control-allow-origin") == ORIGIN


def test_wildcard_origin_is_rejected_and_names_the_setting():
    with pytest.raises(ValidationError) as excinfo:
        Settings(_env_file=None, frontend_origin="*")
    assert "FRONTEND_ORIGIN" in str(excinfo.value)


def test_default_origin_is_vite_dev_server():
    assert Settings(_env_file=None).frontend_origin == ORIGIN
