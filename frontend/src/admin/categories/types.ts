export interface AdminRatingCategory {
  id: number
  event: number
  key: string
  left_label: string
  right_label: string
  description: string
  order: number
  required: boolean
  active: boolean
  created_at: string
  updated_at: string
}

export interface RatingCategoryCreatePayload {
  event: number
  key: string
  left_label: string
  right_label: string
  description?: string
  required?: boolean
  active?: boolean
}

export type RatingCategoryUpdatePayload = Partial<
  Omit<RatingCategoryCreatePayload, 'event' | 'key'>
>
