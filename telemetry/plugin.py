import os
import time

import pytest

import telemetry

required_metadata = {"vpx": {"hdl_hash": None, "linux_hash": None}}


def pytest_addoption(parser):
    group = parser.getgroup("telemetry")
    group.addoption(
        "--telemetry-enable",
        action="store_true",
        default=False,
        help="Enable telemetry upload",
    )
    group.addoption(
        "--telemetry-configpath",
        action="store",
        default=None,
        help="Path to telemetry configuration file",
    )
    group.addoption(
        "--telemetry-jenkins-job",
        action="store",
        default=None,
        help="Path to junit xml report",
    )
    for field in required_metadata["vpx"]:
        group.addoption(
            f"--telemetry-{field}",
            action="store",
            default=None,
            help=f"Metadata field {field}",
        )


# Run at the start of the test session
def pytest_configure(config):
    # Check if telemetry is enabled
    if not config.option.telemetry_enable:
        return

    # Check dependencies
    path = config.option.xmlpath
    if not path:
        raise Exception(
            "junit report generation not enabled. Needed for telemetry upload. \nAdd --junitxml=path/to/report.xml to pytest command line"
        )

    # Check if databases are reachable
    configfilename = config.option.telemetry_configpath
    try:
        res = telemetry.VPX(configfilename=configfilename)
    except Exception as e:
        raise Exception("Unable to connect to databases") from e

    # Make sure we have necessary metadata before starting tests
    project = "vpx"

    # These can exist as environment variables or from the CLI
    metadata = required_metadata[project]
    for field in required_metadata[project]:
        metadata[field] = os.getenv(field.upper(), "NA")
    # Overwrite with CLI values
    for field in required_metadata[project]:
        field = field.replace("-", "_")
        if hasattr(config.option, f"telemetry_{field}"):
            val = getattr(config.option, f"telemetry_{field}")
            if val:
                metadata[field] = val

    metadata["test_date"] = str(time.strftime("%Y%m%d_%H%M%S"))

    # Save res to config for later use
    config._telemetry = res
    config._telemetry_metadata = metadata


# Hook to run after all tests are done
def pytest_sessionfinish(session, exitstatus):
    # Get XML data
    xmlpath = session.config.option.xmlpath
    with open(xmlpath, "r") as f:
        xml = f.read()
    session.config._telemetry_metadata["junit_xml"] = xml

    res = session.config._telemetry
    # Create job ID
    if session.config.option.telemetry_jenkins_job:
        job_id = f"j{str(session.config.option.telemetry_jenkins_job)}"
    else:
        job_id = "m" + str(time.strftime("%Y%m%d_%H%M%S"))

    # Get files
    telemetry_files = session.config.stash.get("telemetry_files", None)

    res.submit_test_data(
        job_id, session.config._telemetry_metadata, [xmlpath] + telemetry_files
    )


@pytest.fixture(scope="session", autouse=True)
def telemetry_files(pytestconfig):
    """Fixture to store files for telemetry upload."""
    files = []
    yield files
    pytestconfig.stash["telemetry_files"] = files
