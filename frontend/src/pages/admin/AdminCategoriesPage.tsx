import { useState, type FormEvent } from 'react'
import {
  useAdminCategories,
  useCreateAdminCategory,
  useReorderAdminCategories,
} from '../../admin/categories/useAdminCategories'
import { useAdminEvents } from '../../admin/events/useAdminEvents'
import { ApiError } from '../../lib/apiClient'
import { CategoryRow } from '../../admin/categories/CategoryRow'

export function AdminCategoriesPage() {
  const { data: events } = useAdminEvents()
  const { data: allCategories, isLoading, isError, refetch } = useAdminCategories()
  const createCategory = useCreateAdminCategory()
  const reorder = useReorderAdminCategories()

  const [showCreate, setShowCreate] = useState(false)
  const [selectedEventId, setSelectedEventId] = useState<number | null>(null)
  const [key, setKey] = useState('')
  const [leftLabel, setLeftLabel] = useState('')
  const [rightLabel, setRightLabel] = useState('')
  const [description, setDescription] = useState('')
  const [required, setRequired] = useState(true)
  const [formError, setFormError] = useState<string | null>(null)

  const currentEventId = selectedEventId ?? events?.[0]?.id ?? allCategories?.[0]?.event ?? null
  const categories = allCategories?.filter((category) => category.event === currentEventId)

  async function handleCreate(event: FormEvent) {
    event.preventDefault()
    setFormError(null)

    if (!currentEventId) {
      setFormError('ابتدا باید یک رویداد در پنل مدیریت جنگو ایجاد شود.')
      return
    }

    try {
      await createCategory.mutateAsync({
        event: currentEventId,
        key,
        left_label: leftLabel,
        right_label: rightLabel,
        description: description || undefined,
        required,
      })
      setKey('')
      setLeftLabel('')
      setRightLabel('')
      setDescription('')
      setRequired(true)
      setShowCreate(false)
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'ذخیره نشد.')
    }
  }

  function move(index: number, direction: -1 | 1) {
    if (!categories) return
    const target = index + direction
    if (target < 0 || target >= categories.length) return

    const ids = categories.map((category) => category.id)
    ;[ids[index], ids[target]] = [ids[target], ids[index]]
    reorder.mutate(ids)
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-xl font-bold text-gray-900">مدیریت دسته‌های امتیازدهی</h1>

      <button
          type="button"
          onClick={() => setShowCreate((v) => !v)}
          className="mt-4 rounded-full bg-gray-900 px-4 py-2 text-sm font-medium text-white"
        >
          {showCreate ? 'بستن فرم' : '+ افزودن دسته جدید'}
        </button>

        {showCreate && (
          <form
            onSubmit={handleCreate}
            className="mt-3 space-y-3 rounded-2xl bg-white p-4 shadow-sm"
          >
            {events && events.length > 1 && (
              <div>
                <label className="text-xs text-gray-500">رویداد</label>
                <select
                  value={currentEventId ?? ''}
                  onChange={(e) => setSelectedEventId(Number(e.target.value))}
                  className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
                >
                  {events.map((event) => (
                    <option key={event.id} value={event.id}>
                      {event.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div>
              <label className="text-xs text-gray-500">کلید (انگلیسی، مثل shift_behavior)</label>
              <input
                value={key}
                onChange={(e) => setKey(e.target.value)}
                required
                className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs text-gray-500">برچسب چپ (۰)</label>
                <input
                  value={leftLabel}
                  onChange={(e) => setLeftLabel(e.target.value)}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500">برچسب راست (۱۰)</label>
                <input
                  value={rightLabel}
                  onChange={(e) => setRightLabel(e.target.value)}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-gray-500">توضیح (اختیاری)</label>
              <input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
              />
            </div>

            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={required}
                onChange={(e) => setRequired(e.target.checked)}
              />
              اجباری
            </label>

            {formError && <p className="text-xs text-red-600">{formError}</p>}

            <button
              type="submit"
              disabled={createCategory.isPending}
              className="w-full rounded-full bg-gray-900 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              ذخیره دسته
            </button>
          </form>
        )}

        <div className="mt-6 space-y-3">
          {isLoading && (
            <div className="space-y-3" aria-busy="true" aria-label="در حال بارگذاری">
              {[0, 1, 2].map((placeholder) => (
                <div key={placeholder} className="h-32 animate-pulse rounded-2xl bg-gray-200" />
              ))}
            </div>
          )}

          {isError && (
            <div className="rounded-2xl bg-white p-6 text-center text-gray-500">
              <p>یه مشکلی پیش اومد.</p>
              <button
                type="button"
                onClick={() => refetch()}
                className="mt-3 text-sm font-medium text-gray-900 underline"
              >
                دوباره امتحان کن
              </button>
            </div>
          )}

          {categories && categories.length === 0 && (
            <div className="rounded-2xl bg-white p-6 text-center text-gray-500">
              هنوز دسته‌ای ثبت نشده.
            </div>
          )}

          {categories?.map((category, index) => (
            <CategoryRow
              key={category.id}
              category={category}
              isFirst={index === 0}
              isLast={index === categories.length - 1}
              reordering={reorder.isPending}
              onMoveUp={() => move(index, -1)}
              onMoveDown={() => move(index, 1)}
            />
          ))}
      </div>
    </div>
  )
}
