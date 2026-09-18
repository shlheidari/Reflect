import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createAdminEvent, fetchAdminEvents, updateAdminEvent } from './api'
import type { AdminEventCreatePayload, AdminEventUpdatePayload } from './types'

const EVENTS_KEY = ['admin', 'events']

export function useAdminEvents() {
  return useQuery({ queryKey: EVENTS_KEY, queryFn: fetchAdminEvents })
}

export function useCreateAdminEvent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: AdminEventCreatePayload) => createAdminEvent(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: EVENTS_KEY }),
  })
}

export function useUpdateAdminEvent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: AdminEventUpdatePayload }) =>
      updateAdminEvent(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: EVENTS_KEY }),
  })
}
