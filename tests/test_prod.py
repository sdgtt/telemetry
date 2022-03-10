import pytest
import os
import telemetry
import time
import datetime


@pytest.fixture(autouse=True)
def run_around_tests():
    # Before test
    sync = telemetry.prod.SynchronaLog()
    result = sync.collection.delete_many({})
    yield
    # After test
    sync = telemetry.prod.SynchronaLog()
    result = sync.collection.delete_many({})


def test_prod_synchrona_example_import():
    sync = telemetry.prod.SynchronaLog()
    pwd = os.path.dirname(os.path.abspath(__file__))
    artifact_dir = os.path.join(pwd, "prod_example_artifacts")
    sync = telemetry.prod.SynchronaLog()
    sync.default_unprocessed_log_dir = artifact_dir
    # Do import
    sync()
    # Check
    logs = sync.get_all_logs()
    assert len(logs) == 11
