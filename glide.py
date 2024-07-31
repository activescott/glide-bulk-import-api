from typing import Dict, Any, Iterator, List
import logging
import requests
import os

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

    def __eq__(self, other):
        if not isinstance(other, TableColumn):
            return False
        return dict(self) == dict(other)

    def __repr__(self):
        return f"Column(id='{self.id()}', type='{self.type()}')"


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
            r = requests.post(
                self.url(f"stashes"),
                headers=self.headers(),
            )
            try:
                r.raise_for_status()
            except Exception as e:
                raise Exception(f"failed to create stash. Response was '{r.text}'") from e # nopep8

            result = r.json()
            self.stash_id = result["data"]["stashID"]
            self.stash_serial = 0
            logger.info(f"Created new stash for records with id '{self.stash_id}'") # nopep8

        logger.debug(f"adding {len(rows)} rows to stash {self.stash_id} as batch {self.stash_serial}...") # nopep8
        r = requests.post(
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
