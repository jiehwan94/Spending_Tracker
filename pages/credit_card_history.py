import streamlit as st
import pandas as pd
import os
from google_drive_utils import load_excel_from_drive
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Credit Card History",
    page_icon="💳",
    layout="wide"
)

def load_credit_card_data():
    """Load credit card history data from Google Drive"""
    # Import the functions we need
    from google_drive_utils import get_file_id_from_path, download_file_from_drive
    
    # Check if there's a specific file ID for credit card history
    credit_card_file_id = os.getenv("CREDIT_CARD_FILE_ID")
    if credit_card_file_id:
        file_id = credit_card_file_id
    else:
        # Search for file by path
        file_id = get_file_id_from_path("FINANCE", "크레딧카드_히스토리.xlsx")
        if not file_id:
            st.error("Could not find credit card history file in Google Drive")
            return pd.DataFrame()
    
    # Download the file temporarily
    temp_filename = "temp_credit_card_data.xlsx"
    if download_file_from_drive(file_id, temp_filename):
        try:
            # Load the correct sheet
            df = pd.read_excel(temp_filename, sheet_name="크레딧카드히스토리_v1")
            return df
        except Exception as e:
            st.error(f"Error loading credit card data: {e}")
            return pd.DataFrame()
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
            except:
                pass  # Ignore cleanup errors
    else:
        st.error("Failed to download file from Google Drive")
        return pd.DataFrame()

def main():
    st.subheader("📋 Credit Card History")
    
    # Load data
    with st.spinner("Loading credit card data from Google Drive..."):
        df = load_credit_card_data()
    
    if df.empty:
        st.error("No credit card data found. Please check the file path and sheet name.")
        return
    
    # Display basic info
    st.success(f"✅ Loaded {len(df)} credit card records")
    
    # Show data info
    col1, col2, col3, col4 = st.columns(4)
    
    # Filter for currently open cards (no closing date)
    open_cards = df[df['Closing Date'].isna()]
    
    with col1:
        st.metric("Currently Open Cards", len(open_cards))
    
    with col2:
        if 'Number of Cards Opened 24 months prior' in df.columns:
            # Get the last record's 5/24 count
            last_record = df.iloc[-1]
            five_twenty_four_count = last_record['Number of Cards Opened 24 months prior']
            st.metric("5/24 Counts", five_twenty_four_count)
        else:
            st.metric("5/24 Counts", "N/A")

    with col3:
        if 'Opening Date' in df.columns and 'Number of Cards Opened 24 months prior' in df.columns:
            # Convert Opening Date to datetime if needed
            if not pd.api.types.is_datetime64_any_dtype(df['Opening Date']):
                df['Opening Date'] = pd.to_datetime(df['Opening Date'])
            
            # Get current date
            current_date = datetime.now()
            
            # Find when we'll have less than 5 cards in 24 months
            target_month = None
            
            # Check each month from now until we find when 5/24 drops below 5
            for months_ahead in range(1, 25):  # Check up to 24 months ahead
                check_date = current_date + pd.DateOffset(months=months_ahead)
                
                # Count cards opened in the 24 months before this future date
                cards_in_24_months = 0
                for _, row in df.iterrows():
                    if pd.notna(row['Opening Date']):
                        # Check if card was opened within 24 months of the check date
                        months_diff = (check_date.year - row['Opening Date'].year) * 12 + (check_date.month - row['Opening Date'].month)
                        if 0 <= months_diff < 24:
                            cards_in_24_months += 1
                
                if cards_in_24_months < 5:
                    target_month = check_date
                    break
            
            if target_month:
                st.metric("5/24 < 5 by", target_month.strftime('%Y-%m'))
            else:
                st.metric("5/24 < 5 by", "Beyond 24 months")
        else:
            st.metric("5/24 < 5 by", "N/A")

    with col4:
        if len(open_cards) > 0 and 'Opening Date' in open_cards.columns:
            # Calculate average months for currently open cards
            
            # Convert Opening Date to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(open_cards['Opening Date']):
                open_cards['Opening Date'] = pd.to_datetime(open_cards['Opening Date'])
            
            # Calculate months since opening for each card
            current_date = datetime.now()
            months_open = []
            
            for opening_date in open_cards['Opening Date']:
                if pd.notna(opening_date):
                    # Calculate months between opening date and current date
                    months = (current_date.year - opening_date.year) * 12 + (current_date.month - opening_date.month)
                    months_open.append(months)
            
            if months_open:
                avg_months = sum(months_open) / len(months_open)
                st.metric("Average Months Open", f"{avg_months:.1f}")
            else:
                st.metric("Average Months Open", "N/A")
        else:
            st.metric("Average Months Open", "N/A")
    
    # Format the dataframe for better display
    display_df = df.copy()
    
    # Format date columns
    date_columns = ['Opening Date', 'Closing Date']
    for col in date_columns:
        if col in display_df.columns and pd.api.types.is_datetime64_any_dtype(display_df[col]):
            display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
    
    # Display the dataframe
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    main() 