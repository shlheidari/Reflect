import { MemoryCard } from '../memories/MemoryCard'
import { useMyMemories } from '../memories/useMemories'
import { AboutMeTabs } from './AboutMeTabs'

export function MyMemoriesPage() {
  const { data, isLoading, isError, refetch } = useMyMemories()

  return (
    <div className="min-h-screen bg-gradient-to-b from-rose-50 to-gray-50 p-4 pb-24">
      <div className="mx-auto max-w-md">
        <div className="pt-4 text-center">
          <p className="text-3xl">❤️</p>
          <h1 className="mt-2 text-lg font-bold text-gray-900">خاطره‌ها درباره تو</h1>
          <p className="mt-1 text-sm text-gray-500">این خاطره‌ها به‌صورت ناشناس نمایش داده می‌شوند.</p>
        </div>

        <AboutMeTabs />

        <div className="mt-5 space-y-3">
          {isLoading &&
            [0, 1, 2].map((key) => (
              <div key={key} className="h-24 animate-pulse rounded-2xl bg-white/70" />
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

          {data && data.length === 0 && (
            <div className="rounded-2xl bg-white p-8 text-center">
              <p className="text-3xl">📭</p>
              <p className="mt-3 font-medium text-gray-900">هنوز خاطره‌ای درباره‌ات ثبت نشده</p>
              <p className="mt-1 text-sm text-gray-400">وقتی بقیه برات خاطره بنویسن، اینجا می‌بینیش.</p>
            </div>
          )}

          {data?.map((memory) => (
            <MemoryCard key={memory.id} memory={memory} />
          ))}
        </div>
      </div>
    </div>
  )
}
