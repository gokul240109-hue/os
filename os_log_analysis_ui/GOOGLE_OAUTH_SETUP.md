# Google OAuth2 Setup Guide

This application now supports Google Login! Follow these steps to set it up.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown and select **New Project**
3. Enter a project name (e.g., "OS Log Analysis") and click **Create**
4. Wait for the project to be created

## Step 2: Create OAuth2 Credentials

1. In the Google Cloud Console, go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. If prompted, first click **Configure Consent Screen** and fill in:
   - **App name**: OS Log Analysis
   - **User support email**: your-email@example.com
   - **Scopes**: Select `email`, `profile`, and `openid`
   - Complete and save

4. Now go back to **Credentials** and click **+ CREATE CREDENTIALS** > **OAuth client ID** again
5. Select **Web application**
6. Add Authorized redirect URIs:
   - `http://localhost:8080/auth/google/callback`
   - `http://127.0.0.1:8080/auth/google/callback`
   - (If deploying to production, add your production domain)

7. Click **Create**
8. Copy the **Client ID** and **Client Secret**

## Step 3: Set Environment Variables

Choose one of these methods:

### Option A: Set as System Environment Variables (Windows)

1. Press `Win + X` and select **System**
2. Click **Advanced system settings**
3. Click **Environment Variables**
4. Under **User variables**, click **New** and add:
   - Variable name: `GOOGLE_CLIENT_ID`
   - Variable value: `[paste your Client ID]`
5. Click **New** again and add:
   - Variable name: `GOOGLE_CLIENT_SECRET`
   - Variable value: `[paste your Client Secret]`
6. Click **OK** and restart VS Code/Terminal

### Option B: Create a `.env` File

Create a `.env` file in your project root:

```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

Then update `app.py` to load from `.env`:

```python
from dotenv import load_dotenv
load_dotenv()
```

First install python-dotenv:
```bash
pip install python-dotenv
```

### Option C: Set in Terminal (Temporary)

For Windows PowerShell:
```powershell
$env:GOOGLE_CLIENT_ID = "your_client_id_here"
$env:GOOGLE_CLIENT_SECRET = "your_client_secret_here"
```

## Step 4: Test Google Login

1. Restart your Flask application
2. Go to http://localhost:8080 or http://127.0.0.1:8080
3. Click **Continue with Google**
4. Sign in with your Google account
5. You'll be automatically logged in and redirected to the dashboard

## Troubleshooting

### "Google OAuth not configured"
- Make sure environment variables are set correctly
- Check that `GOOGLE_CLIENT_ID` doesn't contain "YOUR_GOOGLE_CLIENT_ID_HERE"

### "redirect_uri_mismatch"
- The redirect URI in your Google Cloud Console must exactly match the one in your app
- Make sure to add BOTH `localhost` and `127.0.0.1` variants if testing locally

### "Invalid Client"
- Double-check that your Client ID and Client Secret are correct
- Make sure they're copied completely without extra spaces

### Login page shows error
- Check the Flask console for detailed error messages
- Make sure the `google-auth-oauthlib` and `google-auth-httplib2` packages are installed

## Security Notes

1. **Never commit credentials** to version control
2. Keep your `Client Secret` private
3. Use environment variables or `.env` files (in .gitignore)
4. Restrict OAuth URLs to your domain in production
5. Users created via Google login are assigned the "Analyst" role by default

## What Happens Next

When a user logs in with Google:
1. The app verifies their Google account
2. Creates a new user account in your database (if first-time login)
3. Sets up a session and logs them in
4. Stores their Google profile picture in the session (optional for future use)

Enjoy Google OAuth integration! 🎉
