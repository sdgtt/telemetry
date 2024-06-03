"""Core features for development board telemetry."""

import datetime
import os
from typing import List

import pymongo
from minio import Minio
import yaml


class Core:
    def __init__(
        self,
        project_type,
        configfilename=None,
        configs: dict = {},
    ):

        extracted_config = {"mongo": None, "minio": None}
        if configfilename:
            if not os.path.isfile(configfilename):
                raise Exception(f"Config file {configfilename} does not exist")

            with open(configfilename) as f:
                config = yaml.load(f, Loader=yaml.FullLoader)

            for k in config:
                project = config[k]
                project_name = project["project"]
                if project_name == project_type:
                    servers = project["servers"]
                    for server in servers:
                        if "type" not in server:
                            continue
                        if server["type"] == "mongo":
                            extracted_config["mongo"] = server
                        elif server["type"] == "minio":
                            extracted_config["minio"] = server

        # Merge configs where configs input takes precedence
        for k in extracted_config:
            if k in configs:
                extracted_config[k] = {**extracted_config[k], **configs[k]}

        if "mongo" in extracted_config:
            self.mongo = self.setup_mongo(extracted_config["mongo"])
        else:
            raise Exception("No MongoDB configuration found")

        if "minio" in extracted_config:
            self.minio = self.setup_minio(extracted_config["minio"])
        else:
            raise Exception("No Minio configuration found")

    def setup_mongo(self, config):
        """Setup MongoDB connection."""
        # Check config
        required_fields = [
            "username",
            "password",
            "address",
            "port",
            "database",
            "collection",
        ]
        for f in required_fields:
            if f not in config:
                raise Exception(f"Mongo config missing field {f}")

        cmd = f"mongodb://{config['username']}:{config['password']}@{config['address']}:{config['port']}/"

        try:
            self.client = pymongo.MongoClient(cmd)
        except Exception as e1:
            try:
                cmd = cmd.replace("mongodb+srv://", "mongodb://")
                self.client = pymongo.MongoClient(cmd)
            except Exception as e2:
                print(e1, e2)
                raise Exception("Unable to connect to MongoDB")

        db = self.client[config["database"]]
        self.collection = db[config["collection"]]

        return self.client

    def setup_minio(self, config):
        """Setup Minio connection."""
        # Check config
        required_fields = ["address", "port", "access_key", "secret_key"]
        for f in required_fields:
            if f not in config:
                raise Exception(f"Minio config missing field {f}")
        address = f"{config['address']}:{config['port']}"
        return Minio(
            address,
            access_key=config["access_key"],
            secret_key=config["secret_key"],
            secure=False,
        )
