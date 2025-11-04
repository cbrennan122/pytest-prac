import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import pytest
import logging
log = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def sample_data():
    print("\n[SETUP] Loading sample data")
    data = {"values": [1, 2, 3]}
    yield data
    print("\n[TEARDOWN] Clearing sample data")
    data["values"].clear()

def test_sum(sample_data):
    log.info("Starting test_sum")
    assert sum(sample_data["values"]) == 6

def test_append(sample_data):
    log.info("Starting test_append")
    sample_data["values"].append(4)
    assert len(sample_data["values"]) == 4
    assert 4 in sample_data["values"]
