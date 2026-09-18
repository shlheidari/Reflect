import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './authContext'

export function ProtectedRoute() {
  const { status } = useAuth()

  if (status === 'checking') {
    return (
      <div className="flex min-h-screen items-center justify-center text-gray-500">
        در حال بررسی نشست...
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
