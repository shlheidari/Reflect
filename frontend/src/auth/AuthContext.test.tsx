import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { apiRequest, refreshAccessToken, setAccessToken } from '../lib/apiClient'
// Explicit ".tsx" extension needed: on this filesystem, an extension-less
// './AuthContext' import resolves ambiguously against the sibling
// './authContext.ts' (case-folding on the Windows-hosted bind mount) —
// main.tsx already sidesteps this the same way.
import { AuthProvider } from './AuthContext.tsx'
import { useAuth } from './authContext'

vi.mock('../lib/apiClient', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../lib/apiClient')>()
  return {
    ...actual,
    refreshAccessToken: vi.fn(),
    apiRequest: vi.fn(),
    setAccessToken: vi.fn(),
  }
})

function Probe() {
  const { status, user, error, login, logout } = useAuth()
  return (
    <div>
      <p data-testid="status">{status}</p>
      <p data-testid="username">{user?.username ?? ''}</p>
      <p data-testid="error">{error ?? ''}</p>
      <button onClick={() => login('ali', 'ali-pass-123').catch(() => {})}>login</button>
      <button onClick={() => logout().catch(() => {})}>logout</button>
    </div>
  )
}

describe('AuthProvider', () => {
  beforeEach(() => {
    vi.mocked(refreshAccessToken).mockReset()
    vi.mocked(apiRequest).mockReset()
    vi.mocked(setAccessToken).mockReset()
  })

  it('starts as unauthenticated when there is no valid refresh cookie', async () => {
    vi.mocked(refreshAccessToken).mockResolvedValue(null)

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'))
    expect(apiRequest).not.toHaveBeenCalled()
  })

  it('restores an authenticated session when the refresh cookie is still valid', async () => {
    vi.mocked(refreshAccessToken).mockResolvedValue('a-fresh-access-token')
    vi.mocked(apiRequest).mockResolvedValue({
      id: 7,
      username: 'sara',
      is_staff: false,
      participant: { id: 3, display_name: 'Sara', avatar: null, event: 1, is_active: true },
    })

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('authenticated'))
    expect(screen.getByTestId('username')).toHaveTextContent('sara')
    expect(apiRequest).toHaveBeenCalledWith('/me/')
  })

  it('logs in on demand and stores no password/token anywhere but the in-memory client', async () => {
    vi.mocked(refreshAccessToken).mockResolvedValue(null)
    vi.mocked(apiRequest).mockImplementation(async (path: string) => {
      if (path === '/auth/login/') {
        return {
          access: 'brand-new-access-token',
          user: { id: 1, username: 'ali', is_staff: false, participant: null },
        }
      }
      throw new Error(`unexpected path ${path}`)
    })

    const user = userEvent.setup()
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'))
    await user.click(screen.getByText('login'))

    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('authenticated'))
    expect(screen.getByTestId('username')).toHaveTextContent('ali')
    // The access token must go through setAccessToken (the in-memory-only
    // holder in lib/apiClient.ts) — never window/localStorage/sessionStorage.
    expect(setAccessToken).toHaveBeenCalledWith('brand-new-access-token')
    expect(window.localStorage.length).toBe(0)
    expect(window.sessionStorage.length).toBe(0)
  })

  it('surfaces a login failure as an error without authenticating', async () => {
    vi.mocked(refreshAccessToken).mockResolvedValue(null)
    vi.mocked(apiRequest).mockRejectedValue(new Error('bad credentials'))

    const user = userEvent.setup()
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'))
    await user.click(screen.getByText('login'))

    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'))
    expect(screen.getByTestId('username')).toHaveTextContent('')
  })

  it('clears local state on logout even if the network call fails', async () => {
    vi.mocked(refreshAccessToken).mockResolvedValue('token')
    vi.mocked(apiRequest).mockResolvedValueOnce({
      id: 1,
      username: 'ali',
      is_staff: false,
      participant: null,
    })

    const user = userEvent.setup()
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('authenticated'))

    vi.mocked(apiRequest).mockRejectedValueOnce(new Error('network down'))
    await act(async () => {
      await user.click(screen.getByText('logout'))
    })

    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'))
    expect(screen.getByTestId('username')).toHaveTextContent('')
    expect(setAccessToken).toHaveBeenCalledWith(null)
  })
})
