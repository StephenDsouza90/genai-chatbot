import { create } from 'zustand';
import { chatAPI } from '../services/api';

export const useChatStore = create((set, get) => ({
  sessionId: null,
  messages: [],
  isLoading: false,
  sessions: [],
  sessionsLoading: false,

  initializeSession: async () => {
    try {
      const response = await chatAPI.createSession();
      set({ sessionId: response.session_id });
      // Refresh sessions list after creating new session
      get().fetchSessions();
    } catch (error) {
      console.error('Failed to initialize session:', error);
    }
  },

  fetchSessions: async () => {
    try {
      set({ sessionsLoading: true });
      const sessions = await chatAPI.getAllSessions();
      set({ sessions, sessionsLoading: false });
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
      set({ sessionsLoading: false });
    }
  },

  switchSession: async (sessionId) => {
    try {
      set({ isLoading: true });
      
      // Fetch the chat history for this session
      const sessionHistory = await chatAPI.getSessionHistory(sessionId);
      
      // Convert the backend message format to frontend format
      const messages = sessionHistory.messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        sources: msg.sources || undefined
      }));
      
      set({ 
        sessionId, 
        messages,
        isLoading: false 
      });
      
      // Refresh sessions list
      get().fetchSessions();
    } catch (error) {
      console.error('Failed to switch session:', error);
      // If there's an error, still switch to the session but with no messages
      set({ 
        sessionId, 
        messages: [],
        isLoading: false 
      });
    }
  },

  deleteSession: async (sessionId) => {
    try {
      await chatAPI.deleteSession(sessionId);
      
      // Remove from sessions list
      set(state => ({
        sessions: state.sessions.filter(s => s.session_id !== sessionId)
      }));
      
      // If we deleted the current session, clear it
      if (get().sessionId === sessionId) {
        set({ sessionId: null, messages: [] });
      }
      
      return true;
    } catch (error) {
      console.error('Failed to delete session:', error);
      throw error;
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

      // Refresh sessions list to update message counts
      get().fetchSessions();

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
