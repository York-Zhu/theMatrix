const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = require('electron-is-dev');
const log = require('electron-log');

// Configure logging
log.transports.file.level = 'info';
log.transports.console.level = 'info';

// Global references
let mainWindow;
let backendProcess = null;
let backendReady = false;

// Get the path to the backend executable
function getBackendPath() {
  if (isDev) {
    // In development, use the backend from the resources directory
    return path.join(process.cwd(), 'resources', 'twitter_alert_tool');
  } else {
    // In production, use the backend from the resources directory in the app bundle
    return path.join(process.resourcesPath, 'resources', 'twitter_alert_tool');
  }
}

// Start the backend process
function startBackendProcess() {
  try {
    const backendPath = getBackendPath();
    log.info(`Starting backend process from: ${backendPath}`);
    
    // Make the file executable on Unix-like systems
    if (process.platform !== 'win32') {
      require('fs').chmodSync(backendPath, '755');
    }
    
    // Spawn the backend process
    backendProcess = spawn(backendPath, [], {
      detached: false,
      stdio: ['ignore', 'pipe', 'pipe']
    });
    
    // Log backend output
    backendProcess.stdout.on('data', (data) => {
      const output = data.toString();
      log.info(`Backend stdout: ${output}`);
      
      // Check if the backend is ready
      if (output.includes('Started server process')) {
        backendReady = true;
        if (mainWindow) {
          mainWindow.webContents.send('backend-status', { status: 'ready' });
        }
      }
    });
    
    backendProcess.stderr.on('data', (data) => {
      log.error(`Backend stderr: ${data.toString()}`);
    });
    
    backendProcess.on('error', (error) => {
      log.error(`Backend process error: ${error.message}`);
      backendReady = false;
      if (mainWindow) {
        mainWindow.webContents.send('backend-status', { 
          status: 'error',
          message: error.message
        });
      }
    });
    
    backendProcess.on('close', (code) => {
      log.info(`Backend process exited with code ${code}`);
      backendReady = false;
      backendProcess = null;
      
      if (mainWindow) {
        mainWindow.webContents.send('backend-status', { 
          status: 'stopped',
          code: code
        });
      }
      
      // Restart the backend if it crashes and the app is still running
      if (code !== 0 && !app.isQuitting) {
        log.info('Restarting backend process...');
        setTimeout(startBackendProcess, 1000);
      }
    });
    
    return true;
  } catch (error) {
    log.error(`Failed to start backend process: ${error.message}`);
    return false;
  }
}

// Create the main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.cjs')
    }
  });
  
  // Load the app
  if (isDev) {
    // In development, load from the dev server
    mainWindow.loadURL('http://localhost:5173');
    // Open DevTools
    mainWindow.webContents.openDevTools();
  } else {
    // In production, load from the built files
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
  
  // Send the initial backend status
  if (backendReady) {
    mainWindow.webContents.send('backend-status', { status: 'ready' });
  } else {
    mainWindow.webContents.send('backend-status', { status: 'starting' });
  }
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App ready event
app.whenReady().then(() => {
  // Start the backend process
  startBackendProcess();
  
  // Create the main window
  createWindow();
  
  // On macOS, recreate the window when the dock icon is clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
  
  // Handle IPC messages from the renderer process
  ipcMain.handle('get-backend-status', () => {
    return { ready: backendReady };
  });
  
  ipcMain.handle('restart-backend', async () => {
    if (backendProcess) {
      log.info('Killing backend process...');
      backendProcess.kill();
      backendProcess = null;
    }
    
    // Wait a moment before restarting
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Start the backend process again
    const success = startBackendProcess();
    return { success };
  });
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Clean up before quitting
app.on('before-quit', () => {
  app.isQuitting = true;
  
  // Kill the backend process
  if (backendProcess) {
    log.info('Killing backend process...');
    backendProcess.kill();
    backendProcess = null;
  }
});
