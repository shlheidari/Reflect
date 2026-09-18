import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchMyResults, fetchRatingCategories, submitRating } from './api'
import type { RatingSubmitPayload } from './types'

export function useRatingCategories() {
  return useQuery({ queryKey: ['rating-categories'], queryFn: fetchRatingCategories })
}

export function useMyResults() {
  return useQuery({ queryKey: ['my-results'], queryFn: fetchMyResults })
}

export function useSubmitRating() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: RatingSubmitPayload) => submitRating(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['participants'] })
    },
  })
}
