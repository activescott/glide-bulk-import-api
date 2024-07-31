from typing import Dict, Any, Iterator, List
from glide import TableRow
import random

api_base_url = 'https://api.glideapps.com'


def get_rows_with_suffix(suffix) -> List[TableRow]:
    return [
        {
            "fullName": f"Alex Bard {suffix}",
            "ageInYears": random.randint(15, 90),
            "hiredOn": "2021-07-03"
        },
        {
            "fullName": f"Alicia Hines {suffix}",
            "ageInYears": random.randint(15, 90),
            "hiredOn": "2023-01-015"
        }
    ]


def columns():
    return[
        {
            "id": "fullName",
            "displayName": "Name",
            #
            # NOTE: Schema expected to change here to "type": "string"
            #
            "type": {"kind": "string"}
        },
        {
            "id": "ageInYears",
            "displayName": "Age",
            "type": {"kind": "string"}
        },
        {
            "id": "hiredOn",
            "displayName": "Hire Date",
            "type": {"kind": "string"}
        }
    ]
