import pytest
import os
import telemetry
import time
import datetime
from unittest.mock import Mock

TEST_JOB = 'http://server/jenkins/job/HW_tests/' \
           'job/HW_test_multiconfig/lastSuccessfulBuild/'

@pytest.fixture(autouse=True)
def setup_env():
    test_directory = os.path.dirname(os.path.abspath(__file__))
    test_file_dir = os.path.join(telemetry.parser.FILE_DIR)
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
    ]
)
def test_get_parser(artifact, parser_object, parser_type):
    test_url = TEST_JOB + 'artifact/' + artifact
    telemetry.parser.grabber = Mock()
    p = telemetry.parser.get_parser(test_url)
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
    ]
)
def test_parser(artifact, parser_object, parser_type):
    test_url = TEST_JOB + 'artifact/' + artifact
    telemetry.parser.grabber = Mock()
    p = parser_object(test_url)
    assert p.url == test_url
    assert p.artifact_info_type == parser_type
    assert p.file_name == artifact
    assert len(p.payload_raw) > 0
