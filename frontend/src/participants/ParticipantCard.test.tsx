import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderWithProviders } from '../test/test-utils'
import { ParticipantCard } from './ParticipantCard'
import type { ParticipantSummary } from './types'

const base: ParticipantSummary = {
  id: 42,
  display_name: 'Ali Rezaei',
  avatar: null,
  rating_count: 18,
  rated_by_me: false,
}

describe('ParticipantCard', () => {
  it('shows the name and rating count, with a rate link when not yet rated', () => {
    renderWithProviders(<ParticipantCard participant={base} />)

    expect(screen.getByText('Ali Rezaei')).toBeInTheDocument()
    expect(screen.getByText('18 نظر ثبت شده')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'نظر بده' })).toHaveAttribute('href', '/rate/42')
  })

  it('shows a checkmark badge instead of a rate link once already rated', () => {
    renderWithProviders(<ParticipantCard participant={{ ...base, rated_by_me: true }} />)

    expect(screen.getByText('✓ نظر ثبت شده')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'نظر بده' })).not.toBeInTheDocument()
  })

  it('never renders any evaluator-identifying data — only fields present in ParticipantSummary', () => {
    const { container } = renderWithProviders(<ParticipantCard participant={base} />)
    // Privacy floor: this card must only ever show data present on
    // ParticipantSummary (docs/PRIVACY.md). Guards against a future edit
    // accidentally passing/rendering an evaluator id or username here.
    expect(container.textContent).not.toMatch(/evaluator/i)
  })
})
