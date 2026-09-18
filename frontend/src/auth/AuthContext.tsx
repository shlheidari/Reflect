import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { ApiError, apiRequest, refreshAccessToken, setAccessToken } from '../lib/apiClient'
import { AuthContext, type AuthStatus, type CurrentUser, type LoginResponse } from './authContext'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('checking')
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function restoreSession() {
      const token = await refreshAccessToken()
      if (!token) {
        if (!cancelled) setStatus('unauthenticated')
        return
      }

      setAccessToken(token)
      try {
        const me = await apiRequest<CurrentUser>('/me/')
        if (!cancelled) {
          setUser(me)
          setStatus('authenticated')
        }
      } catch {
        if (!cancelled) {
          setAccessToken(null)
          setStatus('unauthenticated')
        }
      }
    }

    restoreSession()

    return () => {
      cancelled = true
    }
  }, [])

  async function login(username: string, password: string) {
    setError(null)
    try {
      const response = await apiRequest<LoginResponse>('/auth/login/', {
        method: 'POST',
        body: { username, password },
        skipAuthRetry: true,
      })
      setAccessToken(response.access)
      setUser(response.user)
      setStatus('authenticated')
    } catch (err) {
      setAccessToken(null)
      setStatus('unauthenticated')
      const message = err instanceof ApiError ? err.message : 'ورود ناموفق بود.'
      setError(message)
      throw err
    }
  }

  async function logout() {
    try {
      await apiRequest('/auth/logout/', { method: 'POST', skipAuthRetry: true })
    } finally {
      setAccessToken(null)
      setUser(null)
      setStatus('unauthenticated')
    }
  }

  const value = useMemo(
    () => ({ status, user, error, login, logout }),
    [status, user, error],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
