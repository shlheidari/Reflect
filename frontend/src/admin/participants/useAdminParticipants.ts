import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  createAdminParticipant,
  fetchAdminParticipants,
  resetAdminParticipantPassword,
  updateAdminParticipant,
} from './api'
import type {
  AdminParticipantCreatePayload,
  AdminParticipantUpdatePayload,
  ResetPasswordPayload,
} from './types'

const PARTICIPANTS_KEY = ['admin', 'participants']

export function useAdminParticipants() {
  return useQuery({ queryKey: PARTICIPANTS_KEY, queryFn: fetchAdminParticipants })
}

export function useCreateAdminParticipant() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: AdminParticipantCreatePayload) => createAdminParticipant(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: PARTICIPANTS_KEY }),
  })
}

export function useUpdateAdminParticipant() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: AdminParticipantUpdatePayload }) =>
      updateAdminParticipant(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: PARTICIPANTS_KEY }),
  })
}

export function useResetAdminParticipantPassword() {
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload?: ResetPasswordPayload }) =>
      resetAdminParticipantPassword(id, payload),
  })
}
