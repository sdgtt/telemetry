import pytest
import os
import telemetry
import time
import datetime
from unittest.mock import patch

TEST_JOB = 'http://server/jenkins/job/HW_tests/' \
           'job/HW_test_multiconfig/lastSuccessfulBuild/'

@pytest.fixture(autouse=True)
def setup_env():
    test_directory = os.path.dirname(os.path.abspath(__file__))
    test_file_dir = os.path.join("event_horizon")
    if not os.path.exists(test_file_dir):
        os.mkdir(test_file_dir)
    os.system('cp -a {} {}'.format(os.path.join(test_directory,'test_artifacts','.'),test_file_dir))
    yield
    os.system('rm -rf {}'.format(test_file_dir))


@pytest.mark.parametrize(
    "artifact,parser_object,parser_type",
    [
        ('dmesg_pluto.log', telemetry.parser.Dmesg, 'dmesg'),
        ('dmesg_pluto_err.log', telemetry.parser.DmesgError, 'dmesg_err'),
        ('dmesg_pluto_warn.log', telemetry.parser.DmesgWarning, 'dmesg_warn'),
        ('zynq-zed-adv7511-adrv9002-rx2tx2-vcmos_enumerated_devs.log', \
            telemetry.parser.EnumeratedDevs, 'enumerated_devs'),
        ('zynq-zed-adv7511-adrv9002-rx2tx2-vcmos_missing_devs.log', \
            telemetry.parser.MissingDevs, 'missing_devs'),
        ('info.txt', telemetry.parser.InfoTxt, 'info_txt'),
    ]
)
def test_get_parser(artifact, parser_object, parser_type):
    test_url = TEST_JOB + 'artifact/' + artifact
    grabber = telemetry.grabber.Grabber()
    with patch.object(parser_object, "get_payload_raw"):
        p = telemetry.parser.get_parser(test_url,grabber)
        assert type(p) == parser_object

@pytest.mark.parametrize(
    "artifact,parser_object,parser_type",
    [
        ('dmesg_pluto.log', telemetry.parser.Dmesg, 'dmesg'),
        ('dmesg_pluto_err.log', telemetry.parser.DmesgError, 'dmesg_err'),
        ('dmesg_pluto_warn.log', telemetry.parser.DmesgWarning, 'dmesg_warn'),
        ('zynq-zed-adv7511-adrv9002-rx2tx2-vcmos_enumerated_devs.log', \
            telemetry.parser.EnumeratedDevs, 'enumerated_devs'),
        ('zynq-zed-adv7511-adrv9002-rx2tx2-vcmos_missing_devs.log', \
            telemetry.parser.MissingDevs, 'missing_devs'),
        ('info.txt', telemetry.parser.InfoTxt, 'info_txt'),
        ('zynqmp_zcu102_rev10_fmcdaq3_reports.xml', telemetry.parser.PytestFailure, 'pytest_failure'),
    ]
)
def test_parser(artifact, parser_object, parser_type):
    test_url = TEST_JOB + 'artifact/' + artifact
    grabber = telemetry.grabber.Grabber()
    with patch.object(
        telemetry.grabber.Grabber,
        "download_file",
        return_value=os.path.join("event_horizon", artifact)
    ):
        p = parser_object(test_url, grabber)
        assert p.url == test_url
        assert p.artifact_info_type == parser_type
        assert p.file_name == artifact
        assert len(p.payload_raw) > 0
        assert len(p.payload) > 0
        assert len(p.payload_raw) > 0