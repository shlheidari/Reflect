import { apiRequest } from '../../lib/apiClient'
import type { AdminEvent, AdminEventCreatePayload, AdminEventUpdatePayload } from './types'

export function fetchAdminEvents(): Promise<AdminEvent[]> {
  return apiRequest<AdminEvent[]>('/admin/events/')
}

export function createAdminEvent(payload: AdminEventCreatePayload): Promise<AdminEvent> {
  return apiRequest<AdminEvent>('/admin/events/', { method: 'POST', body: payload })
}

export function updateAdminEvent(id: number, payload: AdminEventUpdatePayload): Promise<AdminEvent> {
  return apiRequest<AdminEvent>(`/admin/events/${id}/`, { method: 'PATCH', body: payload })
}
