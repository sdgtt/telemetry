import json
import logging
from elasticsearch import Elasticsearch

# logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)


class elastic:
    schema = ""

    def __init__(
        self,
        server="alpine",
        port=9200,
        username="elastic",
        password="changeme",
        index_name="example_index",
        scheme="http"
    ):
        self.es = Elasticsearch(
            [{"host": server, "port": port, "scheme":scheme}],
            http_auth=(username, password),
            timeout=3,
            max_retries=2,
            retry_on_timeout=True,
        )
        if not self.es.ping():
            raise Exception("Elasticsearch server not accessible")
        self.index_name = index_name

    def search_all(self):
        res = self.es.search(index=self.index_name, body={"query": {"match_all": {}}})
        print(res)
        return res

    def import_schema(self, json_filename):
        with open(json_filename) as json_raw:
            schema = json.load(json_raw)
        return schema

    def create_db_from_schema(self, schema):
        log.info(schema)
        log.info("Creating db")
        if not self.es.indices.exists(self.index_name):
            # self.es.indices.create(index=self.index_name, ignore=400, body=settings)
            self.es.indices.create(index=self.index_name, body=schema)
            log.info("Index created")
        else:
            log.info("Index exists")

    def add_entry(self, entry):
        if not self.es.indices.exists(self.index_name):
            raise Exception("Index does not exist")
        outcome = self.es.index(index=self.index_name, body=entry)
        log.info(outcome)
        assert outcome["result"] == "created", "Unable to add entry"

    def __del__(self):
        self.es.close()

    def delete_index(self):
        """ Delete database index (table) """
        if self.es.indices.exists(self.index_name):
            ret = self.es.indices.delete(index=self.index_name)
            assert ret["acknowledged"], "Index deletion failed"
        else:
            log.info("Index does not exist")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    d = elastic()
    # d.add_entry()
    # d.print_all()
    # del d