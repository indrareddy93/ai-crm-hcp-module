import { useDispatch, useSelector } from 'react-redux'
import { setModel } from '../store/chatSlice'

const MODELS = [
  { value: 'gemma2-9b-it', label: 'Gemma 2 9B (fast)' },
  { value: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B (powerful)' },
]

export default function ModelSelector() {
  const dispatch = useDispatch()
  const selectedModel = useSelector((s) => s.chat.selectedModel)

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-textSecondary font-medium whitespace-nowrap">AI Model:</span>
      <select
        value={selectedModel}
        onChange={(e) => dispatch(setModel(e.target.value))}
        className="text-xs border border-border rounded-lg px-2 py-1.5 text-textPrimary bg-white focus:outline-none focus:ring-2 focus:ring-primary-700 cursor-pointer"
      >
        {MODELS.map((m) => (
          <option key={m.value} value={m.value}>
            {m.label}
          </option>
        ))}
      </select>
    </div>
  )
}
