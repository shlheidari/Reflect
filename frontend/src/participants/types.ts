export interface ParticipantSummary {
  id: number
  display_name: string
  avatar: string | null
  rating_count: number
  rated_by_me: boolean
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
