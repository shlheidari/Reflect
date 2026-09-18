import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CategoryResultCard } from './CategoryResultCard'
import type { ResultCategory } from './types'

const category: ResultCategory = {
  category_id: 1,
  left_label: 'خوش‌کشیک',
  right_label: 'بدکشیک',
  average: 7.4,
  count: 18,
  has_enough_ratings: true,
}

describe('CategoryResultCard', () => {
  it('shows the aggregate average and count', () => {
    render(<CategoryResultCard category={category} />)

    expect(screen.getByText('7.4')).toBeInTheDocument()
    expect(screen.getByText('بر اساس 18 نظر')).toBeInTheDocument()
  })

  it('shows a locked placeholder instead of a score when there are not enough ratings', () => {
    render(<CategoryResultCard category={{ ...category, has_enough_ratings: false, average: null }} />)

    expect(screen.getByText('هنوز تعداد نظرات برای نمایش نتیجه کافی نیست.')).toBeInTheDocument()
    expect(screen.queryByText('7.4')).not.toBeInTheDocument()
  })

  it('never renders any individual score or evaluator identity — only the aggregate fields on ResultCategory', () => {
    const { container } = render(<CategoryResultCard category={category} />)
    // docs/PRIVACY.md #8: results are aggregate-only. ResultCategory itself
    // carries no evaluator/individual-score fields, so this guards against a
    // future prop change accidentally introducing one.
    expect(container.textContent).not.toMatch(/(evaluator|username)/i)
  })
})
