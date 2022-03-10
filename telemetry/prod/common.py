import datetime
import os
from abc import ABCMeta, abstractmethod

import pymongo


class ProductionLog(metaclass=ABCMeta):

    production_test_schema = {
        "raw_log": "string",
        "upload_date": "string",
        "board": "string",
    }

    skip_insert = False

    def __init__(self, server=None, username=None, password=None, dbname=None) -> None:

        if not server:
            server = os.getenv("DBSERVER")
        if not username:
            username = os.getenv("DBUSERNAME")
        if not password:
            password = os.getenv("DBPASSWORD")
        if not dbname:
            dbname = os.getenv("DBNAME")

        cmd = f"mongodb+srv://{username}:{password}@{server}/"

        try:
            self.client = pymongo.MongoClient(cmd)
        except Exception as e1:
            try:
                cmd = cmd.replace("mongodb+srv://", "mongodb://")
                self.client = pymongo.MongoClient(cmd)
            except Exception as e2:
                print(e1, e2)
                raise Exception("Unable to connect to MongoDB")

        db = self.client["sdg"]
        self.collection = db[dbname]

    def _ref_scheme(self):
        s = self.production_test_schema.copy()
        s["upload_date"] = datetime.datetime.now().isoformat()
        s["board"] = self.board_name
        return s

    @abstractmethod
    def process_logs(self) -> None:
        """Name of driver used for transmitting data.
        This is the IIO device used collect data from.
        """
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def board_name(self) -> None:
        """Name of driver used for transmitting data.
        This is the IIO device used collect data from.
        """
        raise NotImplementedError  # pragma: no cover

    def __call__(self) -> None:

        schema = self._ref_scheme()
        data = self.process_logs(schema)
        if not self.skip_insert and data:
            self.collection.insert_one(data)
