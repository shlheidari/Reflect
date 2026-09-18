export interface Memory {
  id: number
  text: string
}

export interface PaginatedMemories {
  count: number
  next: string | null
  previous: string | null
  results: Memory[]
}
