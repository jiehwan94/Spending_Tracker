import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import hashlib
import os
import time

from datetime import datetime, timedelta
from google_drive_utils import load_data_with_fallback


# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

# Page configuration
st.set_page_config(
    page_title="Spending Tracker",
    page_icon="💰",
    layout="wide"
)

# Authentication configuration
def init_authentication():
    """Initialize authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
        st.session_state.last_attempt = 0

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_available_usernames():
    """Get list of available usernames from environment variables (for debugging)"""
    usernames = []
    
    # Primary user
    primary_username = os.getenv("ST_USERNAME")
    if primary_username:
        usernames.append(primary_username)
    
    # Additional users
    i = 2
    while True:
        additional_username = os.getenv(f"ST_USERNAME_{i}")
        if additional_username:
            usernames.append(additional_username)
            i += 1
        else:
            break
    
    return usernames

def check_credentials(username, password):
    """Check user credentials using environment variables"""
    # Get credentials from environment variables (more secure)
    env_username = os.getenv("ST_USERNAME")
    env_password = os.getenv("ST_PASSWORD")
    
    # Check if environment variables are set
    if not env_username or not env_password:
        # For local development, provide helpful instructions
        st.error("⚠️ Environment variables not configured.")
        st.info("💡 **For local development**: Create a `.env` file with your credentials or set environment variables.")
        st.code("ST_USERNAME=your_username\nST_PASSWORD=your_password", language="bash")
        st.info("💡 **For Streamlit Cloud**: Go to app settings → Secrets and add your credentials.")
        return False
    
    # Check environment variables
    if username == env_username and hash_password(password) == hash_password(env_password):
        return True
    
    # If you want to support multiple users, you can add them as additional environment variables
    # For example: ST_USERNAME_2, ST_PASSWORD_2, etc.
    additional_users = []
    i = 2
    while True:
        additional_username = os.getenv(f"ST_USERNAME_{i}")
        additional_password = os.getenv(f"ST_PASSWORD_{i}")
        if additional_username and additional_password:
            additional_users.append((additional_username, additional_password))
            i += 1
        else:
            break
    
    # Check additional users
    for additional_username, additional_password in additional_users:
        if username == additional_username and hash_password(password) == hash_password(additional_password):
            return True
    
    return False

def login_page():
    """Display login page with rate limiting"""
    st.title("🔐 Spending Tracker Login")
    st.markdown("Please enter your credentials to access the spending tracker.")
    
    # Check if environment variables are configured
    available_usernames = get_available_usernames()
    if not available_usernames:
        st.error("⚠️ **Configuration Error**: Environment variables not set. Please configure ST_USERNAME and ST_PASSWORD in Streamlit Cloud secrets.")
        st.info("💡 **To fix this**: Go to your Streamlit Cloud app settings → Secrets and add your credentials.")
        return
    
    # Rate limiting
    current_time = time.time()
    if st.session_state.login_attempts >= 3:
        if current_time - st.session_state.last_attempt < 300:  # 5 minute lockout
            remaining_time = int(300 - (current_time - st.session_state.last_attempt))
            st.error(f"Too many login attempts. Please wait {remaining_time} seconds before trying again.")
            return
        else:
            st.session_state.login_attempts = 0
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            st.session_state.last_attempt = current_time
            if check_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.login_attempts = 0
                st.success("Login successful!")
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                st.error(f"Invalid username or password. Attempt {st.session_state.login_attempts}/3")
    
    # Debug information (only show in development)
    try:
        debug_mode = st.secrets.get("DEBUG_MODE", False)
    except:
        # If secrets file doesn't exist (local development), check environment variable
        debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    if debug_mode:
        with st.expander("🔧 Debug Information"):
            st.write(f"Available usernames: {', '.join(available_usernames)}")
            st.write(f"Environment variables configured: {len(available_usernames) > 0}")
    
    # Add some styling
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p>💰 Private Spending Tracker Application</p>
        <p>Contact administrator for access credentials</p>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes to allow for data updates
def load_data():
    """Load data from Google Drive with fallback to local file"""
    return load_data_with_fallback()

def main_app():
    """Main application after authentication"""
    # Add logout button in sidebar
    with st.sidebar:
        st.markdown(f"**Welcome, {st.session_state.username}!**")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    # Title and description
    st.title("💰 Spending Tracker")
    st.markdown("Track and analyze your spending patterns")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("No data loaded. Please check the Excel file.")
        return
    
    # Sidebar for filters
    st.sidebar.header("Filters")
    
    # Date range filter
    min_date = df['지출일'].min()
    max_date = df['지출일'].max()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    # Category filter
    categories = ['All'] + sorted(df['카테고리'].unique().tolist())
    selected_category = st.sidebar.selectbox("Select Category", categories)
    
    # Apply filters
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[
            (df['지출일'].dt.date >= start_date) &
            (df['지출일'].dt.date <= end_date)
        ]
    else:
        filtered_df = df.copy()
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['카테고리'] == selected_category]
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Spending Overview")
        total_spending = filtered_df['금액'].sum()
        avg_spending = filtered_df['금액'].mean()
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Total Spending", f"${total_spending:,.0f}")
        with metric_col2:
            st.metric("Average per Transaction", f"${avg_spending:,.0f}")
        with metric_col3:
            st.metric("Number of Transactions", len(filtered_df))
    
    with col2:
        st.subheader("🔍 Search Records")
        search_term = st.text_input("Search by name, category, or notes:")
        
        if search_term:
            search_results = filtered_df[
                filtered_df['이름'].str.contains(search_term, case=False, na=False) |
                filtered_df['카테고리'].str.contains(search_term, case=False, na=False) |
                filtered_df['비고'].str.contains(search_term, case=False, na=False)
            ]
            st.write(f"Found {len(search_results)} matching records")
        else:
            search_results = filtered_df.copy()
    
    # Data table
    st.subheader("📋 Transaction Records")
    
    # Display search results or filtered data
    display_df = search_results if search_term else filtered_df
    
    if not display_df.empty:
        # Format the dataframe for display
        display_df_formatted = display_df.copy()
        display_df_formatted['지출일'] = display_df_formatted['지출일'].dt.strftime('%Y-%m-%d')
        display_df_formatted['금액'] = display_df_formatted['금액'].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(
            display_df_formatted,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No transactions found matching your criteria.")
    
    # Visualizations
    st.subheader("📈 Spending Analysis")
    
    if not filtered_df.empty:
        # Create tabs for different time periods
        tab1, tab2, tab3, tab4 = st.tabs(["By Category", "Monthly", "Weekly", "Daily"])
        
        with tab1:
            # Spending by category
            category_spending = filtered_df.groupby('카테고리')['금액'].sum().sort_values(ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart - sorted by largest to smallest
                fig_pie = px.pie(
                    values=category_spending.values,
                    names=category_spending.index,
                    title="Spending by Category (Pie Chart)"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Bar chart
                fig_bar = px.bar(
                    x=category_spending.index,
                    y=category_spending.values,
                    title="Spending by Category (Bar Chart)",
                    labels={'x': 'Category', 'y': 'Amount ($)'}
                )
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        with tab2:
            # Monthly spending - using a different approach to avoid column conflicts
            filtered_df_copy = filtered_df.copy()
            filtered_df_copy['Year'] = filtered_df_copy['지출일'].dt.year
            filtered_df_copy['Month'] = filtered_df_copy['지출일'].dt.month
            
            monthly_spending = filtered_df_copy.groupby(['Year', 'Month'])['금액'].sum().reset_index()
            monthly_spending['Month_Label'] = monthly_spending.apply(
                lambda x: f"{int(x['Year'])}-{int(x['Month']):02d}", axis=1
            )
            
            fig_monthly = px.line(
                monthly_spending,
                x='Month_Label',
                y='금액',
                title="Monthly Spending Trend",
                labels={'금액': 'Amount ($)', 'Month_Label': 'Month'}
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
            
            # Monthly spending by category
            filtered_df_copy['Period'] = filtered_df_copy['지출일'].dt.to_period('M')
            monthly_category = filtered_df_copy.groupby(['Period', '카테고리'])['금액'].sum().reset_index()
            monthly_category['Month'] = monthly_category['Period'].astype(str)
            
            fig_monthly_category = px.bar(
                monthly_category,
                x='Month',
                y='금액',
                color='카테고리',
                title="Monthly Spending by Category",
                labels={'금액': 'Amount ($)', 'Month': 'Month'}
            )
            fig_monthly_category.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_monthly_category, use_container_width=True)
        
        with tab3:
            # Weekly spending
            weekly_spending = filtered_df.groupby([
                filtered_df['지출일'].dt.isocalendar().week
            ])['금액'].sum().reset_index()
            weekly_spending.columns = ['Week', 'Amount']
            
            fig_weekly = px.line(
                weekly_spending,
                x='Week',
                y='Amount',
                title="Weekly Spending Trend",
                labels={'Amount': 'Amount ($)', 'Week': 'Week Number'}
            )
            st.plotly_chart(fig_weekly, use_container_width=True)
        
        with tab4:
            # Daily spending
            daily_spending = filtered_df.groupby('지출일')['금액'].sum().reset_index()
            
            fig_daily = px.line(
                daily_spending,
                x='지출일',
                y='금액',
                title="Daily Spending Trend",
                labels={'금액': 'Amount ($)', '지출일': 'Date'}
            )
            st.plotly_chart(fig_daily, use_container_width=True)
    
    # Additional insights
    if not filtered_df.empty:
        st.subheader("💡 Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top spending categories
            top_categories = filtered_df.groupby('카테고리')['금액'].sum().nlargest(3)
            st.write("**Top 3 Spending Categories:**")
            for i, (category, amount) in enumerate(top_categories.items(), 1):
                st.write(f"{i}. {category}: ${amount:,.0f}")
        
        with col2:
            # Spending patterns
            st.write("**Spending Patterns:**")
            most_expensive = filtered_df.loc[filtered_df['금액'].idxmax()]
            st.write(f"Most expensive transaction: {most_expensive['이름']} (${most_expensive['금액']:,.0f})")
            
            avg_daily = filtered_df.groupby('지출일')['금액'].sum().mean()
            st.write(f"Average daily spending: ${avg_daily:,.0f}")
            
            # Average daily spending on 식비 (food expenses)
            food_expenses = filtered_df[filtered_df['카테고리'] == '식비']
            if not food_expenses.empty:
                avg_daily_food = food_expenses.groupby('지출일')['금액'].sum().mean()
                st.write(f"Average daily spending on 식비: ${avg_daily_food:,.0f}")
            else:
                st.write("No 식비 transactions found in the selected period.")

def main():
    """Main function with authentication"""
    init_authentication()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main() 