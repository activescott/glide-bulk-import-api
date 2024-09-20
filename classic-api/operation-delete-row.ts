#!/usr/bin/env -S npx tsx

import {
  classicApiUrl,
  getApiToken,
  getAppAndTableFromEnvironment,
  MutationBody,
  MutationItemDeleteRow,
} from "./glide"

function mapRowsToMutations(
  rows: Record<string, any>[],
  tableName: string
): MutationItemDeleteRow[] {
  return rows.map((row) => {
    if (!row.$rowID) {
      throw new Error("Row must have a $rowID")
    }
    return {
      kind: "delete-row",
      tableName: tableName,
      rowID: row.$rowID,
    }
  })
}

async function deleteRows(
  apiKey: string,
  appID: string,
  tableName: string,
  rows: { $rowID: string }[]
): Promise<void> {
  const body: MutationBody = {
    appID: appID,
    mutations: mapRowsToMutations(rows, tableName),
  }

  console.info(`Deleting ${rows.length} rows in table ${tableName}...`)

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
    throw new Error(`Failed to delete rows: ${response.statusText}`)
  }

  console.info(`Deleting ${rows.length} rows in table ${tableName} succeeded.`)
}

async function main() {
  const apiKey = getApiToken()
  const { appID, tableName } = getAppAndTableFromEnvironment()

  // sample data
  const rows = [
    {
      $rowID: "18aEGOZfQL2yr4qv7tch5w",
    },
    {
      $rowID: "l0jgMyI4S.SrkaWeU89A9w",
    },
  ]

  await deleteRows(apiKey, appID, tableName, rows)
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
