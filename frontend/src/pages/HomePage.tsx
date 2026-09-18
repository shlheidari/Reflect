import { Link } from 'react-router-dom'
import { useAuth } from '../auth/authContext'
import { useParticipants } from '../participants/useParticipants'

export function HomePage() {
  const { user } = useAuth()
  const name = user?.participant?.display_name ?? user?.username ?? ''

  const { data: participants, isLoading } = useParticipants()
  const total = participants?.length ?? 0
  const ratedCount = participants?.filter((p) => p.rated_by_me).length ?? 0
  const percent = total > 0 ? Math.round((ratedCount / total) * 100) : 0
  const allRated = total > 0 && ratedCount === total

  return (
    <div className="p-4 pb-24">
      <h1 className="text-xl font-bold text-gray-900">سلام، {name} 👋</h1>

      {isLoading && <div className="mt-4 h-20 animate-pulse rounded-2xl bg-gray-200" />}

      {!isLoading && total === 0 && (
        <p className="mt-2 text-gray-500">هنوز کسی برای ارزیابی ثبت نشده.</p>
      )}

      {!isLoading && total > 0 && allRated && (
        <div className="mt-4 rounded-2xl bg-gradient-to-l from-fuchsia-50 to-violet-50 p-5 text-center">
          <p className="text-3xl">🎉</p>
          <p className="mt-2 font-bold text-gray-900">همه رو ارزیابی کردی!</p>
          <p className="mt-1 text-sm text-gray-500">حالا وقتشه ببینی بقیه درباره خودت چی گفتن 👀</p>
        </div>
      )}

      {!isLoading && total > 0 && !allRated && (
        <>
          <p className="mt-2 text-gray-500">چقدر از بچه‌ها رو ارزیابی کردی؟</p>
          <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full rounded-full bg-gradient-to-l from-fuchsia-500 to-violet-500 transition-all"
              style={{ width: `${percent}%` }}
            />
          </div>
          <p className="mt-2 text-sm text-gray-500">
            {ratedCount} از {total} نفر
          </p>
        </>
      )}

      <div className="mt-6 space-y-3">
        <Link
          to="/people"
          className="block rounded-2xl bg-gray-900 p-4 text-center font-medium text-white transition-transform active:scale-[0.98]"
        >
          {allRated ? 'مرور دوباره لیست بچه‌ها' : 'نظر دادن درباره بچه‌ها'}
        </Link>
        <Link
          to="/results"
          className="block rounded-2xl bg-white p-4 text-center font-medium text-gray-900 shadow-sm transition-transform active:scale-[0.98]"
        >
          ببین بقیه درباره من چی گفتن
        </Link>
      </div>
    </div>
  )
}
