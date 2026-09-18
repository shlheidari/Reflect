import { CategoryResultCard } from '../ratings/CategoryResultCard'
import { useMyResults } from '../ratings/useRatings'
import { AboutMeTabs } from './AboutMeTabs'

export function MyResultsPage() {
  const { data, isLoading, isError, refetch } = useMyResults()

  return (
    <div className="min-h-screen bg-gradient-to-b from-fuchsia-50 to-gray-50 p-4 pb-24">
      <div className="mx-auto max-w-md">
        <div className="pt-4 text-center">
          <p className="text-3xl">👀</p>
          <h1 className="mt-2 text-lg font-bold text-gray-900">درباره تو چی فکر می‌کنن؟</h1>
          {data && (
            <p className="mt-1 text-sm text-gray-500">
              {data.rating_count > 0 ? `${data.rating_count} نفر بهت نظر دادن` : 'هنوز کسی نظر نداده'}
            </p>
          )}
        </div>

        <AboutMeTabs />

        <div className="mt-5 space-y-3">
          {isLoading &&
            [0, 1, 2].map((key) => (
              <div key={key} className="h-28 animate-pulse rounded-2xl bg-white/70" />
            ))}

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

          {data && data.rating_count === 0 && (
            <div className="rounded-2xl bg-white p-8 text-center">
              <p className="text-3xl">🌱</p>
              <p className="mt-3 font-medium text-gray-900">هنوز کسی درباره‌ات نظر نداده</p>
              <p className="mt-1 text-sm text-gray-400">به بقیه هم یادآوری کن نظر بدن!</p>
            </div>
          )}

          {data &&
            data.rating_count > 0 &&
            data.categories.map((category) => (
              <CategoryResultCard key={category.category_id} category={category} />
            ))}
        </div>
      </div>
    </div>
  )
}
