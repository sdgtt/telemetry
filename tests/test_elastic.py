import pytest
import os
import telemetry
import time
import datetime

server = os.environ.get("SERVER") if "SERVER" in os.environ else "alpine"


@pytest.fixture(autouse=True)
def run_around_tests():
    # Before test
    res = telemetry.elastic(server=server)
    res.index_name = "dummy"
    res.delete_index()
    yield
    # After test
    res = telemetry.elastic(server=server)
    res.index_name = "dummy"
    res.delete_index()


def test_db_connect():
    telemetry.elastic(server=server)
    # Should complete without error
    assert True


def test_db_create_delete():
    res = telemetry.elastic(server=server)
    loc = os.path.dirname(__file__)
    loc = os.path.split(loc)[:-1]
    loc = os.path.join(loc[0], "telemetry", "resources", "evm_tests_el.json")
    s = res.import_schema(loc)
    res.create_db_from_schema(s)
    res.delete_index()


def test_add_entry():
    res = telemetry.elastic(server=server)
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
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    tel.log_ad9361_tx_quad_cal_test("test1", "pluto", 4, 100, 0)
    time.sleep(2)
    results = tel.db.search_all()
    tel.db.delete_index()
    assert results["hits"]["total"]["value"] == 1


def test_search_tx_quad_cal():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    tel.log_ad9361_tx_quad_cal_test("test1", "pluto", 4, 100, 0)
    time.sleep(2)
    tel = telemetry.searches(server=server)
    tel.use_test_index = True
    x, y, t = tel.ad9361_tx_quad_cal_test()
    tel.db.delete_index()
    assert y == [4]
    assert t == [100]
    assert x


def test_search_tx_quad_cal_chan1():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    tel.log_ad9361_tx_quad_cal_test("test1", "pluto", 4, 100, 0)
    time.sleep(2)
    tel = telemetry.searches(server=server)
    tel.use_test_index = True
    x, y, t = tel.ad9361_tx_quad_cal_test(channel=1)
    tel.db.delete_index()
    assert y == []
    assert t == []
    assert x == []


def test_search_tx_quad_cal_chan0():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    tel.log_ad9361_tx_quad_cal_test("test1", "pluto", 4, 100, 0)
    time.sleep(2)
    tel = telemetry.searches(server=server)
    tel.use_test_index = True
    x, y, t = tel.ad9361_tx_quad_cal_test(channel=0)
    tel.db.delete_index()
    assert y == [4]
    assert t == [100]
    assert x


def test_ingest_lte():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    tel.log_lte_evm_test(
        "AD9361",
        -10,
        "slow_attack",
        1e9,
        "TM 3.1",
        "5 MHz",
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
    )
    time.sleep(2)
    results = tel.db.search_all()
    tel.db.delete_index()
    assert results["hits"]["total"]["value"] == 1


def test_ingest_github_stats():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    tel.log_ad9361_tx_quad_cal_test("TransceiverToolbox", 1, 2, 3, 4)
    time.sleep(2)
    results = tel.db.search_all()
    tel.db.delete_index()
    assert results["hits"]["total"]["value"] == 1


def test_search_github_stats():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    tel.log_github_stats("TransceiverToolbox", 1, 2, 3, 4)
    time.sleep(2)
    tel = telemetry.searches(server=server)
    tel.use_test_index = True
    stats = tel.github_stats()
    tel.db.delete_index()
    for k in stats:
        assert k == "TransceiverToolbox"
    assert stats["TransceiverToolbox"]["views"] == 1
    assert stats["TransceiverToolbox"]["clones"] == 2
    assert stats["TransceiverToolbox"]["view_unique"] == 3
    assert stats["TransceiverToolbox"]["clones_unique"] == 4


def test_ingest_boot_tests_stats():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True

    inputs = {
        "boot_folder_name": "zynq-adrv9361-z7035-bob",
        "hdl_hash": "ecd880d44cdd000691283f2edbd31aa52d6ccc3e",
        "linux_hash": "b0cb7c3bfd1fec02b1671b061112cd2551a9b340",
        "hdl_branch": "hdl_2019_r2",
        "linux_branch": "2019_R2",
        "is_hdl_release": True,
        "is_linux_release": True,
        "uboot_reached": True,
        "linux_prompt_reached": True,
        "drivers_enumerated": True,
        "dmesg_warnings_found": False,
        "dmesg_errors_found": False,
        "jenkins_job_date": datetime.datetime.now(),  # "Dec 31, 2020 @ 13:47:04.129",
        "jenkins_build_number": 34,
        "jenkins_project_name": "pyadi-iio-hw",
        "jenkins_agent": "master",
    }

    tel.log_boot_tests(**inputs)
    time.sleep(2)
    results = tel.db.search_all()
    tel.db.delete_index()
    assert results["hits"]["total"]["value"] == 1


def test_ingest_hdl_resources():
    loc = os.path.dirname(__file__)
    loc = os.path.split(loc)[:-1]
    loc = os.path.join(loc[0], "tests", "resource_utilization.csv")

    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    tel.log_hdl_resources_from_csv(loc)
    time.sleep(2)
    results = tel.db.search_all()
    tel.db.delete_index()
    assert results["hits"]["total"]["value"] == 1


def test_search_boot_tests():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    inputs = {
        "boot_folder_name": "zynq-adrv9361-z7035-bob",
        "hdl_hash": "ecd880d44cdd000691283f2edbd31aa52d6ccc3e",
        "linux_hash": "b0cb7c3bfd1fec02b1671b061112cd2551a9b340",
        "hdl_branch": "hdl_2019_r2",
        "linux_branch": "2019_R2",
        "is_hdl_release": True,
        "is_linux_release": True,
        "uboot_reached": True,
        "linux_prompt_reached": True,
        "drivers_enumerated": True,
        "dmesg_warnings_found": False,
        "dmesg_errors_found": False,
        "jenkins_job_date": datetime.datetime.now(),  # "Dec 31, 2020 @ 13:47:04.129",
        "jenkins_build_number": 34,
        "jenkins_project_name": "pyadi-iio-hw",
        "jenkins_agent": "master",
    }

    tel.log_boot_tests(**inputs)
    time.sleep(2)
    inputs["boot_folder_name"] = "zynq-adrv9361-z7035-fmc"
    tel.log_boot_tests(**inputs)
    time.sleep(2)
    tel = telemetry.searches(server=server)
    tel.use_test_index = True
    res = tel.boot_tests(inputs["boot_folder_name"])
    tel.db.delete_index()
    assert len(res) == 2
    assert "zynq-adrv9361-z7035-fmc" in res.keys()
    assert "zynq-adrv9361-z7035-bob" in res.keys()
