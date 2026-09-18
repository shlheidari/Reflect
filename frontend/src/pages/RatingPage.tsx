import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ApiError } from '../lib/apiClient'
import { useParticipants } from '../participants/useParticipants'
import { CategorySlider } from '../ratings/CategorySlider'
import { useRatingCategories, useSubmitRating } from '../ratings/useRatings'

// Must match apps.memories.models.Memory.text's max_length on the backend.
const MEMORY_MAX_LENGTH = 2000

export function RatingPage() {
  const { targetId } = useParams()
  const navigate = useNavigate()
  const targetIdNum = Number(targetId)

  const { data: participants } = useParticipants()
  const target = participants?.find((p) => p.id === targetIdNum)

  const { data: categories, isLoading, isError, refetch } = useRatingCategories()
  const submitRating = useSubmitRating()

  const [scores, setScores] = useState<Record<number, number>>({})
  const [skipped, setSkipped] = useState<Set<number>>(new Set())
  const [touched, setTouched] = useState<Set<number>>(new Set())
  const [memoryText, setMemoryText] = useState('')
  const [confirming, setConfirming] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const total = categories?.length ?? 0
  const answered = categories?.filter((c) => touched.has(c.id) || skipped.has(c.id)).length ?? 0

  function scoreFor(categoryId: number) {
    return scores[categoryId] ?? 5
  }

  function handleChange(categoryId: number, value: number) {
    setScores((prev) => ({ ...prev, [categoryId]: value }))
    setTouched((prev) => new Set(prev).add(categoryId))
  }

  function toggleSkip(categoryId: number) {
    setSkipped((prev) => {
      const next = new Set(prev)
      if (next.has(categoryId)) next.delete(categoryId)
      else next.add(categoryId)
      return next
    })
  }

  async function handleConfirmSubmit() {
    if (!categories) return
    setSubmitError(null)
    const ratings = categories
      .filter((c) => !skipped.has(c.id))
      .map((c) => ({ category_id: c.id, score: scoreFor(c.id) }))

    try {
      await submitRating.mutateAsync({ target_id: targetIdNum, ratings, memory: memoryText })
      setConfirming(false)
    } catch (err) {
      setConfirming(false)
      setSubmitError(err instanceof ApiError ? err.message : 'ذخیره نشد.')
    }
  }

  if (submitRating.isSuccess) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-2 p-6 text-center">
        <p className="text-5xl">🎉</p>
        <p className="text-lg font-bold text-gray-900">
          نظرت درباره {target?.display_name ?? 'این شخص'} ثبت شد
        </p>
        <p className="text-sm text-gray-500">ممنون که وقت گذاشتی!</p>
        <button
          type="button"
          onClick={() => navigate('/people')}
          className="mt-4 rounded-full bg-gray-900 px-6 py-2.5 font-medium text-white"
        >
          بازگشت به لیست
        </button>
      </div>
    )
  }

  if (target?.rated_by_me) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-2 p-6 text-center">
        <p className="text-5xl">✓</p>
        <p className="font-bold text-gray-900">قبلاً درباره {target.display_name} نظر ثبت کردی</p>
        <Link to="/people" className="mt-4 rounded-full bg-gray-900 px-6 py-2.5 font-medium text-white">
          بازگشت به لیست
        </Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 pb-28">
      <div className="mx-auto max-w-md">
        <div className="flex items-center justify-between">
          <Link to="/people" className="text-sm text-gray-500 underline">
            برگرد
          </Link>
          <h1 className="font-bold text-gray-900">{target?.display_name ?? 'نظر بده'}</h1>
          <span className="w-10" />
        </div>

        {total > 0 && (
          <div className="mt-4">
            <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
              <div
                className="h-full rounded-full bg-gray-900 transition-all"
                style={{ width: `${Math.round((answered / total) * 100)}%` }}
              />
            </div>
            <p className="mt-1 text-xs text-gray-500">
              {answered} از {total}
            </p>
          </div>
        )}

        <div className="mt-4 space-y-3">
          {isLoading &&
            [0, 1, 2].map((key) => (
              <div key={key} className="h-28 animate-pulse rounded-2xl bg-gray-200" />
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

          {categories?.map((category) => (
            <CategorySlider
              key={category.id}
              category={category}
              value={scoreFor(category.id)}
              skipped={skipped.has(category.id)}
              onChange={(value) => handleChange(category.id, value)}
              onToggleSkip={() => toggleSkip(category.id)}
            />
          ))}

          {categories && categories.length > 0 && (
            <div className="rounded-2xl bg-white p-4 shadow-sm">
              <p className="font-bold text-gray-900">
                یه خاطره از {target?.display_name ?? 'این شخص'} داری؟ 👀
              </p>
              <textarea
                value={memoryText}
                onChange={(e) => setMemoryText(e.target.value)}
                maxLength={MEMORY_MAX_LENGTH}
                rows={4}
                placeholder="یه خاطره یا حرف دلت رو بنویس... (اختیاری)"
                className="mt-3 w-full resize-none rounded-xl border border-gray-200 p-3 text-sm text-gray-900 placeholder:text-gray-400 focus:border-fuchsia-400 focus:outline-none focus:ring-2 focus:ring-fuchsia-500/20"
              />
              <div className="mt-1.5 flex items-center justify-between">
                <p className="text-xs text-gray-400">این بخش ناشناس نمایش داده میشه.</p>
                <p className="shrink-0 text-xs text-gray-300">
                  {memoryText.length}/{MEMORY_MAX_LENGTH}
                </p>
              </div>
            </div>
          )}
        </div>

        {submitError && <p className="mt-3 text-center text-sm text-red-600">{submitError}</p>}
      </div>

      {categories && categories.length > 0 && (
        <div className="fixed inset-x-0 bottom-0 border-t border-gray-200 bg-white p-4">
          <div className="mx-auto max-w-md">
            <button
              type="button"
              onClick={() => setConfirming(true)}
              className="w-full rounded-full bg-gray-900 py-3 font-medium text-white"
            >
              ثبت نظر
            </button>
          </div>
        </div>
      )}

      {confirming && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-sm rounded-2xl bg-white p-5 text-center">
            <p className="font-bold text-gray-900">آماده‌ای نظرت رو ثبت کنی؟</p>
            <p className="mt-2 text-sm text-gray-500">
              بعد از ثبت، طبق تنظیمات جشن ممکنه امکان ویرایش وجود داشته باشه.
            </p>
            <div className="mt-4 flex gap-2">
              <button
                type="button"
                onClick={() => setConfirming(false)}
                className="flex-1 rounded-full bg-gray-100 py-2.5 font-medium text-gray-700"
              >
                برگرد
              </button>
              <button
                type="button"
                onClick={handleConfirmSubmit}
                disabled={submitRating.isPending}
                className="flex-1 rounded-full bg-gray-900 py-2.5 font-medium text-white disabled:opacity-50"
              >
                {submitRating.isPending ? 'در حال ثبت...' : 'ثبت نظر'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
