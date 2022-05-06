import datetime
import os
import glob
from abc import ABCMeta, abstractmethod

import pymongo

class TextInfo(metaclass=ABCMeta):
    cn0511_schema = {
        "raw_text": "string",
        "upload_date": "string",
        "board": "string"
    }

    def __init__(self, server=None, username=None, password=None, dbname=None, boardname=None) -> None:

        if not server:
            server = os.getenv("DBSERVER")
        if not username:
            username = os.getenv("DBUSERNAME")
        if not password:
            password = os.getenv("DBPASSWORD")
        if not dbname:
            dbname = os.getenv("DBNAME")
        if not boardname:
            self.board_name = os.getenv("BOARD_NAME")
        else:
            self.board_name = boardname
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

        db = self.client["production_test3"]
        self.collection = db[dbname]
    
    def _ref_scheme(self):
        s = self.cn0511_schema.copy()
        s["upload_date"] = datetime.datetime.now().isoformat()
        s["board"] = "cn0511"
        return s
    
    def process_file(self, schema) -> None:
        files = glob.glob(f"{self.default_unprocessed_log_dir}/*.txt")

        for file in files:
            with open(file, "r") as f:
                content = f.read()
                schema_new = schema.copy()
                schema_new["raw_text"] = content
                last_dir = file.split("/")
                schema_new["serial_number"] = file.split("/")[len(last_dir) - 1].split(".")[0]

                try:
                    result = self.collection.insert_one(schema_new)
                    print("Inserted:", result.inserted_id)
                except pymongo.errors.DuplicateKeyError:
                    print("Duplicate key error")
                filename = os.path.basename(file)
                os.rename(file, f"{self.default_processed_log_dir}/{filename}")
    
        return None

    def __call__(self) -> None:

        schema = self._ref_scheme()
        data = self.process_file(schema)
        if data:
            self.collection.insert_one(data)
    