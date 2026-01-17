"""
Google Sheets API Module
Handles OAuth flow and direct export to Google Sheets
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Credentials file path
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')

# In-memory token storage (for demo - use database in production)
user_tokens = {}


def get_oauth_flow(redirect_uri: str = "http://localhost:8000/oauth/callback") -> Flow:
    """Create and return an OAuth flow."""
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    return flow


def get_auth_url() -> tuple:
    """Get the authorization URL for Google OAuth."""
    flow = get_oauth_flow()
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url, state


def exchange_code_for_token(code: str, state: str) -> dict:
    """Exchange authorization code for tokens."""
    flow = get_oauth_flow()
    flow.fetch_token(code=code)
    
    credentials = flow.credentials
    
    # Store tokens
    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': list(credentials.scopes)
    }
    
    user_tokens['current'] = token_data
    return token_data


def get_credentials():
    """Get stored credentials if available."""
    if 'current' not in user_tokens:
        return None
    
    token_data = user_tokens['current']
    
    credentials = Credentials(
        token=token_data['token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )
    
    return credentials


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return 'current' in user_tokens


def create_spreadsheet_with_data(analysis: dict) -> dict:
    """
    Create a new Google Spreadsheet and populate it with analysis data.
    Returns the spreadsheet URL.
    """
    credentials = get_credentials()
    if not credentials:
        raise Exception("Not authenticated")
    
    try:
        service = build('sheets', 'v4', credentials=credentials)
        
        # Create spreadsheet
        target_role = analysis.get('target_role', 'Career Analysis')
        spreadsheet = {
            'properties': {
                'title': f'Career Analysis - {target_role}'
            },
            'sheets': [
                {
                    'properties': {
                        'title': 'Analysis',
                        'gridProperties': {
                            'frozenRowCount': 1
                        }
                    }
                }
            ]
        }
        
        result = service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = result['spreadsheetId']
        spreadsheet_url = result['spreadsheetUrl']
        
        # Get the actual sheet ID from the created spreadsheet
        sheet_id = result['sheets'][0]['properties']['sheetId']
        
        # Prepare data rows
        rows = []
        
        # Header row
        rows.append(['Career Analysis Report', '', ''])
        rows.append(['Target Role', analysis.get('target_role', ''), ''])
        rows.append(['Role Fit Score', f"{analysis.get('role_fit_score', 0)}%", ''])
        rows.append(['', '', ''])
        
        # Strengths
        rows.append(['STRENGTHS', '', ''])
        for strength in analysis.get('strengths', []):
            rows.append(['✓', strength, ''])
        rows.append(['', '', ''])
        
        # Skill Gaps
        rows.append(['SKILLS TO DEVELOP', '', ''])
        for skill in analysis.get('skill_gaps', {}).get('core', []):
            rows.append(['Core', skill, ''])
        for skill in analysis.get('skill_gaps', {}).get('supporting', []):
            rows.append(['Supporting', skill, ''])
        rows.append(['', '', ''])
        
        # Learning Roadmap
        rows.append(['LEARNING ROADMAP', '', ''])
        rows.append(['Skill', 'Priority', 'Time Estimate'])
        for item in analysis.get('roadmap', []):
            rows.append([
                item.get('skill', ''),
                item.get('priority', ''),
                item.get('estimated_time', '')
            ])
        rows.append(['', '', ''])
        
        # AI Insight
        rows.append(['AI MENTOR INSIGHT', '', ''])
        reflection = analysis.get('reflection', {})
        rows.append(['', reflection.get('reason', ''), ''])
        
        # Write data to sheet
        body = {'values': rows}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Analysis!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Format the spreadsheet (make headers bold, etc.)
        requests = [
            # Bold the title
            {
                'repeatCell': {
                    'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1},
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True, 'fontSize': 14}
                        }
                    },
                    'fields': 'userEnteredFormat.textFormat'
                }
            },
            # Auto-resize columns
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 3
                    }
                }
            }
        ]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        return {
            'spreadsheet_id': spreadsheet_id,
            'spreadsheet_url': spreadsheet_url,
            'success': True
        }
        
    except HttpError as error:
        return {
            'success': False,
            'error': str(error)
        }
