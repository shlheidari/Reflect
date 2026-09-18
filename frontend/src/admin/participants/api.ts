import { apiRequest, fetchAllPages } from '../../lib/apiClient'
import type {
  AdminParticipant,
  AdminParticipantCreatePayload,
  AdminParticipantUpdatePayload,
  CreateParticipantResult,
  ResetPasswordPayload,
  ResetPasswordResult,
} from './types'

export function fetchAdminParticipants(): Promise<AdminParticipant[]> {
  return fetchAllPages<AdminParticipant>('/admin/participants/')
}

export function createAdminParticipant(
  payload: AdminParticipantCreatePayload,
): Promise<CreateParticipantResult> {
  return apiRequest<CreateParticipantResult>('/admin/participants/', {
    method: 'POST',
    body: payload,
  })
}

export function updateAdminParticipant(
  id: number,
  payload: AdminParticipantUpdatePayload,
): Promise<AdminParticipant> {
  return apiRequest<AdminParticipant>(`/admin/participants/${id}/`, {
    method: 'PATCH',
    body: payload,
  })
}

export function resetAdminParticipantPassword(
  id: number,
  payload: ResetPasswordPayload = {},
): Promise<ResetPasswordResult> {
  return apiRequest<ResetPasswordResult>(`/admin/participants/${id}/reset-password/`, {
    method: 'POST',
    body: payload,
  })
}
