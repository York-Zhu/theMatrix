# User Guide

This document provides instructions for using the Twitter Following Tracker application.

## Getting Started

After installing the application, launch it from your applications menu or desktop shortcut. The application will open in a window with two main tabs:

1. **Tracked Users**: View and manage the Twitter users you are tracking.
2. **New Followings**: View the new accounts that your tracked users have followed.

## Managing Tracked Users

### Viewing Tracked Users

The "Tracked Users" tab displays a list of all the Twitter users you are currently tracking. For each user, you can see:

- Their Twitter handle
- Their display name
- When their following list was last updated

### Adding a User to Track

To add a new Twitter user to track:

1. Go to the "Tracked Users" tab.
2. Enter the Twitter handle (without the @ symbol) in the input field.
3. Click the "Add User" button.

The user will be added to your tracking list, and their following list will be fetched automatically.

### Removing a User from Tracking

To remove a user from your tracking list:

1. Go to the "Tracked Users" tab.
2. Find the user you want to remove.
3. Click the trash icon next to their name.
4. Confirm the removal in the dialog that appears.

## Viewing New Followings

### Checking New Followings

The "New Followings" tab displays all the new accounts that your tracked users have followed since you started tracking them. For each new following, you can see:

- The Twitter handle of the new following
- The display name of the new following
- Which tracked user followed them
- When the following was detected

### Updating Following Lists

To check for new followings:

1. Go to the "New Followings" tab.
2. Click the "Update All" button to fetch the latest following lists for all tracked users.

The application will check for new followings and display them in the list.

### Viewing on Twitter

To view a user or following on Twitter:

1. Click the external link icon next to any Twitter handle.
2. This will open the Twitter profile in your default web browser.

## Slack Notifications

If you have configured a Slack webhook URL, the application will send notifications to your Slack channel whenever new followings are detected. The notifications include:

- The Twitter handle of the tracked user
- The Twitter handle of the new following
- A link to the new following's Twitter profile

To configure Slack notifications, set the `SLACK_WEBHOOK_URL` environment variable as described in the installation guide.

## Troubleshooting

### Backend Service Issues

If the application displays a message about the backend service being unavailable:

1. Check that your internet connection is working.
2. Click the "Restart Backend" button to attempt to restart the service.
3. If the issue persists, restart the application.

### Data Not Updating

If you're not seeing new followings or the data seems outdated:

1. Click the refresh button on the respective tab.
2. Check that the Twitter API is working correctly.
3. Ensure that the Twitter handles you're tracking are valid and active.

## Feedback and Support

If you encounter any issues or have suggestions for improving the application, please report them on the GitHub repository.
