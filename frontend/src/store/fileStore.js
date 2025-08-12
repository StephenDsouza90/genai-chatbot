import { create } from 'zustand';
import { fileAPI } from '../services/api';

export const useFileStore = create((set, get) => ({
  files: [],
  selectedFiles: [],
  isLoading: false,
  isUploading: false,

  loadFiles: async () => {
    set({ isLoading: true });
    try {
      const files = await fileAPI.getFiles();
      set({ files, isLoading: false });
    } catch (error) {
      console.error('Failed to load files:', error);
      set({ isLoading: false });
    }
  },

  uploadFile: async (file) => {
    set({ isUploading: true });
    try {
      await fileAPI.uploadFile(file);
      // Reload files after upload
      await get().loadFiles();
    } finally {
      set({ isUploading: false });
    }
  },

  toggleFileSelection: (fileId) => {
    set(state => {
      const isSelected = state.selectedFiles.includes(fileId);
      const selectedFiles = isSelected
        ? state.selectedFiles.filter(id => id !== fileId)
        : [...state.selectedFiles, fileId];
      
      return { selectedFiles };
    });
  },

  selectAllFiles: () => {
    const { files } = get();
    set({ selectedFiles: files.map(file => file.id) });
  },

  clearSelection: () => {
    set({ selectedFiles: [] });
  }
}));