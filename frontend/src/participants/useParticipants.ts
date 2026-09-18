import { useQuery } from '@tanstack/react-query'
import { fetchParticipants } from './api'

export function useParticipants() {
  return useQuery({
    queryKey: ['participants'],
    queryFn: fetchParticipants,
  })
}
