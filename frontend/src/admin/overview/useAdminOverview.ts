import { useQuery } from '@tanstack/react-query'
import { fetchAdminStatistics } from './api'

export function useAdminStatistics(eventId: number | null) {
  return useQuery({
    queryKey: ['admin', 'statistics', eventId],
    queryFn: () => fetchAdminStatistics(eventId as number),
    enabled: eventId !== null,
  })
}
