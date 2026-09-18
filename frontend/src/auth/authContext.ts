import { createContext, useContext } from 'react'

export interface CurrentParticipant {
  id: number
  display_name: string
  avatar: string | null
  event: number
  is_active: boolean
}

export interface CurrentUser {
  id: number
  username: string
  is_staff: boolean
  participant: CurrentParticipant | null
}

export interface LoginResponse {
  access: string
  user: CurrentUser
}

export type AuthStatus = 'checking' | 'authenticated' | 'unauthenticated'

export interface AuthContextValue {
  status: AuthStatus
  user: CurrentUser | null
  error: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
