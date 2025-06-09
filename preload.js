// preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  saveReport: (data) => ipcRenderer.send('save-report', data)
});
