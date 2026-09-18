import { useMutation, useQuery } from '@tanstack/react-query'
import { fetchMyMemories, reportMemory } from './api'

export function useMyMemories() {
  return useQuery({ queryKey: ['my-memories'], queryFn: fetchMyMemories })
}

export function useReportMemory() {
  return useMutation({
    mutationFn: (memoryId: number) => reportMemory(memoryId),
  })
}
