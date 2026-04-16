import { useRef, useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { sendChatMessage, addUserMessage, clearChat } from '../store/chatSlice'
import { addInteraction } from '../store/interactionsSlice'

function ToolCallCard({ toolCall, result }) {
  const [expanded, setExpanded] = useState(false)
  const hasResult = result !== undefined

  const isLogInteraction = toolCall.name === 'log_interaction'
  const hasInteractionId = hasResult && result?.interaction_id

  return (
    <div className="border border-border rounded-xl overflow-hidden text-xs bg-white shadow-sm">
      {/* Header */}
      <button
        onClick={() => setExpanded((e) => !e)}
        className="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-primary-700 font-medium">⚙️ Tool: {toolCall.name}</span>
          {hasResult && (
            <span className={`px-1.5 py-0.5 rounded-full text-xs font-medium ${hasInteractionId ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
              {hasInteractionId ? '✓ Done' : '✓ OK'}
            </span>
          )}
        </div>
        <span className="text-textSecondary">{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div className="px-3 py-2 space-y-2">
          {/* Args */}
          <div>
            <div className="text-textSecondary font-medium mb-1">Args:</div>
            <pre className="text-xs text-textPrimary bg-gray-50 p-2 rounded-lg overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(toolCall.args, null, 2)}
            </pre>
          </div>

          {/* Result */}
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

      {/* Success banner for logged interactions */}
      {isLogInteraction && hasInteractionId && (
        <div className="px-3 py-2 bg-green-50 border-t border-green-100 flex items-center justify-between">
          <span className="text-green-700 font-medium">✓ Logged interaction #{result.interaction_id?.slice(0, 8)}</span>
          <span className="text-green-600 text-xs">Sentiment: {result.sentiment}</span>
        </div>
      )}
    </div>
  )
}

function Message({ msg, allMessages, index }) {
  const isUser = msg.role === 'user'
  const isAssistant = msg.role === 'assistant'
  const isTool = msg.role === 'tool'

  // Skip tool messages — they're rendered inline with the assistant message
  if (isTool) return null

  // For assistant messages with tool_calls, pair them with following tool results
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
        <div className="max-w-[80%] bg-primary-700 text-white text-sm px-4 py-2.5 rounded-2xl rounded-tr-sm">
          {msg.content}
        </div>
      </div>
    )
  }

  if (isAssistant) {
    return (
      <div className="flex flex-col gap-2">
        {/* Tool calls */}
        {msg.tool_calls?.map((tc) => (
          <ToolCallCard key={tc.id} toolCall={tc} result={toolResults[tc.id]} />
        ))}

        {/* Assistant text */}
        {msg.content && (
          <div className="flex justify-start">
            <div className="max-w-[85%]">
              <div className="flex items-center gap-1.5 mb-1">
                <div className="w-5 h-5 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 text-xs font-bold">
                  M
                </div>
                <span className="text-xs text-textSecondary font-medium">MedRep Copilot</span>
              </div>
              <div className="bg-white border border-border text-textPrimary text-sm px-4 py-2.5 rounded-2xl rounded-tl-sm shadow-sm whitespace-pre-wrap">
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

export default function ChatInterface() {
  const dispatch = useDispatch()
  const { messages, isLoading, selectedModel, repId } = useSelector((s) => s.chat)
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSend = () => {
    const text = input.trim()
    if (!text || isLoading) return

    // Add user message optimistically
    dispatch(addUserMessage(text))
    setInput('')

    // Build message list including the new user message
    const updatedMessages = [
      ...messages.filter((m) => m.role !== 'tool'), // strip tool msgs for sending
      { role: 'user', content: text },
    ]

    dispatch(sendChatMessage({ messages: updatedMessages, model: selectedModel, repId }))
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const examplePrompts = [
    'Log a meeting with Dr. Sharma about Atorvastatin — she was positive and wants samples',
    'Find Dr. Patel',
    'Show my history with Dr. Sharma',
  ]

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-4 py-8">
            <div className="text-5xl">🤖</div>
            <div>
              <h3 className="text-base font-semibold text-textPrimary mb-1">MedRep Copilot</h3>
              <p className="text-sm text-textSecondary">
                Your AI assistant for logging HCP interactions. Try:
              </p>
            </div>
            <div className="flex flex-col gap-2 w-full max-w-md">
              {examplePrompts.map((p) => (
                <button
                  key={p}
                  onClick={() => { setInput(p); textareaRef.current?.focus() }}
                  className="text-left text-sm px-4 py-2.5 bg-white border border-border rounded-xl hover:border-primary-700 hover:text-primary-700 transition-colors"
                >
                  "{p}"
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <Message key={i} msg={msg} allMessages={messages} index={i} />
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
      <div className="shrink-0 border-t border-border bg-white px-4 py-3">
        {messages.length > 0 && (
          <div className="flex justify-end mb-2">
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
            placeholder="Type a message... (Enter to send, Shift+Enter for new line)"
            rows={2}
            className="input-field flex-1 resize-none"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="btn-primary shrink-0 px-4 py-3 text-base"
          >
            ↑
          </button>
        </div>
        <div className="mt-1.5 text-xs text-textSecondary flex items-center gap-1">
          <span>Model:</span>
          <span className="font-medium text-primary-700">{selectedModel}</span>
        </div>
      </div>
    </div>
  )
}
