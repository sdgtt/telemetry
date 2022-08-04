import glob
import os
from unittest import result
from .common import ProductionLog

import pymongo


class BoardLog(ProductionLog):

    skip_insert = True
    default_unprocessed_log_dir = "/test/logs/unprocessed"
    default_processed_log_dir = "/test/logs/processed"

    def get_all_logs(self):
        return self.collection.find({"board": self.board_name})

    def parse_filename(self, filename):
        """
        Parse the filename to get the board name and timestamp
        :param filename:
        :return:
        """
        # Example: failed_S11-1111SN:11111_2022-03-01_10-54-32.log
        filename = filename.split("/")[len(filename.split("/")) - 1]
        if(filename.split("_")[0].split("/")[-1] == "no"):
            date = "no_date"
            status = filename.split("_")[2]
            serial_number = filename.split("_")[3]
        else:
            date = filename.split("_")[2].split(".")[0]
            status = filename.split("_")[0].split("/")[-1]
            serial_number = filename.split("_")[1]
        return status, serial_number, date

    def process_logs(self, schema) -> None:

        files = glob.glob(f"{self.default_unprocessed_log_dir}/*.log")

        for file in files:
            print("Processing file:", file)
            try:
                status, serial_number, date = self.parse_filename(file)
            except Exception as e:
                print(e)
                print("Unable to parse filename:", file)
                continue
            with open(file, "r") as f:
                content = f.read()
                schema_new = schema.copy()
                schema_new["raw_log"] = content
                schema_new["test_date"] = date
                schema_new["serial_number"] = serial_number
                schema_new["status"] = status
                try:
                    result = self.collection.insert_one(schema_new)
                    print("Inserted:", result.inserted_id)
                except pymongo.errors.DuplicateKeyError:
                    print("Duplicate key error")
                filename = os.path.basename(file)
                os.rename(file, f"{self.default_processed_log_dir}/{filename}")

        return None  # Signal not to upload after as we already did it
