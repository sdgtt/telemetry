import pytest
import os
import time

import telemetry


@pytest.fixture(autouse=True)
def run_around_tests():
    ...
    # # Before test
    # if os.path.isfile("telemetry.db"):
    #     os.remove("telemetry.db")
    # yield
    # # After test
    # if os.path.isfile("telemetry.db"):
    #     os.remove("telemetry.db")


def test_connect(telemetry_files):

    loc = os.path.dirname(__file__)
    config = os.path.join(loc, "dev_test_config.yaml")

    res = telemetry.VPX(configfilename=config)
    assert res.mongo
    assert res.minio

    telemetry_files.append(config)


def test_submit_test_data():

    loc = os.path.dirname(__file__)
    config = os.path.join(loc, "dev_test_config.yaml")
    res = telemetry.VPX(configfilename=config)

    date = time.strftime("%Y%m%d_%H%M%S")
    job_id = "m" + date

    loc = os.path.join(loc, "vpx_test_data", "report.xml")
    with open(loc, "r") as f:
        xml = f.read()

    # Date of form YYYYMMDD_HHMMSS
    metadata = {
        "junit_xml": xml,
        "hdl_hash": "1234",
        "linux_hash": "5678",
        "test_date": date,
    }

    res.submit_test_data(job_id, metadata, [loc])
