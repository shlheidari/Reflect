import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { renderWithProviders } from '../test/test-utils'
import { useAuth } from './authContext'
import { ProtectedRoute } from './ProtectedRoute'

vi.mock('./authContext', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./authContext')>()
  return { ...actual, useAuth: vi.fn() }
})

function renderProtected(route: string) {
  return renderWithProviders(
    <Routes>
      <Route path="/login" element={<div>صفحه ورود</div>} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<div>محتوای محافظت‌شده</div>} />
      </Route>
    </Routes>,
    { route },
  )
}

describe('ProtectedRoute', () => {
  it('shows a checking indicator while the session is still being restored', () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    vi.mocked(useAuth).mockReturnValue({ status: 'checking' } as any)
    renderProtected('/')

    expect(screen.getByText('در حال بررسی نشست...')).toBeInTheDocument()
    expect(screen.queryByText('محتوای محافظت‌شده')).not.toBeInTheDocument()
  })

  it('redirects an unauthenticated user to /login instead of rendering protected content', () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    vi.mocked(useAuth).mockReturnValue({ status: 'unauthenticated' } as any)
    renderProtected('/')

    expect(screen.getByText('صفحه ورود')).toBeInTheDocument()
    expect(screen.queryByText('محتوای محافظت‌شده')).not.toBeInTheDocument()
  })

  it('renders the protected content for an authenticated user', () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    vi.mocked(useAuth).mockReturnValue({ status: 'authenticated' } as any)
    renderProtected('/')

    expect(screen.getByText('محتوای محافظت‌شده')).toBeInTheDocument()
  })
})
