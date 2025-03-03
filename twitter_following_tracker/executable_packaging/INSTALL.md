# Installation Guide

This document provides instructions for installing the Twitter Following Tracker application on different operating systems.

## Windows

### Installation with Installer

1. Download the `Twitter Following Tracker Setup.exe` file from the releases page.
2. Double-click the downloaded file to start the installation process.
3. Follow the on-screen instructions to complete the installation.
4. After installation, you can launch the application from the Start menu or desktop shortcut.

### Portable Version

1. Download the `Twitter Following Tracker.exe` file from the releases page.
2. Place the file in any directory of your choice.
3. Double-click the file to run the application without installation.

## macOS

1. Download the `Twitter Following Tracker.dmg` file from the releases page.
2. Double-click the downloaded file to open the disk image.
3. Drag the Twitter Following Tracker application to the Applications folder.
4. Open the application from the Applications folder or Launchpad.

## Linux

### AppImage

1. Download the `Twitter Following Tracker.AppImage` file from the releases page.
2. Make the file executable: `chmod +x Twitter\ Following\ Tracker.AppImage`
3. Run the application: `./Twitter\ Following\ Tracker.AppImage`

### Debian/Ubuntu

1. Download the `twitter-following-tracker_1.0.0_amd64.deb` file from the releases page.
2. Install the package: `sudo dpkg -i twitter-following-tracker_1.0.0_amd64.deb`
3. If there are dependency issues, run: `sudo apt-get install -f`
4. Launch the application from the applications menu or by running `twitter-following-tracker` in the terminal.

## Configuration

The application uses the following environment variables:

- `TWITTER_API_KEY`: Your Twitter API key (default is provided)
- `SLACK_WEBHOOK_URL`: Your Slack webhook URL for notifications (optional)

You can set these variables in a `.env` file in the same directory as the executable.

## Troubleshooting

If you encounter any issues during installation or while running the application, please check the following:

1. Make sure your system meets the minimum requirements.
2. Check if you have the necessary permissions to install or run the application.
3. For Linux users, ensure that the AppImage file has executable permissions.
4. If the application fails to start, check the log files in the following locations:
   - Windows: `%USERPROFILE%\AppData\Roaming\Twitter Following Tracker\logs`
   - macOS: `~/Library/Logs/Twitter Following Tracker`
   - Linux: `~/.config/Twitter Following Tracker/logs`

If the issue persists, please report it on the GitHub repository.
