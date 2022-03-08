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


def test_log_github_release_stats():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    rd = datetime.datetime.now()
    tel.log_github_release_stats("TransceiverToolbox", "v19.2.1", 1024, rd)
    time.sleep(2)
    results = tel.db.search_all()
    tel.db.delete_index()
    assert results["hits"]["total"]["value"] == 1


def test_search_github_release_stats():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    rd = datetime.datetime.now()
    tel.log_github_release_stats("TransceiverToolbox", "v19.2.1", 1024, rd)
    time.sleep(2)
    tel = telemetry.searches(server=server)
    tel.use_test_index = True
    stats = tel.github_release_stats()
    tel.db.delete_index()

    s = datetime.datetime.strptime(
        stats["TransceiverToolbox"]["release_date"], "%Y-%m-%dT%H:%M:%S.%f"
    )

    for k in stats:
        assert k == "TransceiverToolbox"
    assert stats["TransceiverToolbox"]["tag"] == "v19.2.1"
    assert stats["TransceiverToolbox"]["downloads"] == 1024
    assert s == rd


def test_ingest_boot_tests_stats():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True

    inputs = {
        "boot_folder_name": "zynq-adrv9361-z7035-bob",
        "hdl_hash": "ecd880d44cdd000691283f2edbd31aa52d6ccc3e",
        "linux_hash": "b0cb7c3bfd1fec02b1671b061112cd2551a9b340",
        "boot_partition_hash": "decb7c3bfd1fec02b1671b061112cd2551a9b3ac",
        "hdl_branch": "hdl_2019_r2",
        "linux_branch": "2019_R2",
        "boot_partition_branch": "NA",
        "is_hdl_release": True,
        "is_linux_release": True,
        "is_boot_partition_release": True,
        "uboot_reached": True,
        "linux_prompt_reached": True,
        "drivers_enumerated": 10,
        "drivers_missing": 5,
        "pytest_errors": 5,
        "pytest_failures": 5,
        "pytest_skipped": 5,
        "pytest_tests": 5,
        "matlab_errors": 5,
        "matlab_failures": 6,
        "matlab_skipped": 7,
        "matlab_tests": 8,
        "dmesg_warnings_found": 0,
        "dmesg_errors_found": 0,
        "jenkins_job_date": datetime.datetime.now(),  # "Dec 31, 2020 @ 13:47:04.129",
        "jenkins_build_number": 34,
        "jenkins_project_name": "pyadi-iio-hw",
        "jenkins_agent": "master",
        "jenkins_trigger": "manual",
        "last_failing_stage": "NA",
        "last_failing_stage_failure": "NA"
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
        "boot_partition_hash": "decb7c3bfd1fec02b1671b061112cd2551a9b3ac",
        "hdl_branch": "hdl_2019_r2",
        "linux_branch": "2019_R2",
        "boot_partition_branch": "NA",
        "is_hdl_release": True,
        "is_linux_release": True,
        "is_boot_partition_release": True,
        "uboot_reached": True,
        "linux_prompt_reached": True,
        "drivers_enumerated": 10,
        "drivers_missing": 5,
        "pytest_errors": 5,
        "pytest_failures": 5,
        "pytest_skipped": 5,
        "pytest_tests": 5,
        "matlab_errors": 5,
        "matlab_failures": 6,
        "matlab_skipped": 7,
        "matlab_tests": 8,
        "dmesg_warnings_found": 0,
        "dmesg_errors_found": 0,
        "jenkins_job_date": datetime.datetime.now(),  # "Dec 31, 2020 @ 13:47:04.129",
        "jenkins_build_number": 34,
        "jenkins_project_name": "pyadi-iio-hw",
        "jenkins_agent": "master",
        "jenkins_trigger": "manual",
        "last_failing_stage": "NA",
        "last_failing_stage_failure": "NA"
    }

    tel.log_boot_tests(**inputs)
    time.sleep(2)
    inputs["boot_folder_name"] = "zynq-adrv9361-z7035-fmc"
    tel.log_boot_tests(**inputs)
    time.sleep(2)
    tel = telemetry.searches(server=server)
    tel.use_test_index = True
    res = tel.boot_tests()
    tel.db.delete_index()
    assert len(res) == 2
    assert "zynq-adrv9361-z7035-fmc" in res.keys()
    assert "zynq-adrv9361-z7035-bob" in res.keys()

def test_ingest_log_artifacts():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True

    inputs = {
        "url": "http://SERVER/jenkins/job/HW_tests/job/HW_test_multiconfig/690/artifact/dmesg_zynq-adrv9361-z7035-fmc_err.log",
        "server": "http://SERVER/jenkins",
        "job": "HW_tests/HW_test_multiconfig",
        "job_no": 690,
        "job_date": None,
        "job_build_parameters": "NA",
        "file_name": "dmesg_zynq-adrv9361-z7035-fmc_err.log",
        "target_board": "zynq-adrv9361-z7035-fmc",
        "artifact_info_type": "dmesg_error",
        "payload_raw": "[    3.820072] systemd[1]: Failed to look up module alias 'autofs4': Function not implemented",
        "payload_ts": "3.820072",
        "payload": "systemd[1]: Failed to look up module alias 'autofs4': Function not implemented",
        "payload_param": "False-0-adi.adrv9002"
    }

    tel.log_artifacts(**inputs)
    time.sleep(2)
    results = tel.db.search_all()
    tel.db.delete_index()
    assert results["hits"]["total"]["value"] == 1

def test_search_artifacts():
    tel = telemetry.ingest(server=server)
    tel.use_test_index = True
    inputs = {
        "url": "http://SERVER/jenkins/job/HW_tests/job/HW_test_multiconfig/690/artifact/dmesg_zynq-adrv9361-z7035-fmc_err.log",
        "server": "http://SERVER/jenkins",
        "job": "HW_tests/HW_test_multiconfig",
        "job_no": 690,
        "job_date": None,
        "job_build_parameters": "NA",
        "file_name": "dmesg_zynq-adrv9361-z7035-fmc_err.log",
        "target_board": "zynq-adrv9361-z7035-fmc",
        "artifact_info_type": "dmesg_error",
        "payload_raw": "[    3.820072] systemd[1]: Failed to look up module alias 'autofs4': Function not implemented",
        "payload_ts": "3.820072",
        "payload": "systemd[1]: Failed to look up module alias 'autofs4': Function not implemented",
        "payload_param": "False-0-adi.adrv9002"
    }

    tel.log_artifacts(**inputs)
    time.sleep(2)
    inputs["file_name"] = "zynq-adrv9361-z7035-fmc_enumerated_devs.log"
    tel.log_artifacts(**inputs)
    time.sleep(2)
    tel = telemetry.searches(server=server)
    tel.use_test_index = True
    res = tel.artifacts()
    tel.db.delete_index()
    assert len(res) == 2
    assert "zynq-adrv9361-z7035-fmc_enumerated_devs.log" in res[0]['file_name']
    assert "dmesg_zynq-adrv9361-z7035-fmc_err.log" in res[1]['file_name']
