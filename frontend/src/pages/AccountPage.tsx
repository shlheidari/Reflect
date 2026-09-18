import { Link } from 'react-router-dom'
import { useAuth } from '../auth/authContext'

export function AccountPage() {
  const { user, logout } = useAuth()
  const name = user?.participant?.display_name ?? user?.username ?? ''

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-gray-900">حساب کاربری</h1>

      <div className="mt-4 rounded-2xl bg-white p-4 shadow-sm">
        <p className="font-medium text-gray-900">{name}</p>
        <p className="text-sm text-gray-500">{user?.username}</p>
      </div>

      {user?.is_staff && (
        <Link
          to="/admin/categories"
          className="mt-4 block rounded-2xl bg-white p-4 text-center font-medium text-gray-900 shadow-sm"
        >
          مدیریت دسته‌های امتیازدهی
        </Link>
      )}

      <button
        type="button"
        onClick={() => logout()}
        className="mt-6 w-full rounded-lg bg-gray-900 py-2 font-medium text-white"
      >
        خروج
      </button>
    </div>
  )
}
