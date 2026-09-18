import { useMemo, useState, type FormEvent } from 'react'
import { ParticipantRow } from '../../admin/participants/ParticipantRow'
import { useAdminParticipants, useCreateAdminParticipant } from '../../admin/participants/useAdminParticipants'
import { useAdminEvents } from '../../admin/events/useAdminEvents'
import { ApiError } from '../../lib/apiClient'

export function AdminParticipantsPage() {
  const { data: events } = useAdminEvents()
  const { data: participants, isLoading, isError, refetch } = useAdminParticipants()
  const createParticipant = useCreateAdminParticipant()

  const [showCreate, setShowCreate] = useState(false)
  const [selectedEventId, setSelectedEventId] = useState<number | null>(null)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [createdPassword, setCreatedPassword] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  const currentEventId = selectedEventId ?? events?.[0]?.id ?? null

  const filteredParticipants = useMemo(() => {
    const query = search.trim().toLowerCase()
    if (!query) return participants
    return participants?.filter(
      (p) => p.display_name.toLowerCase().includes(query) || p.username.toLowerCase().includes(query),
    )
  }, [participants, search])

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    setFormError(null)
    setCreatedPassword(null)

    if (!currentEventId) {
      setFormError('ابتدا باید یک رویداد ایجاد شود.')
      return
    }

    try {
      const result = await createParticipant.mutateAsync({
        username,
        password: password || undefined,
        display_name: displayName,
        event: currentEventId,
      })
      setCreatedPassword(result.generated_password ?? null)
      setUsername('')
      setPassword('')
      setDisplayName('')
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'ذخیره نشد.')
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">شرکت‌کننده‌ها</h1>
        <button
          type="button"
          onClick={() => setShowCreate((v) => !v)}
          className="rounded-full bg-gray-900 px-4 py-2 text-sm font-medium text-white"
        >
          {showCreate ? 'بستن فرم' : '+ افزودن شرکت‌کننده'}
        </button>
      </div>

      {participants && participants.length > 5 && (
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="جستجو بر اساس نام یا نام کاربری..."
          aria-label="جستجوی شرکت‌کننده"
          className="mt-4 w-full rounded-xl border border-gray-200 p-2.5 text-sm focus:border-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10"
        />
      )}

      {showCreate && (
        <form onSubmit={handleCreate} className="mt-4 space-y-3 rounded-2xl bg-white p-4 shadow-sm">
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

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <label className="text-xs text-gray-500">نام نمایشی</label>
              <input
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                required
                className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500">نام کاربری</label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
              />
            </div>
          </div>

          <div>
            <label className="text-xs text-gray-500">رمز عبور (اختیاری — خالی بگذار تا خودکار ساخته شود)</label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-gray-200 p-2 text-sm"
            />
          </div>

          {formError && <p className="text-xs text-red-600">{formError}</p>}
          {createdPassword && (
            <p className="rounded-lg bg-amber-50 p-2 text-xs text-amber-800">
              شرکت‌کننده ساخته شد. رمز عبور: <span className="font-mono">{createdPassword}</span>
            </p>
          )}

          <button
            type="submit"
            disabled={createParticipant.isPending}
            className="w-full rounded-full bg-gray-900 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            ذخیره شرکت‌کننده
          </button>
        </form>
      )}

      <div className="mt-6 overflow-x-auto rounded-2xl bg-white shadow-sm">
        {isLoading && (
          <div className="space-y-3 p-4" aria-busy="true" aria-label="در حال بارگذاری">
            {[0, 1, 2].map((placeholder) => (
              <div key={placeholder} className="h-10 animate-pulse rounded-xl bg-gray-100" />
            ))}
          </div>
        )}

        {isError && (
          <div className="p-6 text-center text-gray-500">
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

        {participants && participants.length === 0 && (
          <div className="p-6 text-center text-gray-500">هنوز شرکت‌کننده‌ای ثبت نشده.</div>
        )}

        {participants && participants.length > 0 && filteredParticipants && filteredParticipants.length === 0 && (
          <div className="p-6 text-center text-gray-500">کسی با این مشخصات پیدا نشد.</div>
        )}

        {filteredParticipants && filteredParticipants.length > 0 && (
          <table className="w-full min-w-[640px] text-right">
            <thead>
              <tr className="border-b border-gray-100 text-xs text-gray-400">
                <th className="py-3 pl-3 font-medium">نام</th>
                <th className="py-3 pl-3 text-center font-medium">وضعیت</th>
                <th className="py-3 pl-3 text-center font-medium">آخرین ورود</th>
                <th className="py-3 pl-3 text-center font-medium">نظر داده</th>
                <th className="py-3 pl-3 text-center font-medium">نظر گرفته</th>
                <th className="py-3 font-medium">رمز عبور</th>
              </tr>
            </thead>
            <tbody>
              {filteredParticipants.map((participant) => (
                <ParticipantRow key={participant.id} participant={participant} />
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
