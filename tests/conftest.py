import os
from unittest.mock import patch, MagicMock
import pytest

# Set dummy environment variables for tests
@pytest.fixture(autouse=True)
def set_test_env():
    with patch.dict(os.environ, {
        "ADO_ORGANIZATION": "test-org",
        "ADO_PROJECT": "test-project",
        "ADO_PAT": "test-pat",
        "OPENAI_API_KEY": "test-key"
    }):
        yield
