import { useState } from 'react'
import { useAdminEvents } from '../../admin/events/useAdminEvents'
import type { AdminStatistics } from '../../admin/overview/types'
import { useAdminStatistics } from '../../admin/overview/useAdminOverview'

const cards: Array<{ key: keyof AdminStatistics; label: string; icon: string; suffix?: string }> = [
  { key: 'total_participants', label: 'کل شرکت‌کننده‌ها', icon: '👥' },
  { key: 'active_participants', label: 'شرکت‌کننده‌های فعال', icon: '✅' },
  { key: 'participants_logged_in', label: 'وارد شده‌اند', icon: '🔑' },
  { key: 'participants_rated', label: 'نظر داده‌اند', icon: '📝' },
  { key: 'total_ratings', label: 'کل نظرات ثبت‌شده', icon: '⭐' },
  { key: 'total_memories', label: 'کل خاطره‌ها', icon: '❤️' },
  { key: 'average_ratings_per_participant', label: 'میانگین نظر به ازای هرنفر', icon: '📊' },
  { key: 'participation_percentage', label: 'درصد مشارکت', icon: '🎯', suffix: '٪' },
]

export function AdminOverviewPage() {
  const { data: events, isLoading: eventsLoading } = useAdminEvents()
  const [selectedEventId, setSelectedEventId] = useState<number | null>(null)
  const currentEventId = selectedEventId ?? events?.[0]?.id ?? null

  const { data: stats, isLoading, isError, refetch } = useAdminStatistics(currentEventId)

  return (
    <div className="mx-auto max-w-4xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-bold text-gray-900">نمای کلی</h1>

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

      {!eventsLoading && events && events.length === 0 && (
        <div className="mt-6 rounded-2xl bg-white p-6 text-center text-gray-500">
          هنوز رویدادی ایجاد نشده.
        </div>
      )}

      {(isLoading || eventsLoading) && (
        <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
          {Array.from({ length: 8 }).map((_, index) => (
            <div key={index} className="h-24 animate-pulse rounded-2xl bg-white/70" />
          ))}
        </div>
      )}

      {isError && (
        <div className="mt-6 rounded-2xl bg-white p-6 text-center text-gray-500">
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

      {stats && (
        <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
          {cards.map((card) => (
            <div key={card.key} className="rounded-2xl bg-white p-4 shadow-sm">
              <p className="text-2xl">{card.icon}</p>
              <p className="mt-2 text-2xl font-extrabold text-gray-900">
                {stats[card.key]}
                {card.suffix ?? ''}
              </p>
              <p className="mt-1 text-xs text-gray-500">{card.label}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
