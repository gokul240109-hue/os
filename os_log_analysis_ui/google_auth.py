"""
Google OAuth2 Authentication Module
Configure your Google OAuth2 credentials and set up authentication
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
import google.auth.oauthlib.flow

# Configuration - Replace with your Google OAuth2 credentials
# Get credentials from: https://console.cloud.google.com/
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID_HERE')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET_HERE')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8080/auth/google/callback')

# Scopes for Google OAuth
SCOPES = ['openid', 'email', 'profile']

def create_oauth_flow():
    """Create and return an OAuth2 flow object"""
    flow = google.auth.oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI)
    return flow

def get_authorization_url():
    """Generate Google authorization URL"""
    try:
        flow = create_oauth_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')
        return authorization_url, state
    except Exception as e:
        print(f"Error creating authorization URL: {e}")
        return None, None

def handle_oauth_callback(authorization_response, state):
    """Handle OAuth callback and get user info"""
    try:
        flow = create_oauth_flow()
        token = flow.fetch_token(authorization_response=authorization_response)
        
        # Get user info from token
        credentials = flow.credentials
        user_info = {
            'email': token.get('email'),
            'name': token.get('name'),
            'picture': token.get('picture'),
            'id': token.get('sub')
        }
        return user_info, token
    except Exception as e:
        print(f"Error in OAuth callback: {e}")
        return None, None

def verify_google_token(token):
    """Verify Google ID token"""
    try:
        idinfo = verify_oauth2_token(token, Request(), GOOGLE_CLIENT_ID)
        return idinfo
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None
