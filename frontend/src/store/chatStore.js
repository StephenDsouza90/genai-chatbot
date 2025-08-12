import { create } from 'zustand';
import { chatAPI } from '../services/api';

export const useChatStore = create((set, get) => ({
  sessionId: null,
  messages: [],
  isLoading: false,

  initializeSession: async () => {
    try {
      const response = await chatAPI.createSession();
      set({ sessionId: response.session_id });
    } catch (error) {
      console.error('Failed to initialize session:', error);
    }
  },

  sendMessage: async (message, documentIds) => {
    const { sessionId } = get();
    
    // Add user message immediately
    set(state => ({
      messages: [...state.messages, { role: 'user', content: message }],
      isLoading: true
    }));

    try {
      const response = await chatAPI.sendMessage({
        question: message,
        document_ids: documentIds,
        session_id: sessionId
      });

      // Add assistant response
      set(state => ({
        messages: [...state.messages, {
          role: 'assistant',
          content: response.answer,
          sources: response.sources
        }],
        isLoading: false,
        sessionId: response.session_id // Update session ID if changed
      }));

    } catch (error) {
      // Remove user message on error
      set(state => ({
        messages: state.messages.slice(0, -1),
        isLoading: false
      }));
      throw error;
    }
  },

  clearChat: () => {
    set({ messages: [] });
  }
}));
