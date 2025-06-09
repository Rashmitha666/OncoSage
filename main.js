import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// Required to work with __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function createWindow() {
  const win = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile('index.html');
}

app.whenReady().then(createWindow);

// Handle JSON file save
ipcMain.on('save-report', async (event, data) => {
  const { filePath } = await dialog.showSaveDialog({
    title: 'Save Genomic Report',
    defaultPath: 'genomic_report.json',
    filters: [{ name: 'JSON', extensions: ['json'] }]
  });

  if (filePath) {
    fs.writeFileSync(filePath, data, 'utf-8');
  }
});
