import pytest
import os
import results


@pytest.fixture(autouse=True)
def run_around_tests():
    # Before test
    if os.path.isfile("results.db"):
        os.remove("results.db")
    yield
    # After test
    if os.path.isfile("results.db"):
        os.remove("results.db")


def test_db_create():
    res = results.db()
    assert os.path.isfile("results.db")


def test_import_schema():
    res = results.db(skip_db_create=True)
    loc = os.path.dirname(__file__)
    loc = os.path.split(loc)[:-1]
    loc = os.path.join(loc[0], "resources", "evm_tests.json")
    s = res.import_schema(loc)
    res.create_db_from_schema(s)
    assert os.path.isfile("results.db")
