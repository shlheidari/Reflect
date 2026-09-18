import { apiRequest, fetchAllPages } from '../../lib/apiClient'
import type { AdminReport } from './types'

export function fetchAdminReports(): Promise<AdminReport[]> {
  return fetchAllPages<AdminReport>('/admin/reports/')
}

export function resolveAdminReport(id: number): Promise<AdminReport> {
  return apiRequest<AdminReport>(`/admin/reports/${id}/resolve/`, { method: 'POST' })
}

export function dismissAdminReport(id: number): Promise<AdminReport> {
  return apiRequest<AdminReport>(`/admin/reports/${id}/dismiss/`, { method: 'POST' })
}

export function hideAdminMemory(memoryId: number): Promise<{ detail: string }> {
  return apiRequest<{ detail: string }>(`/admin/memories/${memoryId}/hide/`, { method: 'POST' })
}

export function restoreAdminMemory(memoryId: number): Promise<{ detail: string }> {
  return apiRequest<{ detail: string }>(`/admin/memories/${memoryId}/restore/`, { method: 'POST' })
}
