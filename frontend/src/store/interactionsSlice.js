import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import client from '../api/client'

export const fetchInteractions = createAsyncThunk(
  'interactions/fetch',
  async ({ hcpId = null, limit = 20 } = {}) => {
    const params = { limit }
    if (hcpId) params.hcp_id = hcpId
    const { data } = await client.get('/interactions', { params })
    return data
  }
)

export const createInteraction = createAsyncThunk(
  'interactions/create',
  async (payload) => {
    const { data } = await client.post('/interactions', payload)
    return data
  }
)

const interactionsSlice = createSlice({
  name: 'interactions',
  initialState: {
    items: [],
    loading: false,
    creating: false,
    error: null,
    createError: null,
  },
  reducers: {
    clearCreateError: (state) => { state.createError = null },
    addInteraction: (state, action) => {
      state.items.unshift(action.payload)
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message
      })
      .addCase(createInteraction.pending, (state) => { state.creating = true; state.createError = null })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.creating = false
        state.items.unshift(action.payload)
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.creating = false
        state.createError = action.error.message
      })
  },
})

export const { clearCreateError, addInteraction } = interactionsSlice.actions
export default interactionsSlice.reducer
