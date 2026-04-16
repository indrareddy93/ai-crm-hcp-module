import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import client from '../api/client'

export const sendChatMessage = createAsyncThunk(
  'chat/send',
  async ({ messages, model, repId }, { rejectWithValue }) => {
    try {
      const { data } = await client.post('/chat', {
        messages: messages.map((m) => ({
          role: m.role,
          content: m.content,
        })),
        model,
        rep_id: repId,
      })
      return data.messages
    } catch (err) {
      return rejectWithValue(err.message)
    }
  }
)

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    isLoading: false,
    selectedModel: 'llama-3.1-8b-instant',
    repId: 'rep_001',
    error: null,
  },
  reducers: {
    setModel: (state, action) => { state.selectedModel = action.payload },
    addUserMessage: (state, action) => {
      state.messages.push({ role: 'user', content: action.payload })
    },
    clearChat: (state) => { state.messages = []; state.error = null },
    clearError: (state) => { state.error = null },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.isLoading = false
        // Replace messages with full response (includes tool calls + results)
        state.messages = action.payload
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload || 'Something went wrong'
        state.messages.push({
          role: 'assistant',
          content: `Error: ${action.payload || 'Something went wrong. Please try again.'}`,
        })
      })
  },
})

export const { setModel, addUserMessage, clearChat, clearError } = chatSlice.actions
export default chatSlice.reducer
