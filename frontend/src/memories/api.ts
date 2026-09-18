import { apiRequest, fetchAllPages } from '../lib/apiClient'
import type { Memory } from './types'

export function fetchMyMemories(): Promise<Memory[]> {
  return fetchAllPages<Memory>('/me/memories/')
}

export function reportMemory(memoryId: number): Promise<{ detail: string }> {
  return apiRequest<{ detail: string }>(`/memories/${memoryId}/report/`, {
    method: 'POST',
    body: {},
  })
}
