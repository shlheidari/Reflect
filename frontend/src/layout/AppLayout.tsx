import { NavLink, Outlet } from 'react-router-dom'

const tabs = [
  { to: '/', label: 'خانه', icon: '🏠' },
  { to: '/people', label: 'بچه‌ها', icon: '👥' },
  { to: '/results', label: 'درباره من', icon: '⭐' },
  { to: '/account', label: 'حساب', icon: '👤' },
]

export function AppLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <main className="mx-auto max-w-md">
        <Outlet />
      </main>

      <nav className="fixed inset-x-0 bottom-0 border-t border-gray-200 bg-white">
        <div className="mx-auto flex max-w-md">
          {tabs.map((tab) => (
            <NavLink
              key={tab.to}
              to={tab.to}
              end={tab.to === '/'}
              className={({ isActive }) =>
                `flex flex-1 flex-col items-center gap-1 py-2.5 text-xs font-medium ${
                  isActive ? 'text-gray-900' : 'text-gray-400'
                }`
              }
            >
              <span className="text-lg">{tab.icon}</span>
              {tab.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
