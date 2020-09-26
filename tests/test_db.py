import pytest
import os
import telemetry


@pytest.fixture(autouse=True)
def run_around_tests():
    # Before test
    if os.path.isfile("telemetry.db"):
        os.remove("telemetry.db")
    yield
    # After test
    if os.path.isfile("telemetry.db"):
        os.remove("telemetry.db")


def test_db_create():
    res = telemetry.db()
    assert os.path.isfile("telemetry.db")


def test_import_schema():
    res = telemetry.db(skip_db_create=True)
    loc = os.path.dirname(__file__)
    loc = os.path.split(loc)[:-1]
    loc = os.path.join(loc[0], "telemetry", "resources", "evm_tests.json")
    s = res.import_schema(loc)
    res.create_db_from_schema(s)
    assert os.path.isfile("telemetry.db")


def test_add_entry():
    res = telemetry.db(skip_db_create=True)
    loc = os.path.dirname(__file__)
    loc = os.path.split(loc)[:-1]
    loc = os.path.join(loc[0], "telemetry", "resources", "evm_tests.json")
    s = res.import_schema(loc)
    res.create_db_from_schema(s)
    # Add entry
    import datetime

    entry = {
        "NAME": "EVM_1",
        "DATE": str(datetime.datetime.now()),
        "TX_DEVICE": "PlutoA",
        "RX_DEVICE": "PlutoA",
        "CARRIER_FREQUENCY": 1000000000,
        "RX_SAMPLE_RATE": 1000000,
        "TX_SAMPLE_RATE": 1000000,
        "STANDARD": "LTE10_ETM3p1",
        "EVM_MEAN": 0.7,
        "EVM_STD": 3.2,
        "ITERATIONS_AT_CARRIER": 10,
    }
    res.add_entry(entry)
    res.print_all_schema()
