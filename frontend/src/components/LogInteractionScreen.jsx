import { useState } from 'react'
import InteractionForm from './InteractionForm'
import ChatInterface from './ChatInterface'
import InteractionList from './InteractionList'
import { useDispatch } from 'react-redux'
import { fetchInteractions } from '../store/interactionsSlice'

const TABS = [
  { id: 'form', label: '📋 Structured Form' },
  { id: 'chat', label: '💬 Chat with AI' },
]

export default function LogInteractionScreen() {
  const [activeTab, setActiveTab] = useState('form')
  const [railOpen, setRailOpen] = useState(true)
  const dispatch = useDispatch()

  const handleFormSuccess = () => {
    dispatch(fetchInteractions({ limit: 20 }))
  }

  return (
    <div className="flex h-full overflow-hidden">
      {/* Main panel */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Tab switcher */}
        <div className="shrink-0 px-6 pt-5 pb-0">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold text-textPrimary">Log Interaction</h1>
            <button
              onClick={() => setRailOpen((r) => !r)}
              className="text-xs text-textSecondary hover:text-textPrimary flex items-center gap-1"
            >
              {railOpen ? '→' : '←'} {railOpen ? 'Hide' : 'Show'} Recent
            </button>
          </div>

          <div className="flex bg-gray-100 rounded-xl p-1 w-fit">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-white text-primary-700 shadow-sm'
                    : 'text-textSecondary hover:text-textPrimary'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content area */}
        <div className="flex-1 overflow-hidden mt-4">
          {activeTab === 'form' ? (
            <div className="h-full overflow-y-auto px-6 pb-6">
              <div className="max-w-2xl">
                <InteractionForm onSuccess={handleFormSuccess} />
              </div>
            </div>
          ) : (
            <div className="h-full">
              <ChatInterface />
            </div>
          )}
        </div>
      </div>

      {/* Right Rail */}
      {railOpen && (
        <div className="w-80 shrink-0 border-l border-border bg-white overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto p-4">
            <InteractionList />
          </div>
        </div>
      )}
    </div>
  )
}
