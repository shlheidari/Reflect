import { useMemo, useState } from 'react'
import { ParticipantCard } from '../participants/ParticipantCard'
import { useParticipants } from '../participants/useParticipants'

export function PeopleListPage() {
  const { data, isLoading, isError, refetch } = useParticipants()
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    const query = search.trim()
    if (!query) return data
    return data?.filter((participant) => participant.display_name.includes(query))
  }, [data, search])

  return (
    <div className="p-4 pb-24">
      <h1 className="text-xl font-bold text-gray-900">بچه‌ها</h1>

      {data && data.length > 5 && (
        <div className="relative mt-4">
          <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-gray-400">
            🔍
          </span>
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="جستجوی اسم..."
            aria-label="جستجوی شرکت‌کننده"
            className="w-full rounded-full border border-gray-200 bg-white py-2.5 pr-10 pl-4 text-sm placeholder:text-gray-400 focus:border-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10"
          />
        </div>
      )}

      <div className="mt-4">
        {isLoading && (
          <div className="space-y-3" aria-busy="true" aria-label="در حال بارگذاری">
            {[0, 1, 2, 3].map((key) => (
              <div key={key} className="h-20 animate-pulse rounded-2xl bg-gray-200" />
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

        {data && data.length === 0 && (
          <div className="rounded-2xl bg-white p-6 text-center text-gray-500">
            هنوز کسی برای ارزیابی ثبت نشده.
          </div>
        )}

        {data && data.length > 0 && filtered && filtered.length === 0 && (
          <div className="rounded-2xl bg-white p-6 text-center text-gray-500">
            کسی با این اسم پیدا نشد.
          </div>
        )}

        {filtered && filtered.length > 0 && (
          <div className="space-y-3">
            {filtered.map((participant) => (
              <ParticipantCard key={participant.id} participant={participant} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
