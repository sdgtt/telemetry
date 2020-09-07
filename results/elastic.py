import sqlite3
from os import path
import logging
from datetime import datetime
from elasticsearch import Elasticsearch
# logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)

class elastic:
    schema = ""

    def __init__(self, server="alpine", port=9200,index_name="evm_tests"):
        self.es = Elasticsearch([{'host': server, 'port': port}],http_auth=('elastic', 'changeme'))
        # self.es = Elasticsearch(hosts="http://elastic:changeme@alpine:9200/")
        # self.es = Elasticsearch(hosts="http://elastic:changem e@192.168.86.33:9200/")
        if self.es.ping():
            print('Yay Connect')
        else:
            raise Exception('Awww it could not connect!')
        self.index_name = index_name
        # Check if table exists


    def search(self):
        res = self.es.search(index=self.index_name, body={"query": {"match_all": {}}})
        print(res)
        return res

    def test_store(self):
        record = {"test_name":"lte20MHz_pluto2","carrier_frequency":1000000000,"evm_mean":0.001}
        outcome = self.es.index(index=self.index_name, body=record)

    def test_stores(self):
        from random import random
        for freq in range(1000000000,6000000000,100000000):
            print(freq)
            for k in range(30):
                record = {"test_name":"lte20MHz_pluto2","carrier_frequency":freq,"evm_mean":random(),"iteration":k}
                outcome = self.es.index(index=self.index_name, body=record)

    def import_schema(self, json_filename):
        import json

        with open(json_filename) as json_raw:
            schema = json.load(json_raw)
        return schema

    def create_db_from_schema(self, schema):
        log.info(schema)
        log.info("Creating db")
        if not self.es.indices.exists(self.index_name):
            # self.es.indices.create(index=self.index_name, ignore=400, body=settings)
            self.es.indices.create(index=self.index_name, body=settings)
            log.info("Index created")
        else:
            log.info("Index exists")

    def check_if_exists(self, id):
        pass

    def add_entry(self, entry):
        id = 3
        if 1:#not self.check_if_exists(id):
            outcome = self.es.index(index=self.index_name, body=entry)

        else:
            logging.warning("Entry already exists")

    def __del__(self):
        self.es.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    d = elastic()
    # d.add_entry()
    # d.print_all()
    # del d
