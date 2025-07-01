# Local Development Setup Guide

## 🔧 Setting Up Environment Variables for Local Development

### Method 1: Using .env file (Recommended)

1. **Install python-dotenv** (if not already installed):
   ```bash
   pip install python-dotenv
   ```

2. **Create a .env file** in your project root:
   ```bash
   # Windows
   copy local_env.txt .env
   
   # Mac/Linux
   cp local_env.txt .env
   ```

3. **Edit the .env file** with your credentials:
   ```env
   ST_USERNAME=admin
   ST_PASSWORD=your_secure_password
   
   # Optional: Add more users
   ST_USERNAME_2=user2
   ST_PASSWORD_2=user2pass
   
   # Optional: Enable debug mode
   DEBUG_MODE=true
   ```

4. **Run your app**:
   ```bash
   streamlit run spending_tracker_secure.py
   ```

### Method 2: Set Environment Variables in Terminal

#### Windows (PowerShell):
```powershell
$env:ST_USERNAME="admin"
$env:ST_PASSWORD="your_password"
streamlit run spending_tracker_secure.py
```

#### Windows (Command Prompt):
```cmd
set ST_USERNAME=admin
set ST_PASSWORD=your_password
streamlit run spending_tracker_secure.py
```

#### Mac/Linux:
```bash
export ST_USERNAME=admin
export ST_PASSWORD=your_password
streamlit run spending_tracker_secure.py
```

### Method 3: One-liner (Mac/Linux)
```bash
ST_USERNAME=admin ST_PASSWORD=your_password streamlit run spending_tracker_secure.py
```

## 🔒 Security Notes

1. **Never commit .env files** to version control
2. **Add .env to .gitignore**:
   ```
   .env
   *.env
   ```
3. **Use strong passwords** even for local development
4. **Keep .env files secure** on your local machine

## 🐛 Troubleshooting

### If you still get "Environment variables not configured":

1. **Check if .env file exists** in the project root
2. **Verify the format** of your .env file (no spaces around =)
3. **Restart your terminal** after setting environment variables
4. **Check if python-dotenv is installed**:
   ```bash
   pip install python-dotenv
   ```

### If you get import errors:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Check Python path** and virtual environment

## 📝 Example .env file

```env
# Primary user
ST_USERNAME=admin
ST_PASSWORD=MySecurePassword123!

# Additional users (optional)
ST_USERNAME_2=user1
ST_PASSWORD_2=User1Password456!

ST_USERNAME_3=user2
ST_PASSWORD_3=User2Password789!

# Debug mode (optional)
DEBUG_MODE=true
```

## 🔄 Switching Between Local and Cloud

- **Local development**: Use .env file or terminal environment variables
- **Streamlit Cloud**: Use the Secrets section in app settings
- **Other platforms**: Use their respective environment variable configuration

The app will automatically detect and use the appropriate method based on what's available. 