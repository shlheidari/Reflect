export interface RatingCategory {
  id: number
  key: string
  left_label: string
  right_label: string
  description: string
  order: number
  required: boolean
}

export interface RatingItem {
  category_id: number
  score: number
}

export interface RatingSubmitPayload {
  target_id: number
  ratings: RatingItem[]
  memory?: string
}

export interface RatingSubmitResponse {
  detail: string
  created: number
}

export interface ResultCategory {
  category_id: number
  left_label: string
  right_label: string
  average: number | null
  count: number
  has_enough_ratings: boolean
}

export interface MyResults {
  rating_count: number
  categories: ResultCategory[]
}
