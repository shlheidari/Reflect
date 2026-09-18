import { apiRequest } from '../lib/apiClient'
import type { MyResults, RatingCategory, RatingSubmitPayload, RatingSubmitResponse } from './types'

export function fetchRatingCategories(): Promise<RatingCategory[]> {
  return apiRequest<RatingCategory[]>('/rating-categories/')
}

export function submitRating(payload: RatingSubmitPayload): Promise<RatingSubmitResponse> {
  return apiRequest<RatingSubmitResponse>('/ratings/', {
    method: 'POST',
    body: payload,
  })
}

export function fetchMyResults(): Promise<MyResults> {
  return apiRequest<MyResults>('/me/results/')
}
