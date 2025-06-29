import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Spending Tracker",
    page_icon="💰",
    layout="wide"
)

# Title and description
st.title("💰 Spending Tracker")
st.markdown("Track and analyze your spending patterns")

@st.cache_data
def load_data():
    """Load data from Excel file"""
    try:
        df = pd.read_excel('data/transactions.xlsx', sheet_name="변동비")
        # Convert date column to datetime if it's not already
        df['지출일'] = pd.to_datetime(df['지출일'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def main():
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

if __name__ == "__main__":
    main() 