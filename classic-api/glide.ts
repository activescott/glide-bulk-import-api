import path from "path"
import fs from "fs"
import { fileURLToPath } from "url"
import * as dotenv from "dotenv"
import { once } from "lodash-es"

export function classicApiUrl(
  resource: "queryTables" | "mutateTables"
): string {
  const API_ROOT = "https://api.glideapp.io/api/function"
  return `${API_ROOT}/${resource}`
}

export function getAppAndTableFromEnvironment(): {
  appID: string
  tableName: string
} {
  loadEnvironmentFilesOnce()
  const appID = process.env.GLIDE_APP_ID
  const tableName = process.env.GLIDE_TABLE_NAME
  if (!appID || !tableName) {
    throw new Error(
      "GLIDE_APP_ID or GLIDE_TABLE_NAME is not set in the environment."
    )
  }
  return { appID, tableName }
}

export function loadEnvironmentFiles(): void {
  const currentDir = path.dirname(fileURLToPath(import.meta.url))
  const dirs = [currentDir]
  const MAX_PARENT_DIRS = 3
  for (let i = 0; i < MAX_PARENT_DIRS; i++) {
    const parentDir = path.resolve(dirs[dirs.length - 1], "..")
    dirs.push(parentDir)
  }

  for (const dir of dirs) {
    const envFilePath = path.join(dir, ".env.secrets")
    if (fs.existsSync(envFilePath)) {
      dotenv.config({ path: envFilePath })
      console.info(`Loaded environment variables from ${envFilePath}`)
    }
  }
}

export const loadEnvironmentFilesOnce = once(loadEnvironmentFiles)

export function getApiToken(): string {
  loadEnvironmentFilesOnce()

  const apiKey = process.env.GLIDE_TOKEN
  if (!apiKey) {
    console.error("GLIDE_TOKEN is not set in the environment.")
    process.exit(1)
  }
  return apiKey
}

/**
 * Returns timestamp in the format of YYYYMMDDHHMMSSmmm as an integer
 */
export function timeStampInteger(): number {
  const now = new Date()
  const pad = (num: number, size: number) => num.toString().padStart(size, "0")
  return parseInt(
    `${now.getFullYear()}${pad(now.getMonth() + 1, 2)}${pad(
      now.getDate(),
      2
    )}${pad(now.getHours(), 2)}${pad(now.getMinutes(), 2)}${pad(
      now.getSeconds(),
      2
    )}${pad(now.getMilliseconds(), 3)}`
  )
}

//////// mutation api stuff:

export function mapColumnNameToID(
  columnIdToNameMap: Record<string, string>,
  columnName: string
): string {
  const mapNameToID: Record<string, string> = {}
  // perf: can be cached
  Object.keys(columnIdToNameMap).forEach((id) => {
    mapNameToID[columnIdToNameMap[id]] = id
  })
  return mapNameToID[columnName]
}

export function mapRowToMutationValues(
  row: Record<string, any>,
  colIdToNameMap: Record<string, string>
): any {
  const columnValues: Record<string, any> = {}
  for (const colId in colIdToNameMap) {
    const colName = colIdToNameMap[colId]
    columnValues[colId] = String(row[colName])
  }
  return columnValues
}

export type MutationItem =
  | MutationItemAddRow
  | MutationItemSetColumnsInRow
  | MutationItemDeleteRow

export interface MutationItemAddRow {
  kind: "add-row-to-table"
  tableName: string
  columnValues: Record<string, any>
}

export interface MutationItemSetColumnsInRow {
  kind: "set-columns-in-row"
  tableName: string
  columnValues: Record<string, any>
  rowID: string
}

export interface MutationItemDeleteRow {
  kind: "delete-row"
  tableName: string
  rowID: string
}

export interface MutationBody {
  appID: string
  mutations: MutationItem[]
}
