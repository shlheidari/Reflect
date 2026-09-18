import { apiRequest } from '../../lib/apiClient'
import type { AdminStatistics } from './types'

export function fetchAdminStatistics(eventId: number): Promise<AdminStatistics> {
  return apiRequest<AdminStatistics>(`/admin/events/${eventId}/statistics/`)
}
