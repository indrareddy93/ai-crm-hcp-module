import { useState, useCallback } from 'react'
import InteractionForm from './InteractionForm'
import ChatInterface from './ChatInterface'
import InteractionList from './InteractionList'
import { useDispatch } from 'react-redux'
import { fetchInteractions } from '../store/interactionsSlice'

export default function LogInteractionScreen() {
  const [chatOpen, setChatOpen] = useState(false)
  const [railOpen, setRailOpen] = useState(false)
  const [chatFilledData, setChatFilledData] = useState(null)
  const dispatch = useDispatch()

  const handleFormSuccess = () => {
    dispatch(fetchInteractions({ limit: 20 }))
  }

  const handleFormUpdate = useCallback((data) => {
    setChatFilledData(data)
  }, [])

  const toggleChat = () => {
    setChatOpen((prev) => {
      if (!prev) setRailOpen(false) // close rail when opening chat
      return !prev
    })
  }

  return (
    <div className="flex h-full overflow-hidden relative">
      {/* Main form panel */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Header */}
        <div className="shrink-0 px-6 pt-5 pb-4 flex items-center justify-between border-b border-border bg-white">
          <h1 className="text-xl font-semibold text-textPrimary">Log Interaction</h1>
          {!chatOpen && (
            <button
              onClick={() => setRailOpen((r) => !r)}
              className="text-xs text-textSecondary hover:text-textPrimary flex items-center gap-1 transition-colors"
            >
              {railOpen ? '→ Hide Recent' : '← Show Recent'}
            </button>
          )}
        </div>

        {/* Form area */}
        <div className="flex-1 overflow-y-auto px-6 pb-24 bg-background">
          <div className="max-w-2xl pt-5">
            <InteractionForm onSuccess={handleFormSuccess} chatFilledData={chatFilledData} />
          </div>
        </div>
      </div>

      {/* Recent interactions rail (hidden when chat is open) */}
      {railOpen && !chatOpen && (
        <div className="w-80 shrink-0 border-l border-border bg-white overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto p-4">
            <InteractionList />
          </div>
        </div>
      )}

      {/* Chat side panel */}
      {chatOpen && (
        <div className="w-96 shrink-0 border-l border-border bg-white overflow-hidden flex flex-col shadow-2xl">
          {/* Chat panel header */}
          <div className="shrink-0 px-4 py-3 border-b border-border bg-primary-50 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-full bg-primary-700 flex items-center justify-center text-lg shadow-sm">
                🤖
              </div>
              <div>
                <p className="text-sm font-semibold text-textPrimary">AI Assistant</p>
                <p className="text-xs text-textSecondary">Log Interaction details here via chat</p>
              </div>
            </div>
            <button
              onClick={() => setChatOpen(false)}
              className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-gray-200 text-textSecondary hover:text-textPrimary transition-colors text-sm font-bold"
              title="Close chat"
            >
              ✕
            </button>
          </div>

          {/* Chat interface */}
          <div className="flex-1 overflow-hidden">
            <ChatInterface onFormUpdate={handleFormUpdate} />
          </div>
        </div>
      )}

      {/* Floating chat bot button */}
      <button
        onClick={toggleChat}
        title={chatOpen ? 'Close AI Assistant' : 'Open AI Assistant'}
        className={`fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-xl flex items-center justify-center z-50 transition-all duration-200 select-none
          ${chatOpen
            ? 'bg-gray-500 hover:bg-gray-600 text-white scale-100'
            : 'bg-primary-700 hover:bg-primary-800 text-white hover:scale-110 hover:shadow-2xl'
          }`}
      >
        <span className="text-2xl leading-none">{chatOpen ? '✕' : '🤖'}</span>

        {/* Pulse ring when chat is closed (invite to click) */}
        {!chatOpen && (
          <span className="absolute inset-0 rounded-full bg-primary-700 opacity-30 animate-ping" />
        )}
      </button>
    </div>
  )
}
