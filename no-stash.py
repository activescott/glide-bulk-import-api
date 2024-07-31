import os
import random
import requests

api_base_url = 'https://api.glideapps.com'

def headers():
    token = os.getenv('GLIDE_TOKEN')
    if not token:
        raise Exception("Please set the GLIDE_TOKEN environment variable")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    return headers


def schema():
    return {
        "columns": [
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
    }


def create_table():
    url = f"{api_base_url}/tables"

    payload = {

        "name": "Employees",
        "schema": schema(),
        "rows": [
            {
                "fullName": "Alex Fard",
                "ageInYears": 30,
                "hiredOn": "2021-07-03"
            },
            {
                "fullName": "Alicia Fines",
                "ageInYears": 34,
                "hiredOn": "2023-01-15"
            }
        ]

    }
    response = requests.request("POST", url, json=payload, headers=headers())
    json = response.json()
    print("Create Table Response:", json["data"])

    return json["data"]["tableID"]
    


def overwrite_table(tableID, rows):
    url = f"{api_base_url}/{tableID}"

    payload = {
        "rows": rows
    }
    response = requests.request("PUT", url, json=payload, headers=headers())
    response.raise_for_status()

    json = response.json()
    print("Overwrite response:", json)
    

if __name__ == "__main__":
    # Create the table if it doesn't exist:
    table_id = create_table()
    print(f"Table ID: {table_id}")

    exit(0)
    #
    # TODO: CHANGE THE tableID to your table ID
    #

    tableID = "dcb3a2fa-4efd-454b-b124-7fbf7b5cb010"
    rows = [
        {
            "fullName": "Alex Bard",
            "ageInYears": random.randint(15, 90),
            "hiredOn": "2021-07-03"
        },
        {
            "fullName": "Alicia Hines",
            "ageInYears": random.randint(15, 90),
            "hiredOn": "2023-01-015"
        }
    ]
    overwrite_table(tableID, rows)
