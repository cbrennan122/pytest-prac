import os
import time
import json
from typing import Any, Dict, Optional
import requests


class APIError(Exception):
    """Generic API error."""


class AuthError(APIError):
    """Authentication/authorization error (401/403)."""


class ApiClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        session: Optional[requests.Session] = None,
        sleep_fn=time.sleep,  # injectable for testing
        max_retries: int = 2,
        backoff_seconds: float = 0.2,
    ):
        self.base_url = (base_url or os.environ.get("API_BASE_URL") or "").rstrip("/")
        if not self.base_url:
            raise ValueError("API_BASE_URL is required")

        self.api_key = api_key or os.environ.get("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY is required")

        self.timeout = timeout or float(os.environ.get("API_TIMEOUT", "5"))
        self.session = session or requests.Session()
        self.sleep_fn = sleep_fn
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, path: str, *, json_body: Any = None, params: Optional[Dict[str, Any]] = None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        attempt = 0
        last_exc = None

        while attempt <= self.max_retries:
            try:
                resp = self.session.request(
                    method=method.upper(),
                    url=url,
                    headers=self._headers(),
                    json=json_body,
                    params=params,
                    timeout=self.timeout,
                )
                # Auth errors
                if resp.status_code in (401, 403):
                    raise AuthError(f"{resp.status_code} {resp.text}")

                # Retry on typical transient 5xx
                if resp.status_code in (502, 503, 504):
                    attempt += 1
                    if attempt > self.max_retries:
                        raise APIError(f"Transient error after retries: {resp.status_code}")
                    self.sleep_fn(self.backoff_seconds * attempt)
                    continue

                # Non-2xx
                if not (200 <= resp.status_code < 300):
                    raise APIError(f"HTTP {resp.status_code}: {resp.text}")

                # Parse JSON safely
                if resp.content:
                    try:
                        return resp.json()
                    except json.JSONDecodeError:
                        raise APIError("Invalid JSON in response")
                return None

            except (requests.Timeout, requests.ConnectionError) as e:
                last_exc = e
                attempt += 1
                if attempt > self.max_retries:
                    raise APIError(f"Network error after retries: {e}") from e
                self.sleep_fn(self.backoff_seconds * attempt)

        raise APIError(f"Failed request: {last_exc}")

    def get(self, path: str, *, params: Optional[Dict[str, Any]] = None):
        return self._request("GET", path, params=params)

    def post(self, path: str, *, json_body: Any = None):
        return self._request("POST", path, json_body=json_body)
