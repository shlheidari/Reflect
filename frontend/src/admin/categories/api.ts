import { apiRequest } from '../../lib/apiClient'
import type { AdminRatingCategory, RatingCategoryCreatePayload, RatingCategoryUpdatePayload } from './types'

export function fetchAdminCategories(): Promise<AdminRatingCategory[]> {
  return apiRequest<AdminRatingCategory[]>('/admin/rating-categories/')
}

export function createAdminCategory(
  payload: RatingCategoryCreatePayload,
): Promise<AdminRatingCategory> {
  return apiRequest<AdminRatingCategory>('/admin/rating-categories/', {
    method: 'POST',
    body: payload,
  })
}

export function updateAdminCategory(
  id: number,
  payload: RatingCategoryUpdatePayload,
): Promise<AdminRatingCategory> {
  return apiRequest<AdminRatingCategory>(`/admin/rating-categories/${id}/`, {
    method: 'PATCH',
    body: payload,
  })
}

export function reorderAdminCategories(ids: number[]): Promise<AdminRatingCategory[]> {
  return apiRequest<AdminRatingCategory[]>('/admin/rating-categories/reorder/', {
    method: 'POST',
    body: { ids },
  })
}
