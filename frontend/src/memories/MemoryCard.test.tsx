import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { renderWithProviders } from '../test/test-utils'
import { MemoryCard } from './MemoryCard'
import type { Memory } from './types'
import { useReportMemory } from './useMemories'

vi.mock('./useMemories', () => ({
  useReportMemory: vi.fn(),
}))

const memory: Memory = { id: 5, text: 'یه خاطره قشنگ' }

describe('MemoryCard', () => {
  beforeEach(() => {
    vi.mocked(useReportMemory).mockReturnValue({
      mutateAsync: vi.fn().mockResolvedValue(undefined),
      isPending: false,
      isSuccess: false,
      isError: false,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any)
  })

  it('renders only the memory text — no author/evaluator identity of any kind', () => {
    const { container } = renderWithProviders(<MemoryCard memory={memory} />)

    expect(screen.getByText('یه خاطره قشنگ')).toBeInTheDocument()
    // Memory only ever carries {id, text} (apps.memories.serializers.MemorySerializer);
    // this guards against a future prop/field sneaking author info into the DOM.
    expect(container.textContent).not.toMatch(/(author|evaluator|username)/i)
  })

  it('requires a confirmation click before actually reporting', async () => {
    const user = userEvent.setup()
    const mutateAsync = vi.fn().mockResolvedValue(undefined)
    vi.mocked(useReportMemory).mockReturnValue({
      mutateAsync,
      isPending: false,
      isSuccess: false,
      isError: false,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any)

    renderWithProviders(<MemoryCard memory={memory} />)

    await user.click(screen.getByRole('button', { name: 'گزارش این خاطره' }))
    expect(mutateAsync).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: 'مطمئنی؟' }))
    await waitFor(() => expect(mutateAsync).toHaveBeenCalledWith(5))
  })

  it('shows a success message once reported', () => {
    vi.mocked(useReportMemory).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
      isSuccess: true,
      isError: false,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any)

    renderWithProviders(<MemoryCard memory={memory} />)
    expect(screen.getByText('گزارش شد ✓')).toBeInTheDocument()
  })
})
