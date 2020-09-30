import sqlite3
from os import path
import logging

# logging.basicConfig(level=logging.DEBUG)


class db:
    schema = ""

    def __init__(self, db_filename="telemetry.db", skip_db_create=False):
        self.db_filename = db_filename
        self.table_name = "COMPANY"
        if not path.exists(self.db_filename):
            self.conn = sqlite3.connect(self.db_filename)
            if not skip_db_create:
                self.create_db()
        else:
            self.conn = sqlite3.connect(self.db_filename)

    def import_schema(self, json_filename):
        import json

        with open(json_filename) as json_raw:
            schema = json.load(json_raw)
        return schema

    def create_db_from_schema(self, schema):
        tbl = " ("
        fields = schema["fields"]
        for field in fields:
            tbl += field + " "
            for subfield in fields[field]:
                tbl += subfield + " "
            tbl = tbl[:-1] + ", "
        tbl = tbl[:-2] + ");"
        tbl = "CREATE TABLE " + schema["table_name"] + tbl
        logging.info(tbl)
        logging.info("Creating db")
        self.conn.execute(tbl)
        self.table_name = schema["table_name"]
        self.schema = schema
        logging.info("Created db")

    def create_db(self):
        logging.info("Creating db")
        self.conn.execute(
            """CREATE TABLE """
            + self.table_name
            + """
            (ID INT PRIMARY KEY     NOT NULL,
            NAME           TEXT    NOT NULL,
            AGE            INT     NOT NULL,
            ADDRESS        CHAR(50),
            SALARY         REAL);"""
        )
        logging.info("Created db")

    def check_if_exists(self, id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM " + self.table_name + " WHERE ID=?", (id,))
        rows = cur.fetchall()
        logging.info("Found entries:")
        logging.info(rows)
        return len(rows) > 0

    def add_entry_example(self):
        id = 3
        if not self.check_if_exists(id):
            self.conn.execute(
                "INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
                    VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )"
            )
            self.conn.commit()
        else:
            logging.warning("Entry already exists")

    def add_entry(self, entry):
        id = 3
        if not self.check_if_exists(id):
            fields = "ID, "
            values = "3, "
            for field in entry:
                fields += field + ", "
                if self.schema["fields"][field][0] in ["TEXT", "DATETIME"]:
                    values += "'" + str(entry[field]) + "', "
                else:
                    values += str(entry[field]) + ", "
            fields = fields[:-2]
            values = values[:-2]
            cmd = (
                "INSERT INTO "
                + self.table_name
                + " ("
                + fields
                + ") VALUES ("
                + values
                + ")"
            )
            logging.info(cmd)
            self.conn.execute(cmd)
            self.conn.commit()
        else:
            logging.warning("Entry already exists")

    def print_all(self):
        cursor = self.conn.execute("SELECT id, name, address, salary from COMPANY")
        for row in cursor:
            print("ID = ", row[0])
            print("NAME = ", row[1])
            print("ADDRESS = ", row[2])
            print("SALARY = ", row[3])

    def print_all_schema(self):
        fields = self.schema["fields"].keys()
        fields = [*fields]
        print(fields)
        all_fields = ", ".join(fields)
        cursor = self.conn.execute("SELECT " + all_fields + " from " + self.table_name)
        for row in cursor:
            for i, field in enumerate(fields):
                print(field, "=", row[i])

    def __del__(self):
        self.conn.close()


if __name__ == "__main__":
    d = db()
    d.add_entry()
    d.print_all()
    del d
