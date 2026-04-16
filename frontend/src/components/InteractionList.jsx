import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchInteractions } from '../store/interactionsSlice'

const SENTIMENT_COLORS = {
  positive: 'bg-green-100 text-green-700',
  neutral: 'bg-gray-100 text-gray-600',
  negative: 'bg-red-100 text-red-600',
}

const TYPE_LABELS = {
  in_person: 'In Person',
  virtual: 'Virtual',
  phone: 'Phone',
  email: 'Email',
}

function InteractionCard({ interaction }) {
  const date = interaction.interaction_date
    ? new Date(interaction.interaction_date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : '—'

  return (
    <div className="p-3 border border-border rounded-xl bg-white hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-1.5">
        <span className="text-xs font-medium text-textPrimary truncate">
          {TYPE_LABELS[interaction.interaction_type] || interaction.interaction_type}
        </span>
        <span
          className={`shrink-0 text-xs px-1.5 py-0.5 rounded-full font-medium capitalize ${
            SENTIMENT_COLORS[interaction.sentiment] || SENTIMENT_COLORS.neutral
          }`}
        >
          {interaction.sentiment || 'neutral'}
        </span>
      </div>

      {interaction.summary && (
        <p className="text-xs text-textSecondary line-clamp-2 mb-1.5">{interaction.summary}</p>
      )}

      {interaction.products_discussed?.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-1.5">
          {interaction.products_discussed.slice(0, 3).map((p) => (
            <span key={p} className="text-xs bg-primary-50 text-primary-700 px-1.5 py-0.5 rounded-md">
              {p}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between">
        <span className="text-xs text-textSecondary">{date}</span>
        <span
          className={`text-xs px-1.5 py-0.5 rounded-md font-medium ${
            interaction.source === 'chat'
              ? 'bg-accent-500 bg-opacity-10 text-accent-600'
              : 'bg-gray-100 text-gray-500'
          }`}
        >
          {interaction.source}
        </span>
      </div>
    </div>
  )
}

export default function InteractionList({ hcpId }) {
  const dispatch = useDispatch()
  const { items, loading, error } = useSelector((s) => s.interactions)

  useEffect(() => {
    dispatch(fetchInteractions({ hcpId, limit: 20 }))
  }, [dispatch, hcpId])

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-textPrimary">Recent Interactions</h3>
        <button
          onClick={() => dispatch(fetchInteractions({ hcpId, limit: 20 }))}
          className="text-xs text-primary-700 hover:underline"
        >
          Refresh
        </button>
      </div>

      {loading && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-xs text-textSecondary animate-pulse">Loading...</div>
        </div>
      )}

      {error && (
        <div className="text-xs text-error bg-red-50 border border-red-200 rounded-xl p-3">
          {error}
        </div>
      )}

      {!loading && items.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center text-center gap-2 py-8">
          <div className="text-3xl">📋</div>
          <p className="text-xs text-textSecondary">No interactions yet</p>
          <p className="text-xs text-textSecondary">Log one using the form or chat</p>
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {items.map((interaction) => (
          <InteractionCard key={interaction.id} interaction={interaction} />
        ))}
      </div>
    </div>
  )
}
