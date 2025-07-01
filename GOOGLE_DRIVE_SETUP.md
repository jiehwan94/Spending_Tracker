# Google Drive Integration Setup Guide

## 🔧 How to Connect Your Google Drive Excel File

### Method 1: Using File ID (Recommended - Easiest)

#### Step 1: Get Your File ID
1. **Go to Google Drive** and find your `가계부.xlsx` file in the `FINANCE` folder
2. **Right-click** on the file and select **"Share"**
3. **Click "Copy link"**
4. The link will look like: `https://drive.google.com/file/d/1ABC123DEF456GHI789JKL/view?usp=sharing`
5. **Copy the file ID** (the part between `/d/` and `/view`): `1ABC123DEF456GHI789JKL`

#### Step 2: Set Environment Variable
**For Local Development:**
1. Edit your `.env` file:
   ```env
   GOOGLE_DRIVE_FILE_ID=1ABC123DEF456GHI789JKL
   ```

**For Streamlit Cloud:**
1. Go to your app settings → Secrets
2. Add:
   ```toml
   GOOGLE_DRIVE_FILE_ID = "1ABC123DEF456GHI789JKL"
   ```

#### Step 3: Make File Accessible
1. **Right-click** on your Excel file in Google Drive
2. **Click "Share"**
3. **Change to "Anyone with the link"** can view
4. **Click "Done"**

### Method 2: Using Google Drive API (Advanced)

If Method 1 doesn't work, you can set up full Google Drive API access:

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API

#### Step 2: Create Service Account
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Download the JSON key file

#### Step 3: Set Up Credentials
1. Save the JSON file as `service-account-key.json` in your project
2. Add to environment variables:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json
   ```

## 🚀 Testing the Integration

### Local Testing
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your .env file** with the file ID

3. **Run the app:**
   ```bash
   streamlit run spending_tracker_secure.py
   ```

### Streamlit Cloud Deployment
1. **Push your changes** to GitHub
2. **Add the file ID** to Streamlit Cloud secrets
3. **Deploy** - the app will automatically use Google Drive

## 📊 How It Works

### Data Flow:
1. **App starts** → Checks for Google Drive file ID
2. **Downloads file** → Temporarily from Google Drive
3. **Loads data** → Into pandas DataFrame
4. **Cleans up** → Removes temporary file
5. **Caches data** → For 5 minutes (allows updates)

### Benefits:
- ✅ **Real-time updates** - Change your Excel file, refresh the app
- ✅ **No redeployment** - Update data without pushing code
- ✅ **Backup system** - Falls back to local file if Drive fails
- ✅ **Secure** - Uses environment variables for file ID

## 🔒 Security Considerations

1. **File permissions** - Set to "Anyone with link can view"
2. **Environment variables** - Never commit file IDs to version control
3. **Temporary files** - Automatically cleaned up after loading
4. **Caching** - Data cached for 5 minutes to reduce API calls

## 🐛 Troubleshooting

### "Could not find file in Google Drive"
- Check that the file ID is correct
- Verify the file is shared with "Anyone with link can view"
- Make sure the file name matches exactly: `가계부.xlsx`

### "Error downloading file"
- Check your internet connection
- Verify the file ID is valid
- Try refreshing the app

### "Sheet not found"
- Make sure the sheet name is exactly `변동비`
- Check that the Excel file structure matches expectations

## 📝 Example Environment Variables

### Local Development (.env):
```env
ST_USERNAME=admin
ST_PASSWORD=admin123
GOOGLE_DRIVE_FILE_ID=1ABC123DEF456GHI789JKL
DEBUG_MODE=true
```

### Streamlit Cloud (Secrets):
```toml
ST_USERNAME = "admin"
ST_PASSWORD = "admin123"
GOOGLE_DRIVE_FILE_ID = "1ABC123DEF456GHI789JKL"
DEBUG_MODE = true
```

## 🔄 Updating Your Data

1. **Edit your Excel file** in Google Drive
2. **Save the changes**
3. **Refresh your Streamlit app** (or wait 5 minutes for cache to expire)
4. **Your changes will appear** automatically!

No need to redeploy or restart the app - just update your Excel file and refresh! 🎉 