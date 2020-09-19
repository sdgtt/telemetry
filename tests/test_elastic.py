import pytest
import os
import telemetry
import time


@pytest.fixture(autouse=True)
def run_around_tests():
    # Before test
    res = telemetry.elastic()
    res.index_name = "dummy"
    res.delete_index()
    yield
    # After test
    res = telemetry.elastic()
    res.index_name = "dummy"
    res.delete_index()


def test_db_connect():
    telemetry.elastic()
    # Should complete without error
    assert True


def test_db_create_delete():
    res = telemetry.elastic()
    loc = os.path.dirname(__file__)
    loc = os.path.split(loc)[:-1]
    loc = os.path.join(loc[0], "telemetry", "resources", "evm_tests_el.json")
    s = res.import_schema(loc)
    res.create_db_from_schema(s)
    res.delete_index()


def test_add_entry():
    res = telemetry.elastic()
    loc = os.path.dirname(__file__)
    loc = os.path.split(loc)[:-1]
    loc = os.path.join(loc[0], "telemetry", "resources", "evm_tests_el.json")
    s = res.import_schema(loc)
    res.create_db_from_schema(s)

    # Add entry
    import datetime

    entry = {
        "test_name": "EVM_1",
        "date": datetime.datetime.now(),
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
    time.sleep(2)
    results = res.search_all()
    res.delete_index()
    print(results)
    assert results["hits"]["total"]["value"] == 1


def test_ingest_tx_quad_cal():
    tel = telemetry.ingest()
    tel.use_test_index = True
    tel.log_ad9361_tx_quad_cal_test("test1", "pluto", 4, 100, 0)
    time.sleep(2)
    results = tel.db.search_all()
    tel.db.delete_index()
    assert results["hits"]["total"]["value"] == 1


def test_search_tx_quad_cal():
    tel = telemetry.ingest()
    tel.use_test_index = True
    tel.log_ad9361_tx_quad_cal_test("test1", "pluto", 4, 100, 0)
    time.sleep(2)
    tel = telemetry.searches()
    tel.use_test_index = True
    x, y, t = tel.ad9361_tx_quad_cal_test()
    tel.db.delete_index()
    assert y == [4]
    assert t == [100]
    assert x


def test_search_tx_quad_cal_chan1():
    tel = telemetry.ingest()
    tel.use_test_index = True
    tel.log_ad9361_tx_quad_cal_test("test1", "pluto", 4, 100, 0)
    time.sleep(2)
    tel = telemetry.searches()
    tel.use_test_index = True
    x, y, t = tel.ad9361_tx_quad_cal_test(channel=1)
    tel.db.delete_index()
    assert y == []
    assert t == []
    assert x == []


def test_search_tx_quad_cal_chan0():
    tel = telemetry.ingest()
    tel.use_test_index = True
    tel.log_ad9361_tx_quad_cal_test("test1", "pluto", 4, 100, 0)
    time.sleep(2)
    tel = telemetry.searches()
    tel.use_test_index = True
    x, y, t = tel.ad9361_tx_quad_cal_test(channel=0)
    tel.db.delete_index()
    assert y == [4]
    assert t == [100]
    assert x


def test_ingest_lte():
    tel = telemetry.ingest()
    tel.use_test_index = True
    tel.log_lte_evm_test(
        "test2", "lte20_tm3.1", "pluto", "pluto", 30720000, 30720000, 1000000000, 0.1, 1
    )
    time.sleep(2)
    results = tel.db.search_all()
    tel.db.delete_index()
    assert results["hits"]["total"]["value"] == 1
