import { useState } from 'react'
import { ApiError } from '../../lib/apiClient'
import type { AdminRatingCategory } from './types'
import { useUpdateAdminCategory } from './useAdminCategories'

interface CategoryRowProps {
  category: AdminRatingCategory
  isFirst: boolean
  isLast: boolean
  reordering: boolean
  onMoveUp: () => void
  onMoveDown: () => void
}

export function CategoryRow({
  category,
  isFirst,
  isLast,
  reordering,
  onMoveUp,
  onMoveDown,
}: CategoryRowProps) {
  const updateCategory = useUpdateAdminCategory()
  const [leftLabel, setLeftLabel] = useState(category.left_label)
  const [rightLabel, setRightLabel] = useState(category.right_label)
  const [description, setDescription] = useState(category.description)
  const [error, setError] = useState<string | null>(null)

  const dirty =
    leftLabel !== category.left_label ||
    rightLabel !== category.right_label ||
    description !== category.description

  async function handleSave() {
    setError(null)
    try {
      await updateCategory.mutateAsync({
        id: category.id,
        payload: { left_label: leftLabel, right_label: rightLabel, description },
      })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'ذخیره نشد.')
    }
  }

  async function toggleActive() {
    setError(null)
    try {
      await updateCategory.mutateAsync({ id: category.id, payload: { active: !category.active } })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'ذخیره نشد.')
    }
  }

  async function toggleRequired() {
    setError(null)
    try {
      await updateCategory.mutateAsync({
        id: category.id,
        payload: { required: !category.required },
      })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'ذخیره نشد.')
    }
  }

  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-xs text-gray-400">{category.key}</span>
        <div className="flex gap-1">
          <button
            type="button"
            onClick={onMoveUp}
            disabled={isFirst || reordering}
            className="rounded-lg bg-gray-100 px-2 py-1 text-sm disabled:opacity-30"
          >
            ▲
          </button>
          <button
            type="button"
            onClick={onMoveDown}
            disabled={isLast || reordering}
            className="rounded-lg bg-gray-100 px-2 py-1 text-sm disabled:opacity-30"
          >
            ▼
          </button>
        </div>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2">
        <div>
          <label className="text-xs text-gray-500">برچسب چپ (۰)</label>
          <input
            value={leftLabel}
            onChange={(e) => setLeftLabel(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-gray-500">برچسب راست (۱۰)</label>
          <input
            value={rightLabel}
            onChange={(e) => setRightLabel(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
          />
        </div>
      </div>

      <div className="mt-2">
        <label className="text-xs text-gray-500">توضیح (اختیاری)</label>
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
        />
      </div>

      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}

      <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={toggleActive}
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              category.active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
            }`}
          >
            {category.active ? 'فعال' : 'غیرفعال'}
          </button>
          <button
            type="button"
            onClick={toggleRequired}
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              category.required ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'
            }`}
          >
            {category.required ? 'اجباری' : 'اختیاری'}
          </button>
        </div>

        <button
          type="button"
          onClick={handleSave}
          disabled={!dirty || updateCategory.isPending}
          className="rounded-full bg-gray-900 px-4 py-1.5 text-xs font-medium text-white disabled:opacity-30"
        >
          ذخیره
        </button>
      </div>
    </div>
  )
}
