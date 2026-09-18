import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../lib/apiClient'
import { useAuth } from '../auth/authContext'
import { renderWithProviders } from '../test/test-utils'
import { LoginPage } from './LoginPage'

vi.mock('../auth/authContext', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../auth/authContext')>()
  return { ...actual, useAuth: vi.fn() }
})

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>()
  return { ...actual, useNavigate: () => mockNavigate }
})

describe('LoginPage', () => {
  beforeEach(() => {
    mockNavigate.mockReset()
  })

  it('submits the typed username/password to login() and navigates home on success', async () => {
    const login = vi.fn().mockResolvedValue(undefined)
    vi.mocked(useAuth).mockReturnValue({
      status: 'unauthenticated',
      user: null,
      error: null,
      login,
      logout: vi.fn(),
    })

    const user = userEvent.setup()
    renderWithProviders(<LoginPage />)

    await user.type(screen.getByLabelText('نام کاربری'), 'ali')
    await user.type(screen.getByLabelText('رمز عبور'), 'ali-pass-123')
    await user.click(screen.getByRole('button', { name: 'ورود' }))

    await waitFor(() => expect(login).toHaveBeenCalledWith('ali', 'ali-pass-123'))
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/', { replace: true }))
  })

  it('shows a generic error message on invalid credentials without leaking backend detail', async () => {
    const login = vi.fn().mockRejectedValue(new ApiError(401, 'Invalid credentials', 'invalid_credentials'))
    vi.mocked(useAuth).mockReturnValue({
      status: 'unauthenticated',
      user: null,
      error: null,
      login,
      logout: vi.fn(),
    })

    const user = userEvent.setup()
    renderWithProviders(<LoginPage />)

    await user.type(screen.getByLabelText('نام کاربری'), 'ali')
    await user.type(screen.getByLabelText('رمز عبور'), 'wrong-password')
    await user.click(screen.getByRole('button', { name: 'ورود' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('نام کاربری یا رمز عبور اشتباه است.')
    expect(mockNavigate).not.toHaveBeenCalled()
  })

  it('redirects away from /login when already authenticated', () => {
    vi.mocked(useAuth).mockReturnValue({
      status: 'authenticated',
      user: { id: 1, username: 'ali', is_staff: false, participant: null },
      error: null,
      login: vi.fn(),
      logout: vi.fn(),
    })

    renderWithProviders(<LoginPage />)
    expect(screen.queryByRole('button', { name: 'ورود' })).not.toBeInTheDocument()
  })
})
