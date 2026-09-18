import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createAdminCategory, fetchAdminCategories, reorderAdminCategories, updateAdminCategory } from './api'
import type { RatingCategoryCreatePayload, RatingCategoryUpdatePayload } from './types'

const CATEGORIES_KEY = ['admin', 'rating-categories']

export function useAdminCategories() {
  return useQuery({ queryKey: CATEGORIES_KEY, queryFn: fetchAdminCategories })
}

export function useCreateAdminCategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: RatingCategoryCreatePayload) => createAdminCategory(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: CATEGORIES_KEY }),
  })
}

export function useUpdateAdminCategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: RatingCategoryUpdatePayload }) =>
      updateAdminCategory(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: CATEGORIES_KEY }),
  })
}

export function useReorderAdminCategories() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (ids: number[]) => reorderAdminCategories(ids),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: CATEGORIES_KEY }),
  })
}
