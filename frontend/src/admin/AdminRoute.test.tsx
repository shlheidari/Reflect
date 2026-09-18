import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { useAuth } from '../auth/authContext'
import { renderWithProviders } from '../test/test-utils'
import { AdminRoute } from './AdminRoute'

vi.mock('../auth/authContext', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../auth/authContext')>()
  return { ...actual, useAuth: vi.fn() }
})

function renderAdminRoute(route: string) {
  return renderWithProviders(
    <Routes>
      <Route path="/" element={<div>خانه شرکت‌کننده</div>} />
      <Route element={<AdminRoute />}>
        <Route path="/admin" element={<div>پنل مدیریت</div>} />
      </Route>
    </Routes>,
    { route },
  )
}

describe('AdminRoute', () => {
  it('bounces a plain participant (participant -> admin resource, IDOR/authorization check) back to /', () => {
    vi.mocked(useAuth).mockReturnValue({
      status: 'authenticated',
      user: { id: 1, username: 'ali', is_staff: false, participant: null },
      error: null,
      login: vi.fn(),
      logout: vi.fn(),
    })
    renderAdminRoute('/admin')

    expect(screen.getByText('خانه شرکت‌کننده')).toBeInTheDocument()
    expect(screen.queryByText('پنل مدیریت')).not.toBeInTheDocument()
  })

  it('bounces a user with no participant/user object at all', () => {
    vi.mocked(useAuth).mockReturnValue({
      status: 'authenticated',
      user: null,
      error: null,
      login: vi.fn(),
      logout: vi.fn(),
    })
    renderAdminRoute('/admin')

    expect(screen.getByText('خانه شرکت‌کننده')).toBeInTheDocument()
  })

  it('lets a staff user through to the admin panel', () => {
    vi.mocked(useAuth).mockReturnValue({
      status: 'authenticated',
      user: { id: 2, username: 'devadmin', is_staff: true, participant: null },
      error: null,
      login: vi.fn(),
      logout: vi.fn(),
    })
    renderAdminRoute('/admin')

    expect(screen.getByText('پنل مدیریت')).toBeInTheDocument()
  })
})
