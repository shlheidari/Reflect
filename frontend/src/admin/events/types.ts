export type EventStatus = 'DRAFT' | 'OPEN' | 'CLOSED'

export interface AdminEvent {
  id: number
  name: string
  status: EventStatus
  start_at: string | null
  end_at: string | null
  results_enabled: boolean
  memories_enabled: boolean
  allow_rating_edit: boolean
  minimum_ratings_for_results: number
  created_at: string
  updated_at: string
}

export interface AdminEventCreatePayload {
  name: string
  status?: EventStatus
}

export type AdminEventUpdatePayload = Partial<
  Omit<AdminEvent, 'id' | 'created_at' | 'updated_at'>
>
