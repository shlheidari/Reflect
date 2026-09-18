import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  dismissAdminReport,
  fetchAdminReports,
  hideAdminMemory,
  resolveAdminReport,
  restoreAdminMemory,
} from './api'

const REPORTS_KEY = ['admin', 'reports']

export function useAdminReports() {
  return useQuery({ queryKey: REPORTS_KEY, queryFn: fetchAdminReports })
}

export function useResolveReport() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => resolveAdminReport(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: REPORTS_KEY }),
  })
}

export function useDismissReport() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => dismissAdminReport(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: REPORTS_KEY }),
  })
}

export function useHideMemory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (memoryId: number) => hideAdminMemory(memoryId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: REPORTS_KEY }),
  })
}

export function useRestoreMemory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (memoryId: number) => restoreAdminMemory(memoryId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: REPORTS_KEY }),
  })
}
