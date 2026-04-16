import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import ModelSelector from './ModelSelector'

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-14 shrink-0 bg-white border-b border-border flex items-center justify-between px-6">
          <nav className="flex items-center gap-2 text-sm text-textSecondary">
            <span>CRM</span>
            <span>/</span>
            <span className="text-textPrimary font-medium">Log Interaction</span>
          </nav>

          <div className="flex items-center gap-4">
            <ModelSelector />
            {/* Rep avatar */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-semibold text-sm">
                R
              </div>
              <span className="text-sm font-medium text-textPrimary hidden sm:block">Rep 001</span>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
