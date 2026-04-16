import { useState, useEffect, useCallback } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { createInteraction } from '../store/interactionsSlice'
import { fetchHCPs, setSelected } from '../store/hcpsSlice'
import client from '../api/client'

const INTERACTION_TYPES = [
  { value: 'in_person', label: '🤝 In Person' },
  { value: 'virtual', label: '💻 Virtual' },
  { value: 'phone', label: '📞 Phone' },
  { value: 'email', label: '✉️ Email' },
]

const SENTIMENT_OPTIONS = [
  { value: 'positive', label: '😊 Positive' },
  { value: 'neutral', label: '😐 Neutral' },
  { value: 'negative', label: '😞 Negative' },
]

const DEFAULT_FORM = {
  hcp_id: '',
  interaction_type: 'in_person',
  interaction_date: '',
  products_discussed: [],
  outcome: '',
  raw_notes: '',
  sentiment: 'neutral',
}

export default function InteractionForm({ onSuccess }) {
  const dispatch = useDispatch()
  const { creating, createError } = useSelector((s) => s.interactions)

  const [form, setForm] = useState(DEFAULT_FORM)
  const [hcpSearch, setHcpSearch] = useState('')
  const [hcpResults, setHcpResults] = useState([])
  const [selectedHcp, setSelectedHcp] = useState(null)
  const [productInput, setProductInput] = useState('')
  const [toast, setToast] = useState(null)
  const [searching, setSearching] = useState(false)

  // Debounced HCP search
  useEffect(() => {
    if (!hcpSearch || hcpSearch.length < 2) { setHcpResults([]); return }
    const timer = setTimeout(async () => {
      setSearching(true)
      try {
        const { data } = await client.get('/hcps', { params: { q: hcpSearch, limit: 8 } })
        setHcpResults(data)
      } catch {
        setHcpResults([])
      } finally {
        setSearching(false)
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [hcpSearch])

  const handleSelectHcp = (hcp) => {
    setSelectedHcp(hcp)
    setForm((f) => ({ ...f, hcp_id: hcp.id }))
    setHcpSearch(`${hcp.first_name} ${hcp.last_name}`)
    setHcpResults([])
  }

  const addProduct = () => {
    const p = productInput.trim()
    if (p && !form.products_discussed.includes(p)) {
      setForm((f) => ({ ...f, products_discussed: [...f.products_discussed, p] }))
    }
    setProductInput('')
  }

  const removeProduct = (p) => {
    setForm((f) => ({ ...f, products_discussed: f.products_discussed.filter((x) => x !== p) }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.hcp_id) { setToast({ type: 'error', msg: 'Please select an HCP.' }); return }

    const payload = {
      ...form,
      source: 'form',
      interaction_date: form.interaction_date || undefined,
    }
    const result = await dispatch(createInteraction(payload))
    if (createInteraction.fulfilled.match(result)) {
      setToast({ type: 'success', msg: '✓ Interaction logged successfully!' })
      setForm(DEFAULT_FORM)
      setHcpSearch('')
      setSelectedHcp(null)
      if (onSuccess) onSuccess()
      setTimeout(() => setToast(null), 3000)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Toast */}
      {toast && (
        <div
          className={`px-4 py-3 rounded-xl text-sm font-medium ${
            toast.type === 'success'
              ? 'bg-green-50 text-success border border-green-200'
              : 'bg-red-50 text-error border border-red-200'
          }`}
        >
          {toast.msg}
        </div>
      )}

      {/* HCP Search */}
      <div>
        <label className="block text-xs font-semibold text-textSecondary mb-1.5 uppercase tracking-wide">
          Healthcare Professional *
        </label>
        <div className="relative">
          <input
            type="text"
            value={hcpSearch}
            onChange={(e) => { setHcpSearch(e.target.value); setSelectedHcp(null); setForm((f) => ({ ...f, hcp_id: '' })) }}
            placeholder="Search by name, specialty, hospital..."
            className="input-field"
          />
          {searching && (
            <div className="absolute right-3 top-2.5 text-xs text-textSecondary animate-pulse">searching...</div>
          )}
          {hcpResults.length > 0 && (
            <div className="absolute z-10 top-full left-0 right-0 bg-white border border-border rounded-xl shadow-lg mt-1 max-h-48 overflow-y-auto">
              {hcpResults.map((hcp) => (
                <button
                  key={hcp.id}
                  type="button"
                  onClick={() => handleSelectHcp(hcp)}
                  className="w-full text-left px-3 py-2.5 hover:bg-primary-50 transition-colors"
                >
                  <div className="text-sm font-medium text-textPrimary">
                    {hcp.first_name} {hcp.last_name}
                  </div>
                  <div className="text-xs text-textSecondary">
                    {hcp.specialty} · {hcp.hospital}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
        {selectedHcp && (
          <div className="mt-2 text-xs text-primary-700 bg-primary-50 px-3 py-1.5 rounded-lg">
            Selected: {selectedHcp.first_name} {selectedHcp.last_name} — {selectedHcp.specialty}, {selectedHcp.hospital}
          </div>
        )}
      </div>

      {/* Interaction Type */}
      <div>
        <label className="block text-xs font-semibold text-textSecondary mb-1.5 uppercase tracking-wide">
          Interaction Type
        </label>
        <div className="flex flex-wrap gap-2">
          {INTERACTION_TYPES.map((t) => (
            <button
              key={t.value}
              type="button"
              onClick={() => setForm((f) => ({ ...f, interaction_type: t.value }))}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition-colors ${
                form.interaction_type === t.value
                  ? 'bg-primary-700 text-white border-primary-700'
                  : 'bg-white text-textSecondary border-border hover:border-primary-700 hover:text-primary-700'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Date */}
      <div>
        <label className="block text-xs font-semibold text-textSecondary mb-1.5 uppercase tracking-wide">
          Date & Time
        </label>
        <input
          type="datetime-local"
          value={form.interaction_date}
          onChange={(e) => setForm((f) => ({ ...f, interaction_date: e.target.value }))}
          className="input-field"
        />
      </div>

      {/* Products */}
      <div>
        <label className="block text-xs font-semibold text-textSecondary mb-1.5 uppercase tracking-wide">
          Products Discussed
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={productInput}
            onChange={(e) => setProductInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addProduct() } }}
            placeholder="Type product name + Enter"
            className="input-field flex-1"
          />
          <button type="button" onClick={addProduct} className="btn-secondary text-sm px-3">
            Add
          </button>
        </div>
        {form.products_discussed.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {form.products_discussed.map((p) => (
              <span
                key={p}
                className="flex items-center gap-1 text-xs bg-primary-50 text-primary-700 px-2 py-1 rounded-lg"
              >
                {p}
                <button type="button" onClick={() => removeProduct(p)} className="hover:text-error ml-0.5">
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Raw Notes */}
      <div>
        <label className="block text-xs font-semibold text-textSecondary mb-1.5 uppercase tracking-wide">
          Field Notes
        </label>
        <textarea
          value={form.raw_notes}
          onChange={(e) => setForm((f) => ({ ...f, raw_notes: e.target.value }))}
          placeholder="Describe the interaction, key discussion points, HCP reactions..."
          rows={4}
          className="input-field resize-none"
        />
      </div>

      {/* Outcome */}
      <div>
        <label className="block text-xs font-semibold text-textSecondary mb-1.5 uppercase tracking-wide">
          Outcome
        </label>
        <textarea
          value={form.outcome}
          onChange={(e) => setForm((f) => ({ ...f, outcome: e.target.value }))}
          placeholder="What was agreed? Any follow-up actions?"
          rows={2}
          className="input-field resize-none"
        />
      </div>

      {/* Sentiment */}
      <div>
        <label className="block text-xs font-semibold text-textSecondary mb-1.5 uppercase tracking-wide">
          Sentiment (optional)
        </label>
        <div className="flex gap-2">
          {SENTIMENT_OPTIONS.map((s) => (
            <button
              key={s.value}
              type="button"
              onClick={() => setForm((f) => ({ ...f, sentiment: s.value }))}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition-colors ${
                form.sentiment === s.value
                  ? 'bg-primary-700 text-white border-primary-700'
                  : 'bg-white text-textSecondary border-border hover:border-primary-700 hover:text-primary-700'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {createError && (
        <div className="text-xs text-error bg-red-50 border border-red-200 rounded-xl p-3">
          {createError}
        </div>
      )}

      {/* Submit */}
      <button type="submit" disabled={creating} className="btn-primary w-full text-sm py-3">
        {creating ? 'Saving...' : '💾 Log Interaction'}
      </button>
    </form>
  )
}
