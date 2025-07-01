# Streamlit Cloud Environment Variables Setup

## 🔐 How to Configure Environment Variables in Streamlit Cloud

### Step 1: Access Your App Settings
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Find your deployed app and click on it
4. Click on the **"Settings"** button (gear icon)

### Step 2: Configure Secrets
1. In the settings page, scroll down to **"Secrets"** section
2. Click on **"Edit secrets"**
3. Add your credentials in the following format:

```toml
ST_USERNAME = "your_username"
ST_PASSWORD = "your_secure_password"
```

### Step 3: Add Multiple Users (Optional)
If you want to add multiple users, you can add additional credentials:

```toml
ST_USERNAME = "admin"
ST_PASSWORD = "admin_password"

ST_USERNAME_2 = "user2"
ST_PASSWORD_2 = "user2_password"

ST_USERNAME_3 = "user3"
ST_PASSWORD_3 = "user3_password"
```

### Step 4: Save and Deploy
1. Click **"Save"** to save your secrets
2. Your app will automatically redeploy with the new configuration
3. Wait for the deployment to complete

## 🔧 How the Code Reads Environment Variables

The updated `spending_tracker_secure.py` now:

1. **Reads from environment variables**: Uses `os.getenv()` to get credentials
2. **No hardcoded passwords**: Removes all hardcoded credentials for security
3. **Supports multiple users**: Can handle multiple username/password pairs
4. **Better error handling**: Shows clear error messages if variables aren't set
5. **Debug mode**: Optional debug information for troubleshooting

## 🚨 Security Best Practices

1. **Use strong passwords**: Make sure your passwords are secure
2. **Don't share secrets**: Never commit secrets to your GitHub repository
3. **Regular rotation**: Change passwords periodically
4. **Monitor access**: Check your app's usage logs

## 🐛 Troubleshooting

### If login doesn't work:
1. Check that environment variables are set correctly
2. Verify username and password match exactly
3. Check for typos in the secrets configuration
4. Wait for the app to redeploy after saving secrets

### If you see "Environment variables not configured":
1. Go to your app settings
2. Check that ST_USERNAME and ST_PASSWORD are set
3. Make sure there are no extra spaces or quotes
4. Save and wait for redeployment

## 📝 Example Secrets Configuration

```toml
# Single user setup
ST_USERNAME = "admin"
ST_PASSWORD = "MySecurePassword123!"

# Multiple users setup
ST_USERNAME = "admin"
ST_PASSWORD = "AdminPassword123!"

ST_USERNAME_2 = "user1"
ST_PASSWORD_2 = "User1Password456!"

ST_USERNAME_3 = "user2"
ST_PASSWORD_3 = "User2Password789!"
```

## 🔄 Updating Credentials

To update credentials:
1. Go to app settings → Secrets
2. Edit the values
3. Click Save
4. App will automatically redeploy

The new credentials will be active immediately after deployment. 