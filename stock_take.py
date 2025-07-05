# Import Libraries
import pandas as pd
import numpy as np
import openpyxl
from pathlib import Path
import streamlit as st

# Streamlit Page Config
st.set_page_config(page_title='🧾 Stock Taker', layout='wide')
st.title('🧾 Stock Take Dashboard')

# Upload Stock File
st.sidebar.header('📂 Upload Section')
st.sidebar.info('Export from PowerClinic: Inventory Management -> Stock Management -> Stock Take -> Print -> Excel')
stock_file = st.sidebar.file_uploader('Upload Stock Take Excel File (.xls)', type=['xls', 'xlsx'])

# Process File
if stock_file:
    if not stock_file.name.endswith(('.xls', '.xlsx')):
        st.error('❌ Invalid file format. Please upload an Excel file.')
        st.stop()

    # Read Excel
    stock = pd.read_excel(stock_file)
    stock = stock.dropna(how='all', axis=1).dropna(how='all').reset_index(drop=True)

    # Set and clean column headers
    stock.columns = stock.loc[6]
    stock.columns = [str(col).strip().lower().replace(' ', '_').replace('.', '').replace("'", '') for col in stock.columns]
    stock = stock.loc[7:].reset_index(drop=True)

    # Rename NaN columns
    new_columns = []
    counter = 0
    for col in stock.columns:
        if col == 'nan':
            counter += 1
            new_columns.append(f'na_{counter}')
        else:
            new_columns.append(col)
    stock.columns = new_columns

    # Merge and clean on_hand_qty
    stock['on_hand_qty'] = stock['on_hand_qty'].fillna(stock['na_3'])
    stock = stock.drop(columns=['na_1', 'na_2', 'na_3'], errors='ignore')
    stock = stock.dropna(how='all').reset_index(drop=True)
    stock = stock[stock['name'].notna()].reset_index(drop=True)
    stock = stock[stock['actual_qty'] != "Actual Q'ty"]
    stock['item_no'] = stock['item_no'].astype(str).str.strip()

    # Categorize items
    consume_df = stock[stock['item_no'].str.startswith('(C)')].copy()
    pharma_df = stock[~stock['item_no'].str.startswith('(C)')].copy()

    # Summary Metrics
    total_consume = consume_df.shape[0]
    total_pharma = pharma_df.shape[0]
    total_items = total_consume + total_pharma

    st.markdown("### 📊 Stock Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", total_items)
    col2.metric("Pharma Items", total_pharma)
    col3.metric("Consumables", total_consume)

    # Display Tables
    with st.expander("📦 View Pharma Items"):
        st.dataframe(pharma_df[['item_no', 'name', 'on_hand_qty']], use_container_width=True)

    with st.expander("🧻 View Consumables"):
        st.dataframe(consume_df[['item_no', 'name', 'on_hand_qty']], use_container_width=True)

    # Non-Tallied Item Calculator
    st.markdown("### 🧮 Non-Tallied Items Calculator")
    st.info("Enter the number of non-tallied pharma items (exclude consumables)")
    st.markdown("<span style='color: gray;'>🎯 KPI Requirement: Non-tallied items must be less than 5% of total pharma items ({:.0f}).</span>".format(total_pharma), unsafe_allow_html=True)

    non_tallied_input = st.text_input("Enter the Number of Non-Tallied Pharma Items", value="", placeholder="Enter a number")

    valid_input = False
    if non_tallied_input.strip() != "":
        try:
            non_tallied_total = int(non_tallied_input)
            if 0 <= non_tallied_total <= total_pharma:
                valid_input = True
            else:
                st.error(f"⚠️ Enter a number between 0 and {total_pharma}.")
        except ValueError:
            st.error("❌ Please enter a valid integer.")

    if valid_input:
        non_tallied_perc = np.round((non_tallied_total / total_pharma) * 100, 2)

        st.markdown("#### 📈 Non-Tallied Summary")
        st.write(f"- **Non-Tallied Items:** {non_tallied_total}")
        st.write(f"- **Percentage:** {non_tallied_perc}%")

        if non_tallied_perc == 0:
            st.success("🎉 Excellent! All items are tallied. Great attention to detail!")
        elif non_tallied_perc <= 5:
            st.warning("⚠️ Within KPI limits, but there's room for improvement.")
        else:
            st.error("❌ Non-tallied percentage exceeds 5%. Please review your stock management process.")
else:
    st.warning("📂 Please upload a stock take Excel file to begin.")
