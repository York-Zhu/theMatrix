# Twitter Following Tracker - Executable Packaging

This directory contains the code and configuration files needed to package the Twitter Following Tracker as a standalone executable application.

## Overview

The Twitter Following Tracker is packaged as a desktop application using Electron for the frontend and a PyInstaller-packaged Python backend. This allows the application to run directly on a user's machine without requiring separate installation of dependencies.

## Directory Structure

- `electron/`: Contains the Electron main process and preload scripts
- `package.json`: Configuration for Electron and electron-builder
- `INSTALL.md`: Installation guide for end users
- `USER_GUIDE.md`: User guide for the application

## Building the Executable

To build the executable:

1. Install dependencies:
   ```
   npm install
   ```

2. Build the frontend:
   ```
   cd frontend && npm run build
   ```

3. Package the backend:
   ```
   cd packaged_backend && pyinstaller twitter_alert_tool.spec
   ```

4. Copy the packaged backend to the resources directory:
   ```
   mkdir -p resources
   cp packaged_backend/dist/twitter_alert_tool resources/
   ```

5. Package the application:
   ```
   npm run package
   ```

The packaged application will be available in the `dist` directory.

## Supported Platforms

The application can be packaged for the following platforms:

- Windows (NSIS installer and portable executable)
- Linux (AppImage and Debian package)
- macOS (DMG)

## Configuration

The application uses the following environment variables:

- `TWITTER_API_KEY`: Your Twitter API key (default is provided)
- `SLACK_WEBHOOK_URL`: Your Slack webhook URL for notifications (optional)

These can be set in a `.env` file in the same directory as the executable.
