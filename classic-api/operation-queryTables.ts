#!/usr/bin/env -S npx tsx

import {
  classicApiUrl,
  getApiToken,
  getAppAndTableFromEnvironment,
} from "./glide"

interface Query {
  tableName: string
  startAt?: string
}

interface RequestBody {
  appID: string
  queries: Query[]
}

interface Response {
  rows: any[]
  next?: string
}

async function fetchTableData(
  apiKey: string,
  appID: string,
  tableName: string,
  startAt?: string
): Promise<void> {
  console.info(
    `Fetching data from table ${tableName} with startAt ${
      startAt ?? "<none>"
    }...`
  )

  const body: RequestBody = {
    appID: appID,
    queries: [
      {
        tableName: tableName,
        startAt: startAt,
      },
    ],
  }

  const response = await fetch(classicApiUrl("queryTables"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  })

  const data: Response[] = await response.json()
  const rows = data[0].rows
  const next = data[0].next

  if (rows.length > 0) {
    const firstTwo = rows.slice(0, 2)
    const lastTwo = rows.slice(-2)
    console.info("First two rows:")
    console.dir(firstTwo)
    console.info("Last two rows:")
    console.dir(lastTwo)
  } else {
    console.info("No rows fetched")
  }

  console.info("Fetched", rows.length, "rows")
  console.info("Continuation token:", next)

  // If there's a continuation token, fetch the next set of rows
  if (next) {
    await fetchTableData(apiKey, appID, tableName, next)
  }
}

async function main() {
  const apiKey = getApiToken()
  const { appID, tableName } = getAppAndTableFromEnvironment()

  await fetchTableData(apiKey, appID, tableName)
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
