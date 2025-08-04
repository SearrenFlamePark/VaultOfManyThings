#!/usr/bin/env python3
"""
Gmail Token Generator for Atticus
Run this locally to generate OAuth tokens for GitHub Actions
"""

import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Gmail API scope for reading emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def generate_gmail_tokens():
    """Generate Gmail OAuth tokens for GitHub Actions"""
    
    print("🔧 Gmail Token Generator for Atticus")
    print("=" * 50)
    
    # Load credentials from JSON file
    creds_file = input("Enter path to your Gmail credentials JSON file: ").strip()
    
    if not os.path.exists(creds_file):
        print("❌ Credentials file not found!")
        return
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
        creds = flow.run_local_server(port=0)
        
        print("\n✅ Authentication successful!")
        print("\n🔑 ADD THESE GITHUB SECRETS:")
        print("=" * 40)
        
        print(f"\nSecret Name: GMAIL_ACCESS_TOKEN")
        print(f"Secret Value: {creds.token}")
        
        print(f"\nSecret Name: GMAIL_REFRESH_TOKEN") 
        print(f"Secret Value: {creds.refresh_token}")
        
        print(f"\nSecret Name: GMAIL_CLIENT_ID")
        with open(creds_file, 'r') as f:
            client_data = json.load(f)
            if 'installed' in client_data:
                client_info = client_data['installed']
            else:
                client_info = client_data['web']
            print(f"Secret Value: {client_info['client_id']}")
        
        print(f"\nSecret Name: GMAIL_CLIENT_SECRET")
        print(f"Secret Value: {client_info['client_secret']}")
        
        print("\n📋 NEXT STEPS:")
        print("1. Add all 4 secrets to your VaultOfManyThings repository")
        print("2. Let me know when they're added")
        print("3. I'll create the Gmail sync workflow!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you:")
        print("- Have the correct JSON file")
        print("- Enabled Gmail API in Google Cloud Console")
        print("- Configured OAuth consent screen")

if __name__ == "__main__":
    generate_gmail_tokens()