import os

import pytest
from fastapi.testclient import TestClient

# The terminal interaction API's flag (ADR-030) is cleared before anything imports `src.main`.
# With both flags exported, importing the app writes the token file for this checkout, replacing
# the token of a server that is running from it. The tests that need the API set the flag
# themselves, with a temporary HOME. HOME is not changed here: it would also change what git and
# other subprocess-based tests read.
os.environ.pop("D_SYSTEM_TERMINAL_API", None)

from src.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
