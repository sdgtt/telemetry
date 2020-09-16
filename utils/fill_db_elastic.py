import os
import results
from random import random
import datetime

res = results.elastic()
# loc = os.path.dirname(__file__)
# loc = os.path.split(loc)[:-1]
# loc = os.path.join(loc[0], "resources", "evm_tests_el.json")
# s = res.import_schema(loc)
# res.create_db_from_schema(s)
# Add entry

los = range(1, 600)

for lo in los:
    lo_full = lo * 10000000
    print(lo_full)
    for iteration in range(1, 10):
        entry = {
            "test_name": "evm_1",
            "date": str(datetime.datetime.now()),
            "tx_device": "PlutoA",
            "rx_device": "PlutoA",
            "carrier_frequency": lo_full,
            "tx_sample_rate": 1000000,
            "rx_sample_rate": 1000000,
            "standard": "LTE10_ETM3p1",
            "evm_db": random() * lo,
            "iteration": iteration,
        }
        res.add_entry(entry)
    # res.search()
