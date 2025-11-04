# tests/test_api_client_unittest_mock.py
import json
import pytest
import requests
from unittest.mock import Mock, MagicMock, create_autospec

from api_client import ApiClient, APIError, AuthError


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "https://api.example.test")
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("API_TIMEOUT", "3")


@pytest.fixture
def fake_sleep():
    """MagicMock in place of time.sleep."""
    return MagicMock()


@pytest.fixture
def session():
    """Mocked requests.Session without pytest-mock."""
    return create_autospec(requests.Session, instance=True)


@pytest.fixture
def client(session, fake_sleep):
    return ApiClient(session=session, sleep_fn=fake_sleep, max_retries=2, backoff_seconds=0.01)


def make_response(status=200, json_data=None, text=""):
    """Helper to build a fake Response-like object using unittest.mock."""
    resp = Mock()
    resp.status_code = status
    if json_data is not None:
        resp.json.return_value = json_data
        resp.content = b"{}"
        resp.text = json.dumps(json_data)
    else:
        resp.json.side_effect = json.JSONDecodeError("x", "y", 0)
        resp.content = text.encode()
        resp.text = text
    return resp


def test_success_get_returns_json(client, session):
    session.request.return_value = make_response(200, {"ok": True})

    data = client.get("/users")

    session.request.assert_called_once_with(
        method="GET",
        url="https://api.example.test/users",
        headers={
            "Authorization": "Bearer test-key",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json=None,
        params=None,
        timeout=3.0,
    )
    assert data == {"ok": True}


def test_auth_error_raises_autherror(client, session):
    session.request.side_effect = [make_response(401, {"error": "nope"})]
    with pytest.raises(AuthError) as ei:
        client.get("/me")
    assert "401" in str(ei.value)


def test_transient_503_retries_then_succeeds(client, session, fake_sleep):
    session.request.side_effect = [
        make_response(503, json_data={"error": "Service Unavailable"}),
        make_response(200, json_data={"ok": True}),
    ]

    data = client.get("/health")
    assert data == {"ok": True}
    assert session.request.call_count == 2
    fake_sleep.assert_called()
    calls = [c.args[0] for c in fake_sleep.call_args_list]
    assert calls[0] > 0


def test_network_timeout_retries_then_fails(client, session, fake_sleep):
    session.request.side_effect = [requests.Timeout() for _ in range(3)]

    with pytest.raises(APIError) as ei:
        client.get("/slow")

    assert "Network error after retries" in str(ei.value)
    assert session.request.call_count == 3
    assert fake_sleep.call_count == 2


def test_invalid_json_raises(client, session):
    bad = Mock()
    bad.status_code = 200
    bad.content = b"not-json"
    bad.text = "not-json"
    bad.json.side_effect = json.JSONDecodeError("x", "y", 0)
    session.request.return_value = bad

    with pytest.raises(APIError) as ei:
        client.get("/weird")
    assert "Invalid JSON" in str(ei.value)


def test_post_sends_body_and_headers(client, session):
    session.request.return_value = make_response(201, {"id": 123})
    payload = {"name": "Connor"}

    out = client.post("/users", json_body=payload)
    assert out["id"] == 123

    kwargs = session.request.call_args.kwargs
    assert kwargs["json"] == payload
    assert kwargs["headers"]["Authorization"].startswith("Bearer ")


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "https://alt.test")
    monkeypatch.setenv("API_KEY", "alt-key")
    c = ApiClient(sleep_fn=lambda *_: None)

    c.session = create_autospec(requests.Session, instance=True)
    c.session.request.return_value = make_response(200, {"ok": True})

    c.get("/ping")
    _, kwargs = c.session.request.call_args
    assert kwargs["url"] == "https://alt.test/ping"
    assert kwargs["headers"]["Authorization"] == "Bearer alt-key"
