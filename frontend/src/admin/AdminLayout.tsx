import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/authContext'

const navItems = [
  { to: '/admin/overview', label: 'نمای کلی', icon: '📊' },
  { to: '/admin/participants', label: 'شرکت‌کننده‌ها', icon: '👥' },
  { to: '/admin/categories', label: 'دسته‌های امتیازدهی', icon: '🎚️' },
  { to: '/admin/event', label: 'تنظیمات رویداد', icon: '⚙️' },
  { to: '/admin/moderation', label: 'مدیریت محتوا', icon: '🚩' },
]

export function AdminLayout() {
  const { logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50 md:flex md:flex-row-reverse">
      <aside className="hidden shrink-0 border-r border-gray-200 bg-white md:flex md:w-60 md:flex-col md:justify-between">
        <div>
          <div className="p-5">
            <p className="text-lg font-bold text-gray-900">پنل مدیریت 🎓</p>
          </div>
          <nav className="space-y-1 px-3">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition-colors ${
                    isActive ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'
                  }`
                }
              >
                <span>{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="space-y-1 border-t border-gray-100 p-3">
          <NavLink
            to="/"
            className="block rounded-xl px-3 py-2 text-sm font-medium text-gray-500 hover:bg-gray-100"
          >
            بازگشت به سایت
          </NavLink>
          <button
            type="button"
            onClick={() => logout()}
            className="w-full rounded-xl px-3 py-2 text-right text-sm font-medium text-gray-500 hover:bg-gray-100"
          >
            خروج
          </button>
        </div>
      </aside>

      <nav className="flex gap-1 overflow-x-auto border-b border-gray-200 bg-white p-2 md:hidden">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `shrink-0 whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-medium ${
                isActive ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600'
              }`
            }
          >
            {item.icon} {item.label}
          </NavLink>
        ))}
        <button
          type="button"
          onClick={() => logout()}
          className="shrink-0 whitespace-nowrap rounded-full bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-500"
        >
          خروج
        </button>
      </nav>

      <main className="min-w-0 flex-1 p-4 md:p-8">
        <Outlet />
      </main>
    </div>
  )
}
