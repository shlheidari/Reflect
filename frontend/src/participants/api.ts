import { fetchAllPages } from '../lib/apiClient'
import type { ParticipantSummary } from './types'

export function fetchParticipants(): Promise<ParticipantSummary[]> {
  return fetchAllPages<ParticipantSummary>('/participants/')
}
