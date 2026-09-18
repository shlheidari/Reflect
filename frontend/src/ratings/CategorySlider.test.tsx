import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { CategorySlider } from './CategorySlider'
import type { RatingCategory } from './types'

const category: RatingCategory = {
  id: 1,
  key: 'good_shift',
  left_label: 'خوش‌کشیک',
  right_label: 'بدکشیک',
  description: '',
  order: 1,
  required: false,
}

describe('CategorySlider', () => {
  it('shows both endpoint labels and the current value', () => {
    render(
      <CategorySlider category={category} value={7} skipped={false} onChange={vi.fn()} onToggleSkip={vi.fn()} />,
    )

    expect(screen.getByText('خوش‌کشیک')).toBeInTheDocument()
    expect(screen.getByText('بدکشیک')).toBeInTheDocument()
    expect(screen.getByText('7')).toBeInTheDocument()
  })

  it('calls onChange with the new numeric value when the slider moves', () => {
    const onChange = vi.fn()
    render(
      <CategorySlider category={category} value={5} skipped={false} onChange={onChange} onToggleSkip={vi.fn()} />,
    )

    fireEvent.change(screen.getByRole('slider'), { target: { value: '9' } })
    expect(onChange).toHaveBeenCalledWith(9)
  })

  it('hides the slider and calls onToggleSkip when skipped for an optional category', () => {
    const onToggleSkip = vi.fn()
    render(
      <CategorySlider category={category} value={5} skipped={false} onChange={vi.fn()} onToggleSkip={onToggleSkip} />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'رد شدن' }))
    expect(onToggleSkip).toHaveBeenCalled()
  })

  it('does not render a skip button for a required category', () => {
    render(
      <CategorySlider
        category={{ ...category, required: true }}
        value={5}
        skipped={false}
        onChange={vi.fn()}
        onToggleSkip={vi.fn()}
      />,
    )

    expect(screen.queryByRole('button', { name: 'رد شدن' })).not.toBeInTheDocument()
  })
})
