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

/**
 * Maps a row to a mutation row item.
 * @param rows A "normal" row where keys are col names and values are values.
 * @param colIdToNameMap A map of column IDs to column names.
 * @param tableName Name of the table
 * @returns
 */
function mapRowsToMutations(
  rows: Record<string, any>[],
  colIdToNameMap: Record<string, string>,
  tableName: string
): MutationItem[] {
  return rows.map((row) => {
    return {
      kind: "add-row-to-table",
      tableName: tableName,
      columnValues: mapRowToMutationValues(row, colIdToNameMap),
    }
  })
}

async function addRows(
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

  console.info(`Adding ${rows.length} rows to table ${tableName}...`)

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
    throw new Error(`Failed to add a row: ${response.statusText}`)
  }

  console.info(`Adding ${rows.length} rows to table ${tableName} succeeded.`)
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
      orderid: timeStampInteger(),
      productid: 11,
      unitprice: 100,
      quantity: 2,
      discount: 0.1,
    },
    {
      orderid: timeStampInteger(),
      productid: 11,
      unitprice: 100,
      quantity: 2,
      discount: 0.1,
    },
  ]

  await addRows(apiKey, appID, tableName, colIdToNameMap, rows)
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
