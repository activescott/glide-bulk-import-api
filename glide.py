from typing import Dict, Any, Iterator, List
import logging
import requests
import os
import argparse
import json
import uuid

LOG_LEVEL_DEFAULT = logging.INFO
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL_DEFAULT)
# for stdout:
logger.addHandler(logging.StreamHandler())

TableRow = Dict[str, Any]

ALLOWED_COLUMN_TYPES = [
    "string",
    "number",
    "boolean",
    "url",
    "dateTime",
    "json",
]

class TableColumn(dict):
    """
    Represents a Column in the glide API.
    NOTE: inherits from dict to be serializable to json.
    """

    def __init__(self, id: str, type: str, displayName: str):
        if type not in ALLOWED_COLUMN_TYPES:
            raise ValueError(f"Column type {type} not allowed. Must be one of {ALLOWED_COLUMN_TYPES}")  # nopep8
        dict.__init__(self, id=id, type={
                      "kind": type}, displayName=displayName)

    def id(self) -> str:
        return self['id']

    def type(self) -> str:
        # NOTE: we serialize this as {kind: "<typename>"} per the rest API's serialization
        return self['type']['kind']
    
    def json(self) -> str:
        return json.dumps(self)

    def __repr__(self):
        return self.json()

    def __eq__(self, other):
        if not isinstance(other, TableColumn):
            return False
        return dict(self) == dict(other)

class Table(dict):
    def __init__(self, id: str, name: str):
        dict.__init__(self, id=id, name=name)

    def id(self) -> str:
        return self['id']

    def name(self) -> str:
        return self['name']

    def __eq__(self, other):
        if not isinstance(other, Table):
            return False
        return dict(self) == dict(other)

    def json(self) -> str:
        return json.dumps(self)

    def __repr__(self):
        return self.json()


class GlideApi:
    def _reset_stash(self):
        self.stash_id = None
        self.stash_serial = 0

    def __init__(self, api_token=None, base_url='https://api.glideapps.com'):
        self.base_url = base_url

        self.api_token = api_token if not api_token == None else os.getenv(
            'GLIDE_TOKEN')
        if self.api_token is None:
            raise Exception("Please set the GLIDE_TOKEN environment variable")

        self._reset_stash()

    def url(self, path: str) -> str:
        return f"{self.base_url}/{path}"

    def headers(self):
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        return headers

    def stash_rows(self, rows: List[TableRow]) -> None:
        # if we haven't started a stash, create one:
        if self.stash_id is None:
            self.stash_id = uuid.uuid4().hex
            self.stash_serial = 0
            logger.info(f"Created new stash for records with id '{self.stash_id}'") # nopep8

        logger.debug(f"adding {len(rows)} rows to stash {self.stash_id} as batch {self.stash_serial}...") # nopep8
        r = requests.put(
            self.url(f"stashes/{self.stash_id}/{self.stash_serial}"),
            headers=self.headers(),
            json=rows
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"failed to add rows batch for serial '{self.stash_serial}'. Response was '{r.text}'") from e  # nopep8

        logger.info(f"added {len(rows)} rows as batch for serial '{self.stash_serial}' successfully.")  # nopep8
        self.stash_serial += 1

    def create_table(self, name: str, columns: List[TableColumn]) -> None:
        logger.debug(f"creating table with columns: {columns}")
        if columns is None:
            raise ValueError("columns must be provided")
        if len(columns) == 0:
            raise ValueError("at least one column must be provided")

        logger.info(f"creating new table for table name '{name}' using stash {self.stash_id}...")  # nopep8
        r = requests.post(
            self.url(f"tables"),
            headers=self.headers(),
            json={
                "name": name,
                "schema": {
                    "columns": columns
                },
                "rows": {
                    "$stashID": self.stash_id
                }
            }
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"failed to create table '{name}'. Response was '{r.text}'.") from e  # nopep8

        logger.info(f"Creating table '{name}' succeeded.")
        self._reset_stash()
        return r.json()["data"]["tableID"]

    def overwrite_table(self, table_id: str, columns: List[TableColumn]) -> None:
        logger.debug(f"overwriting table with columns: {columns}")
        if columns is None:
            raise ValueError("columns must be provided")
        if len(columns) == 0:
            raise ValueError("at least one column must be provided")

        # overwrite (put) the specified table's schema and rows with the stash:
        r = requests.put(
            self.url(f"tables/{table_id}"),
            headers=self.headers(),
            json={
                "schema": {
                    "columns": columns,
                },
                "rows": {
                    "$stashID": self.stash_id
                }
            }
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"failed to overwrite table '{table_id}'. Response was '{r.text}'") from e  # nopep8

        logger.info(f"overwriting table '{table_id}' succeeded.")
        self._reset_stash()

    def list_tables(self) -> Iterator[Table]:
        r = requests.get(
            self.url(f"tables"),
            headers=self.headers()
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"failed to list tables. Response was '{r.text}'") from e

        result = r.json()
        for table in result["data"]:
            yield Table(table["id"], table["name"])
    
    def get_table(self, table_id: str) -> Table:
        raise NotImplementedError("get_table not implemented yet. Please implement this method when the `GET /tables/{id}` method is implemented at https://apidocs.glideapps.com.")  # nopep8
        r = requests.get(
            self.url(f"tables/{table_id}"),
            headers=self.headers()
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"failed to get table '{table_id}'. Response was '{r.text}'") from e

        result = r.json()
        return Table(result["data"]["id"], result["data"]["name"])


def handle_tables_command():
    glide = GlideApi()
    tables = glide.list_tables()
    for table in tables:
        print(table.json())

def handle_table_command(table_id):
    glide = GlideApi()
    table_details = glide.get_table(table_id)
    print(table_details)

def main():
    parser = argparse.ArgumentParser(description="Glide CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the "tables" command
    subparsers.add_parser("tables", help="List all tables")

    # Subparser for the "table" command
    table_parser = subparsers.add_parser("table", help="Get details of a specific table")
    table_parser.add_argument("table_id", type=str, help="The ID of the table")

    args = parser.parse_args()

    if args.command == "tables":
        handle_tables_command()
    elif args.command == "table":
        handle_table_command(args.table_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
