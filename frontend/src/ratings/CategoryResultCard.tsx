import type { ResultCategory } from './types'

interface CategoryResultCardProps {
  category: ResultCategory
}

export function CategoryResultCard({ category }: CategoryResultCardProps) {
  const { left_label, right_label, average, count, has_enough_ratings } = category
  const percent = average !== null ? Math.max(4, Math.min(100, (average / 10) * 100)) : 0

  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm">
      <p className="text-center font-bold text-gray-900">
        {left_label}
        <span className="mx-2 font-normal text-gray-300">←→</span>
        {right_label}
      </p>

      {has_enough_ratings && average !== null ? (
        <>
          <p className="mt-3 text-center text-3xl font-extrabold text-gray-900">
            {average}
            <span className="text-base font-medium text-gray-400"> / 10</span>
          </p>

          <div className="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-gray-100">
            {/* Anchored to the physical-right edge (where left_label / score 0
                sits) with ml-auto, so the fill grows leftward toward
                right_label as the score rises — matching CategorySlider's
                same left=0/right=10 convention. A plain width% div would
                otherwise hug the physical-left edge regardless of `dir`. */}
            <div
              className="ml-auto h-full rounded-full bg-gradient-to-l from-fuchsia-500 to-violet-500 transition-all"
              style={{ width: `${percent}%` }}
            />
          </div>

          <p className="mt-2 text-center text-xs text-gray-400">بر اساس {count} نظر</p>
        </>
      ) : (
        <div className="mt-4 flex flex-col items-center gap-1 py-1 text-center">
          <span className="text-2xl">🤫</span>
          <p className="text-sm text-gray-400">هنوز تعداد نظرات برای نمایش نتیجه کافی نیست.</p>
        </div>
      )}
    </div>
  )
}
