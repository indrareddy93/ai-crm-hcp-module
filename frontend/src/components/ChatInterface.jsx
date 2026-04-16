import { useRef, useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { sendChatMessage, addUserMessage, clearChat } from '../store/chatSlice'

function ToolCallCard({ toolCall, result }) {
  const [expanded, setExpanded] = useState(false)
  const hasResult = result !== undefined

  const isLogInteraction = toolCall.name === 'log_interaction'
  const isEditInteraction = toolCall.name === 'edit_interaction'
  const hasInteractionId = hasResult && result?.interaction_id
  const hasError = hasResult && result?.error

  return (
    <div className="border border-border rounded-xl overflow-hidden text-xs bg-white shadow-sm">
      {/* Header */}
      <button
        onClick={() => setExpanded((e) => !e)}
        className="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-primary-700 font-medium">⚙️ Tool: {toolCall.name}</span>
          {hasResult && !hasError && (
            <span className={`px-1.5 py-0.5 rounded-full text-xs font-medium ${hasInteractionId ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
              {hasInteractionId ? '✓ Done' : '✓ OK'}
            </span>
          )}
          {hasError && (
            <span className="px-1.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">✗ Error</span>
          )}
        </div>
        <span className="text-textSecondary">{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div className="px-3 py-2 space-y-2">
          <div>
            <div className="text-textSecondary font-medium mb-1">Args:</div>
            <pre className="text-xs text-textPrimary bg-gray-50 p-2 rounded-lg overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(toolCall.args, null, 2)}
            </pre>
          </div>
          {hasResult && (
            <div>
              <div className="text-textSecondary font-medium mb-1">Result:</div>
              <pre className="text-xs text-textPrimary bg-gray-50 p-2 rounded-lg overflow-x-auto whitespace-pre-wrap">
                {typeof result === 'string' ? result : JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Success banner for logged/edited interactions */}
      {(isLogInteraction || isEditInteraction) && hasInteractionId && (
        <div className="px-3 py-2 bg-green-50 border-t border-green-100 flex items-center justify-between">
          <span className="text-green-700 font-medium">
            {isLogInteraction ? '✓ Logged' : '✓ Updated'} #{result.interaction_id?.slice(0, 8)}
          </span>
          {result.sentiment && (
            <span className="text-green-600 text-xs capitalize">Sentiment: {result.sentiment}</span>
          )}
        </div>
      )}
    </div>
  )
}

function Message({ msg, allMessages }) {
  const isUser = msg.role === 'user'
  const isAssistant = msg.role === 'assistant'
  const isTool = msg.role === 'tool'

  // Tool messages are rendered inline with the assistant message above
  if (isTool) return null

  // Pair tool results with assistant tool_calls
  const toolResults = {}
  if (isAssistant && msg.tool_calls?.length) {
    msg.tool_calls.forEach((tc) => {
      const resultMsg = allMessages.find(
        (m) => m.role === 'tool' && m.tool_call_id === tc.id
      )
      if (resultMsg) {
        try {
          toolResults[tc.id] = JSON.parse(resultMsg.content)
        } catch {
          toolResults[tc.id] = resultMsg.content
        }
      }
    })
  }

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] bg-primary-700 text-white text-sm px-4 py-2.5 rounded-2xl rounded-tr-sm leading-relaxed">
          {msg.content}
        </div>
      </div>
    )
  }

  if (isAssistant) {
    return (
      <div className="flex flex-col gap-2">
        {/* Tool call cards */}
        {msg.tool_calls?.map((tc) => (
          <ToolCallCard key={tc.id} toolCall={tc} result={toolResults[tc.id]} />
        ))}

        {/* Assistant text bubble */}
        {msg.content && (
          <div className="flex justify-start">
            <div className="max-w-[88%]">
              <div className="flex items-center gap-1.5 mb-1">
                <div className="w-5 h-5 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 text-xs font-bold">
                  M
                </div>
                <span className="text-xs text-textSecondary font-medium">MedRep Copilot</span>
              </div>
              <div className="bg-white border border-border text-textPrimary text-sm px-4 py-2.5 rounded-2xl rounded-tl-sm shadow-sm whitespace-pre-wrap leading-relaxed">
                {msg.content}
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  return null
}

export default function ChatInterface({ onFormUpdate }) {
  const dispatch = useDispatch()
  const { messages, isLoading, selectedModel, repId } = useSelector((s) => s.chat)
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Extract form data from tool results and notify parent
  useEffect(() => {
    if (!onFormUpdate || messages.length === 0) return

    // Scan assistant messages with tool_calls in reverse (most recent first)
    const assistantMsgs = [...messages]
      .reverse()
      .filter((m) => m.role === 'assistant' && m.tool_calls?.length)

    for (const assistantMsg of assistantMsgs) {
      for (const tc of assistantMsg.tool_calls) {
        if (tc.name === 'log_interaction' || tc.name === 'edit_interaction') {
          const toolResult = messages.find(
            (m) => m.role === 'tool' && m.tool_call_id === tc.id
          )
          if (toolResult) {
            try {
              const result = JSON.parse(toolResult.content)
              if (!result.error && !result.ambiguous && result.interaction_id) {
                onFormUpdate(result)
                return
              }
            } catch {
              // ignore parse errors
            }
          }
        }
      }
    }
  }, [messages, onFormUpdate])

  const handleSend = () => {
    const text = input.trim()
    if (!text || isLoading) return

    dispatch(addUserMessage(text))
    setInput('')

    // Build message history: strip tool messages and empty assistant stubs
    // to avoid invalid LangChain message sequences
    const history = messages.filter(
      (m) => m.role !== 'tool' && !(m.role === 'assistant' && !m.content && m.tool_calls?.length)
    )

    const updatedMessages = [...history, { role: 'user', content: text }]
    dispatch(sendChatMessage({ messages: updatedMessages, model: selectedModel, repId }))
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const examplePrompts = [
    'Met Dr. Smith, discussed Product X efficiency. Positive sentiment, shared brochures.',
    'Find Dr. Patel in cardiology',
    'Show my history with Dr. Sharma',
  ]

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col gap-3 pt-2">
            {/* Prompt hint */}
            <div className="bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm text-textSecondary leading-relaxed">
              Log interaction details here (e.g., "Met Dr. Smith, discussed Prodo-X efficacy,
              positive sentiment, shared brochure") or ask for help.
            </div>

            {/* Example prompts */}
            <div className="flex flex-col gap-1.5">
              {examplePrompts.map((p) => (
                <button
                  key={p}
                  onClick={() => { setInput(p); textareaRef.current?.focus() }}
                  className="text-left text-xs px-3 py-2 bg-white border border-border rounded-xl hover:border-primary-700 hover:text-primary-700 transition-colors text-textSecondary"
                >
                  "{p}"
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <Message key={i} msg={msg} allMessages={messages} />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 bg-white border border-border px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-1.5 h-1.5 bg-primary-700 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 150}ms` }}
                  />
                ))}
              </div>
              <span className="text-xs text-textSecondary">Thinking...</span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Composer */}
      <div className="shrink-0 border-t border-border bg-white px-3 py-3">
        {messages.length > 0 && (
          <div className="flex justify-end mb-1.5">
            <button
              onClick={() => dispatch(clearChat())}
              className="text-xs text-textSecondary hover:text-error transition-colors"
            >
              Clear chat
            </button>
          </div>
        )}
        <div className="flex items-end gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe Interaction..."
            rows={2}
            className="input-field flex-1 resize-none text-sm"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="btn-primary shrink-0 px-4 py-3 rounded-xl flex flex-col items-center leading-tight"
            title="Send (Enter)"
          >
            <span className="text-xs font-bold">AI</span>
            <span className="text-xs">Log</span>
          </button>
        </div>
        <div className="mt-1 text-xs text-textSecondary">
          Model: <span className="font-medium text-primary-700">{selectedModel}</span>
        </div>
      </div>
    </div>
  )
}
