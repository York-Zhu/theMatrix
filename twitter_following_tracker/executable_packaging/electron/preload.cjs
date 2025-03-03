const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  restartBackend: () => ipcRenderer.invoke('restart-backend'),
  onBackendStatusChange: (callback) => {
    ipcRenderer.on('backend-status', (_, status) => callback(status));
    return () => {
      ipcRenderer.removeAllListeners('backend-status');
    };
  }
});
