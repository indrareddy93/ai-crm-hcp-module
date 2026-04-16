import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '⊞' },
  { to: '/log', label: 'Log Interaction', icon: '✎', active: true },
  { to: '/hcps', label: 'HCPs', icon: '👤' },
  { to: '/followups', label: 'Follow-ups', icon: '📅' },
]

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 h-full bg-white border-r border-border flex flex-col">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary-700 flex items-center justify-center text-white text-sm font-bold">
            M
          </div>
          <div>
            <div className="text-sm font-700 text-textPrimary leading-tight font-semibold">MedRep CRM</div>
            <div className="text-xs text-textSecondary">Life Sciences</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-textSecondary hover:bg-gray-50 hover:text-textPrimary'
              }`
            }
          >
            <span className="text-base">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-border">
        <div className="text-xs text-textSecondary">© 2024 MedRep CRM</div>
      </div>
    </aside>
  )
}
