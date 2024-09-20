#!/usr/bin/env -S npx tsx

import {
  classicApiUrl,
  getApiToken,
  getAppAndTableFromEnvironment,
  mapRowToMutationValues,
  MutationBody,
  MutationItem,
  timeStampInteger,
} from "./glide"

function mapRowsToMutations(
  rows: Record<string, any>[],
  colIdToNameMap: Record<string, string>,
  tableName: string
): MutationItem[] {
  return rows.map((row) => {
    if (!row.$rowID) {
      throw new Error("Row must have a $rowID")
    }
    return {
      kind: "set-columns-in-row",
      tableName: tableName,
      columnValues: mapRowToMutationValues(row, colIdToNameMap),
      rowID: row.$rowID,
    }
  })
}

async function editRow(
  apiKey: string,
  appID: string,
  tableName: string,
  colIdToNameMap: Record<string, string>,
  rows: Record<string, any>[]
): Promise<void> {
  const body: MutationBody = {
    appID: appID,
    mutations: mapRowsToMutations(rows, colIdToNameMap, tableName),
  }

  console.info(`Editing ${rows.length} rows in table ${tableName}...`)

  console.debug("Request body:")
  console.dir(body, { depth: null })

  const response = await fetch(classicApiUrl("mutateTables"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    throw new Error(`Failed to edit rows: ${response.statusText}`)
  }

  console.info(`Editing ${rows.length} rows in table ${tableName} succeeded.`)
}

async function main() {
  const apiKey = getApiToken()
  const { appID, tableName } = getAppAndTableFromEnvironment()

  // HACK hardcoded for our table:
  const colIdToNameMap = {
    uwqNY: "orderid",
    f8AyA: "productid",
    pML7G: "unitprice",
    JDkEm: "quantity",
    WxTof: "discount",
  } as Record<string, string>

  // create sample data
  const rows = [
    {
      $rowID: "YVP6auooRbK0nDIyexXUmg",
      orderid: 10248,
      productid: 11,
      unitprice: 14,
      quantity: 12,
      discount: timeStampInteger(),
    },
    {
      $rowID: "JZlxuXa8RHqqOB8HJKWxwQ",
      orderid: 10248,
      productid: 42,
      unitprice: 9.8,
      quantity: 10,
      discount: timeStampInteger(),
    },
  ]

  await editRow(apiKey, appID, tableName, colIdToNameMap, rows)
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
