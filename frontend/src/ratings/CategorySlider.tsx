import type { RatingCategory } from './types'

interface CategorySliderProps {
  category: RatingCategory
  value: number
  skipped: boolean
  onChange: (value: number) => void
  onToggleSkip: () => void
}

export function CategorySlider({ category, value, skipped, onChange, onToggleSkip }: CategorySliderProps) {
  return (
    <div
      className={`rounded-2xl bg-white p-4 shadow-sm transition-opacity ${skipped ? 'opacity-50' : ''}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="font-bold text-gray-900">
            {category.left_label}
            <span className="mx-1 font-normal text-gray-300">↔</span>
            {category.right_label}
          </p>
          {category.description && (
            <p className="mt-0.5 text-xs text-gray-400">{category.description}</p>
          )}
        </div>

        {!category.required && (
          <button
            type="button"
            onClick={onToggleSkip}
            className="shrink-0 rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-500"
          >
            {skipped ? 'افزودن نظر' : 'رد شدن'}
          </button>
        )}
      </div>

      {!skipped && (
        <div className="mt-4">
          <div className="flex justify-center">
            <span className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-l from-fuchsia-600 to-violet-600 text-2xl font-bold text-white transition-transform">
              {value}
            </span>
          </div>

          <input
            type="range"
            min={0}
            max={10}
            step={1}
            value={value}
            onChange={(e) => onChange(Number(e.target.value))}
            aria-label={`${category.left_label} تا ${category.right_label}`}
            aria-valuetext={`${value} از ۱۰`}
            className="mt-3 w-full accent-fuchsia-600"
          />

          <div className="mt-1 flex justify-between text-xs text-gray-500">
            <span>{category.left_label}</span>
            <span>{category.right_label}</span>
          </div>
        </div>
      )}
    </div>
  )
}
