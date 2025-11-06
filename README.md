# pytest-prac

A small example repository demonstrating pytest best-practices and test patterns.

This project contains two tiny example modules in `src/` and a comprehensive test
suite in `tests/` that exercises fixtures, parametrization, mocking (both
`pytest-mock` and `unittest.mock` styles), and CI-friendly test reporting.

Highlights
- Small, focused production code in `src/`:
	- `src/math_ops.py` — simple arithmetic helpers used in unit tests.
	- `src/api_client.py` — an HTTP client wrapper that demonstrates retries,
		error handling, and dependency injection for testability.
- Tests in `tests/` show modern pytest patterns: fixtures, parametrized tests,
	and both `pytest-mock` and `unittest.mock` approaches.
- `tools/ci_run.py` — small helper to run pytest with coverage and HTML/JUnit
	reports for CI pipelines.

Table of contents
- Features
- Requirements
- Installation
- Running tests
- Examples
- Contributing
- License

## Features

- Example unit tests covering happy-paths and edge-cases.
- Demonstrates mocking external dependencies (requests.Session).
- Produces JUnit and HTML reports (configured in `pytest.ini`) and includes a
	simple CI helper script.

## Requirements

- Python 3.10+ (typing features like `X | Y` are used in `tools/ci_run.py`).
- See `requirements.txt` and `requirements-dev.txt` for runtime and dev deps.

## Installation

Create a virtual environment and install development requirements:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

If you only need the runtime deps (not test tooling) use:

```bash
python -m pip install -r requirements.txt
```

## Running tests

Run the full test suite with pytest (the repository includes `pytest.ini` which
generates `reports/junit.xml` and `reports/report.html` automatically):

```bash
python -m pytest
```

A CI-oriented runner that also produces coverage XML is available:

```bash
python tools/ci_run.py --report-dir reports
```

Generated reports will be placed in the `reports/` directory.

### Notes about pytest config

The project `pytest.ini` sets `pythonpath = src` so tests can import modules
from `src` directly (e.g. `from math_ops import add`). Adjust if you prefer
package-style imports.

## Examples

Quick example using `math_ops`:

```python
from math_ops import add, divide

print(add(2, 3))      # -> 5
print(divide(10, 2))  # -> 5.0
```

Using `ApiClient` (the client reads `API_BASE_URL` and `API_KEY` from the
environment by default):

```python
import os
from api_client import ApiClient

os.environ["API_BASE_URL"] = "https://api.example.test"
os.environ["API_KEY"] = "mykey"

client = ApiClient()
resp = client.get('/health')
print(resp)
```

For testability, `ApiClient` accepts a `session` (requests.Session-like), a
`sleep_fn` for backoff, and configuration overrides so tests can inject mocks.

## Contributing

Contributions are welcome. Keep changes small and focused. Tests should be
added for new behavior and CI should pass before merging.

Recommended workflow:

1. Create a branch for your change.
2. Add or update tests under `tests/`.
3. Run `python -m pytest` locally and ensure tests and linters (if any) pass.
4. Open a PR describing the change.

## License

This repository includes a `LICENSE` file at the project root. Please refer to
that file for licensing details.

## Files of interest

- `src/` — small example modules (`math_ops.py`, `api_client.py`).
- `tests/` — test suite demonstrating pytest usage.
- `tools/ci_run.py` — CI helper to run pytest + coverage + reports.
- `pytest.ini` — pytest configuration used by the project.

---

If you'd like, I can also add a short contributor guide, code style checks, or
expand the examples with a tiny usage script. Which would you prefer next?
