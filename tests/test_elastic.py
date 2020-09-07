import pytest
import os
import results


@pytest.fixture(autouse=True)
def run_around_tests():
    # Before test
    yield
    # After test


def test_db_create():
    results.elastic()
    # Should complete without error


def test_import_schema():
    res = results.elastic()
    loc = os.path.dirname(__file__)
    loc = os.path.split(loc)[:-1]
    loc = os.path.join(loc[0], "resources", "evm_tests_el.json")
    s = res.import_schema(loc)
    res.create_db_from_schema(s)


def test_add_entry():
    res = results.elastic()
    # loc = os.path.dirname(__file__)
    # loc = os.path.split(loc)[:-1]
    # loc = os.path.join(loc[0], "resources", "evm_tests_el.json")
    # s = res.import_schema(loc)
    # res.create_db_from_schema(s)
    # Add entry
    import datetime

    entry = {
        "test_name": "EVM_1",
        "date": str(datetime.datetime.now()),
        "tx_device": "PlutoA",
        "rx_device": "PlutoA",
        "CARRIER_FREQUENCY": 1000000000,
        "tx_sample_rate": 1000000,
        "rx_sample_rate": 1000000,
        "standard": "LTE10_ETM3p1",
        "evm_db": 3.2,
        "iteration": 1,
    }
    res.add_entry(entry)
    res.search()
