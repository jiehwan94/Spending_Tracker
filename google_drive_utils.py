import os
import pandas as pd
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import gdown

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_google_drive_service():
    """Get Google Drive service with authentication"""
    creds = None
    
    # Check if we have valid credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # For Streamlit Cloud, we'll use service account or direct download
            return None
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def download_file_from_drive(file_id, filename):
    """Download file from Google Drive using file ID"""
    try:
        # Method 1: Using gdown (simpler, works with shared links)
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, filename, quiet=False)
        return True
    except Exception as e:
        st.error(f"Error downloading file: {e}")
        return False

def get_file_id_from_path(folder_name, file_name):
    """Get file ID from folder name and file name using Google Drive API"""
    service = get_google_drive_service()
    if not service:
        return None
    
    try:
        # First, find the folder
        folder_query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        folder_results = service.files().list(q=folder_query, spaces='drive').execute()
        folders = folder_results.get('files', [])
        
        if not folders:
            st.error(f"Folder '{folder_name}' not found in Google Drive")
            return None
        
        folder_id = folders[0]['id']
        
        # Then, find the file in that folder
        file_query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
        file_results = service.files().list(q=file_query, spaces='drive').execute()
        files = file_results.get('files', [])
        
        if not files:
            st.error(f"File '{file_name}' not found in folder '{folder_name}'")
            return None
        
        return files[0]['id']
    
    except Exception as e:
        st.error(f"Error finding file: {e}")
        return None

def load_excel_from_drive(folder_name, file_name, sheet_name):
    """Load Excel file from Google Drive"""
    
    # Method 1: Try using direct file ID (if provided in environment)
    file_id = os.getenv("GOOGLE_DRIVE_FILE_ID")
    
    if not file_id:
        # Method 2: Try to find file by path
        file_id = get_file_id_from_path(folder_name, file_name)
    
    if not file_id:
        st.error("Could not find file in Google Drive. Please check the file path or provide GOOGLE_DRIVE_FILE_ID in environment variables.")
        return pd.DataFrame()
    
    # Download the file
    temp_filename = f"temp_{file_name}_data.xlsx"
    if download_file_from_drive(file_id, temp_filename):
        try:
            # Load the Excel file
            df = pd.read_excel(temp_filename, sheet_name=sheet_name)
            
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            
            return df
        except Exception as e:
            st.error(f"Error loading Excel file: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def get_shared_link_info():
    """Get information about how to set up shared link"""
    st.info("""
    **To use Google Drive integration:**
    
    1. **Option A (Recommended)**: Get the file ID from Google Drive
       - Right-click on your Excel file in Google Drive
       - Click "Share" → "Copy link"
       - The link will be: `https://drive.google.com/file/d/FILE_ID_HERE/view`
       - Copy the FILE_ID_HERE part
    
    2. **Option B**: Set up Google Drive API credentials
       - Create a Google Cloud project
       - Enable Google Drive API
       - Create service account credentials
    
    3. **Add to environment variables:**
       ```
       GOOGLE_DRIVE_FILE_ID=your_file_id_here
       ```
    """)

def load_data_with_fallback():
    """Load data with fallback to local file if Google Drive fails"""
    
    # Try Google Drive first
    df = load_excel_from_drive(folder_name="FINANCE", file_name="가계부.xlsx", sheet_name="변동비")
    
    if df.empty:
        st.warning("Could not load from Google Drive. Trying local file...")
        
        # Fallback to local file
        try:
            df = pd.read_excel('data/transactions.xlsx', sheet_name="변동비")
            st.success("Loaded data from local file successfully.")
        except Exception as e:
            st.error(f"Could not load local file either: {e}")
            get_shared_link_info()
            return pd.DataFrame()
    
    # Convert date column to datetime if it's not already
    if '지출일' in df.columns:
        df['지출일'] = pd.to_datetime(df['지출일'])
    
    return df
