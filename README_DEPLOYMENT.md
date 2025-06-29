# Spending Tracker - Deployment Guide

This guide will help you deploy your spending tracker application with authentication to various cloud platforms.

## 🔐 Authentication Setup

Before deploying, update the credentials in `spending_tracker_auth.py`:

```python
valid_credentials = {
    "admin": hash_password("your_password_here"),  # Change this password
    # Add more users as needed
    # "user2": hash_password("password2"),
}
```

## 🚀 Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free)

1. **Create a GitHub Repository**
   - Push your code to GitHub
   - Make sure your repository is public (for free tier)

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set the main file path to: `spending_tracker_auth.py`
   - Click "Deploy"

3. **Environment Variables** (Optional)
   - Add environment variables for credentials (more secure)
   - Go to app settings → Secrets
   - Add your credentials as secrets

### Option 2: Heroku

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Deploy**
   ```bash
   heroku login
   heroku create your-spending-tracker
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set USERNAME=admin
   heroku config:set PASSWORD=your_password_here
   ```

### Option 3: Railway

1. **Connect to Railway**
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub repository
   - Railway will auto-detect and deploy

2. **Environment Variables**
   - Add your credentials in the Railway dashboard

### Option 4: Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy Web Service**
   - Click "New Web Service"
   - Connect your GitHub repository
   - Set build command: `pip install -r requirements_deploy.txt`
   - Set start command: `streamlit run spending_tracker_auth.py --server.port=$PORT --server.address=0.0.0.0`

## 🔧 Security Best Practices

### For Production Use:

1. **Use Environment Variables**
   ```python
   import os
   
   valid_credentials = {
       os.getenv("USERNAME", "admin"): hash_password(os.getenv("PASSWORD", "default_password"))
   }
   ```

2. **Add Rate Limiting**
   ```python
   # Add to your app
   import time
   
   if 'login_attempts' not in st.session_state:
       st.session_state.login_attempts = 0
       st.session_state.last_attempt = 0
   
   # Check rate limiting
   current_time = time.time()
   if current_time - st.session_state.last_attempt < 60:  # 1 minute cooldown
       st.error("Too many login attempts. Please wait.")
       return
   ```

3. **Use HTTPS**
   - Most cloud platforms provide HTTPS automatically
   - Ensure your app is served over HTTPS

## 📁 File Structure

```
Spending_Tracker/
├── spending_tracker_auth.py      # Main app with authentication
├── data/
│   └── transactions.xlsx         # Your data file
├── requirements_deploy.txt       # Dependencies for deployment
├── Procfile                      # Heroku configuration
├── setup.sh                      # Streamlit Cloud setup
├── .streamlit/
│   └── config.toml              # Streamlit configuration
└── README_DEPLOYMENT.md         # This file
```

## 🔄 Updating Your App

1. **Local Development**
   ```bash
   streamlit run spending_tracker_auth.py
   ```

2. **Deploy Updates**
   - Push changes to GitHub
   - Your cloud platform will auto-deploy (if connected)

## 🛠️ Troubleshooting

### Common Issues:

1. **Port Issues**
   - Make sure your app uses `$PORT` environment variable
   - Add `--server.address=0.0.0.0` for external access

2. **File Not Found**
   - Ensure your Excel file is in the correct path
   - Consider using cloud storage for data files

3. **Authentication Issues**
   - Check that credentials are properly set
   - Verify environment variables are configured

### Support:

- **Streamlit Cloud**: [docs.streamlit.io](https://docs.streamlit.io)
- **Heroku**: [devcenter.heroku.com](https://devcenter.heroku.com)
- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Render**: [render.com/docs](https://render.com/docs)

## 🔒 Security Notes

- Never commit passwords to version control
- Use environment variables for sensitive data
- Regularly update your dependencies
- Consider adding two-factor authentication for production use
- Monitor your app's usage and access logs

## 📊 Data Management

For production use, consider:
- Using a database instead of Excel files
- Implementing data backup strategies
- Adding data export functionality
- Setting up automated data updates 