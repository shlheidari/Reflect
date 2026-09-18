import { useState, type FormEvent } from 'react'
import { useAdminEvents, useUpdateAdminEvent } from '../../admin/events/useAdminEvents'
import type { AdminEvent, EventStatus } from '../../admin/events/types'
import { ApiError } from '../../lib/apiClient'

function toDatetimeLocal(value: string | null): string {
  if (!value) return ''
  // <input type="datetime-local"> wants "YYYY-MM-DDTHH:mm", no timezone/seconds.
  return value.slice(0, 16)
}

interface EventFormProps {
  event: AdminEvent
}

function EventForm({ event }: EventFormProps) {
  const updateEvent = useUpdateAdminEvent()

  const [name, setName] = useState(event.name)
  const [status, setStatus] = useState<EventStatus>(event.status)
  const [startAt, setStartAt] = useState(toDatetimeLocal(event.start_at))
  const [endAt, setEndAt] = useState(toDatetimeLocal(event.end_at))
  const [resultsEnabled, setResultsEnabled] = useState(event.results_enabled)
  const [memoriesEnabled, setMemoriesEnabled] = useState(event.memories_enabled)
  const [allowRatingEdit, setAllowRatingEdit] = useState(event.allow_rating_edit)
  const [minimumRatings, setMinimumRatings] = useState(String(event.minimum_ratings_for_results))
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSaved(false)

    try {
      await updateEvent.mutateAsync({
        id: event.id,
        payload: {
          name,
          status,
          start_at: startAt ? new Date(startAt).toISOString() : null,
          end_at: endAt ? new Date(endAt).toISOString() : null,
          results_enabled: resultsEnabled,
          memories_enabled: memoriesEnabled,
          allow_rating_edit: allowRatingEdit,
          minimum_ratings_for_results: Number(minimumRatings),
        },
      })
      setSaved(true)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'ذخیره نشد.')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl bg-white p-5 shadow-sm">
      <div>
        <label className="text-xs text-gray-500">نام رویداد</label>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
        />
      </div>

      <div>
        <label className="text-xs text-gray-500">وضعیت</label>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value as EventStatus)}
          className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
        >
          <option value="DRAFT">پیش‌نویس</option>
          <option value="OPEN">باز</option>
          <option value="CLOSED">بسته</option>
        </select>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label className="text-xs text-gray-500">زمان شروع</label>
          <input
            type="datetime-local"
            value={startAt}
            onChange={(e) => setStartAt(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-gray-500">زمان پایان</label>
          <input
            type="datetime-local"
            value={endAt}
            onChange={(e) => setEndAt(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
          />
        </div>
      </div>

      <div>
        <label className="text-xs text-gray-500">حداقل تعداد نظر برای نمایش نتیجه</label>
        <input
          type="number"
          min={1}
          value={minimumRatings}
          onChange={(e) => setMinimumRatings(e.target.value)}
          className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
        />
      </div>

      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={resultsEnabled}
            onChange={(e) => setResultsEnabled(e.target.checked)}
          />
          نمایش نتایج برای شرکت‌کننده‌ها فعال باشد
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={memoriesEnabled}
            onChange={(e) => setMemoriesEnabled(e.target.checked)}
          />
          امکان ثبت خاطره فعال باشد
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={allowRatingEdit}
            onChange={(e) => setAllowRatingEdit(e.target.checked)}
          />
          امکان ویرایش نظرات ثبت‌شده فعال باشد
        </label>
      </div>

      {error && <p className="text-xs text-red-600">{error}</p>}
      {saved && !updateEvent.isPending && <p className="text-xs text-emerald-600">ذخیره شد ✓</p>}

      <button
        type="submit"
        disabled={updateEvent.isPending}
        className="w-full rounded-full bg-gray-900 py-2.5 text-sm font-medium text-white disabled:opacity-50"
      >
        {updateEvent.isPending ? 'در حال ذخیره...' : 'ذخیره تنظیمات'}
      </button>
    </form>
  )
}

export function AdminEventPage() {
  const { data: events, isLoading, isError, refetch } = useAdminEvents()
  const [selectedEventId, setSelectedEventId] = useState<number | null>(null)

  const currentEventId = selectedEventId ?? events?.[0]?.id ?? null
  const currentEvent = events?.find((event) => event.id === currentEventId)

  return (
    <div className="mx-auto max-w-xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-bold text-gray-900">تنظیمات رویداد</h1>

        {events && events.length > 1 && (
          <select
            value={currentEventId ?? ''}
            onChange={(e) => setSelectedEventId(Number(e.target.value))}
            className="rounded-lg border border-gray-200 p-2 text-sm"
          >
            {events.map((event) => (
              <option key={event.id} value={event.id}>
                {event.name}
              </option>
            ))}
          </select>
        )}
      </div>

      <div className="mt-6">
        {isLoading && <div className="h-96 animate-pulse rounded-2xl bg-white/70" />}

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

        {events && events.length === 0 && (
          <div className="rounded-2xl bg-white p-6 text-center text-gray-500">
            هنوز رویدادی ایجاد نشده.
          </div>
        )}

        {currentEvent && <EventForm key={currentEvent.id} event={currentEvent} />}
      </div>
    </div>
  )
}
