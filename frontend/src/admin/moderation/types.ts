export type MemoryStatus = 'VISIBLE' | 'REPORTED' | 'HIDDEN'
export type ReportStatus = 'OPEN' | 'RESOLVED' | 'DISMISSED'

export interface AdminReportMemory {
  id: number
  text: string
  status: MemoryStatus
}

export interface AdminReport {
  id: number
  memory: AdminReportMemory
  reason: string
  status: ReportStatus
  created_at: string
  resolved_at: string | null
}

export interface PaginatedReports {
  count: number
  next: string | null
  previous: string | null
  results: AdminReport[]
}
