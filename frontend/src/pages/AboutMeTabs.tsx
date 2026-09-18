import { NavLink } from 'react-router-dom'

// "My Results" and "Memories About Me" are two distinct pages (per project
// CLAUDE.md's page list) that both live under the single "⭐ درباره من"
// bottom-nav slot (docs/UX.md #9 fixes that nav to 4 tabs) — this segmented
// control is how a participant moves between them without adding a 5th tab.
const tabs = [
  { to: '/results', label: 'نتایج' },
  { to: '/memories', label: 'خاطره‌ها' },
]

export function AboutMeTabs() {
  return (
    <div className="mx-auto mt-4 flex w-fit gap-1 rounded-full bg-gray-100 p-1">
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          className={({ isActive }) =>
            `rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
              isActive ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
            }`
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </div>
  )
}
