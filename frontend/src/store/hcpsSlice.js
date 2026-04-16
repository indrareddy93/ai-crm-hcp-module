import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import client from '../api/client'

export const fetchHCPs = createAsyncThunk('hcps/fetch', async (query = '') => {
  const { data } = await client.get('/hcps', { params: { q: query, limit: 20 } })
  return data
})

const hcpsSlice = createSlice({
  name: 'hcps',
  initialState: {
    list: [],
    selected: null,
    loading: false,
    searchQuery: '',
    error: null,
  },
  reducers: {
    setSelected: (state, action) => { state.selected = action.payload },
    setSearchQuery: (state, action) => { state.searchQuery = action.payload },
    clearError: (state) => { state.error = null },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHCPs.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchHCPs.fulfilled, (state, action) => {
        state.loading = false
        state.list = action.payload
      })
      .addCase(fetchHCPs.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message
      })
  },
})

export const { setSelected, setSearchQuery, clearError } = hcpsSlice.actions
export default hcpsSlice.reducer
