# pytest: enable fixture injection
import json
import pytest
from pytest_mock import MockType, MockerFixture
import requests

from api_client import ApiClient, APIError, AuthError

@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "https://api.example.test")
    monkeypatch.setenv("API_KEY", "test_key")
    monkeypatch.setenv("API_TIMEOUT", "3")


@pytest.fixture
def fake_sleep(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture
def session(mocker: MockerFixture) -> MockType:
    return mocker.create_autospec(requests.Session, instance=True)


@pytest.fixture
def client(session, fake_sleep):
    return ApiClient(session=session, sleep_fn=fake_sleep, max_retries=2, backoff_seconds=0.01)

def make_response(mocker, status=200, json_data=None, text=""):
    resp = mocker.Mock()
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


def test_success_get_returns_json(client, session, mocker: MockerFixture):
    session.request.return_value = make_response(mocker, 200, json_data={"ok": True})

    data = client.get("/users")
    session.request.assert_called_once_with(
        method="GET",
        url="https://api.example.test/users",
        headers={"Authorization": "Bearer test_key", "Content-Type": "application/json", "Accept": "application/json"},
        json=None,
        params=None,
        timeout=3,
    )
    assert data == {"ok": True}


def test_auth_error_raises_autherror(client, session, mocker):
    session.request.return_value = make_response(mocker, 401, {"error": "Unauthorized"})
    with pytest.raises(AuthError) as exc_info:
        client.get("/me")
    assert "401" in str(exc_info.value)

def test_transient_503_retries_then_succeeds(client, session, fake_sleep, mocker):
    session.request.side_effect = [
        make_response(mocker, 503, json_data={"error": "Service Unavailable"}),
        make_response(mocker, 200, json_data={"ok": True}),
    ]

    data = client.get("/health")
    assert data == {"ok": True}
    assert session.request.call_count == 2
    fake_sleep.assert_called()
    calls = [c.args[0] for c in fake_sleep.call_args_list]
    assert calls[0] > 0


def test_network_timeout_retries_then_fails(client, session, fake_sleep):
    session.request.side_effect = [requests.Timeout() for _ in range(3)]

    with pytest.raises(APIError) as exc_info:
        client.get("/slow")
    assert "Network error after retries" in str(exc_info.value)
    assert session.request.call_count == 3
    assert fake_sleep.call_count == 2


def test_invalid_json_raises(client, session, mocker):
    bad = mocker.Mock()
    bad.status_code = 200
    bad.content = b"Not JSON"
    bad.text = "Not JSON"
    bad.json.side_effect = json.JSONDecodeError("x", "y", 0)
    session.request.return_value = bad

    with pytest.raises(APIError) as exc_info:
        client.get("/weird")
    assert "Invalid JSON in response" in str(exc_info.value)


def test_post_sends_body_and_headers(client, session, mocker):
    session.request.return_value = make_response(mocker, 201, json_data={"id": 123})
    payload = {"name": "Connor"}

    data = client.post("/users", json_body=payload)
    assert data["id"] == 123

    kwargs = session.request.call_args.kwargs
    assert kwargs["json"] == payload
    assert kwargs["headers"]["Authorization"] == ("Bearer test_key")
