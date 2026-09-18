import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/authContext'

export function AdminRoute() {
  const { user } = useAuth()

  if (!user?.is_staff) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
