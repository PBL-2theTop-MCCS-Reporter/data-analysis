import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import dask.dataframe as dd
from datetime import datetime, timedelta
import warnings
import retail_llm_insights

# Suppress warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="MCCS Retail Sales Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2563EB;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 1rem;
        color: #4B5563;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">MCCS Retail Sales Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown('Interactive analysis of Marine Corps Community Services retail sales data (Dec 2024 - Jan 2025)')

# Sidebar
st.sidebar.title("Filters & Controls")
st.sidebar.markdown("Use these filters to explore the data")

# Function to load data
@st.cache_data
def load_data():
    """Load the retail data and return as a pandas DataFrame"""
    # For initial loading, we'll use a smaller sample to make the app responsive
    # In a production environment, you might want to use Dask for the full dataset
    
    st.info("Loading data... This may take a few minutes for the first run.")
    
    try:
        # Try to load a cached version if it exists
        if os.path.exists('retail_data_sample.parquet'):
            df = pd.read_parquet('retail_data_sample.parquet')
            st.success("Loaded data from cache.")
        else:
            # Define file paths
            csv_path = 'data/convertedcsv/MCCS_RetailData.csv'
            parquet_path = 'data/rawdata/MCCS_RetailData.parquet'
            
            # Try to load from CSV first, then Parquet if CSV doesn't exist
            if os.path.exists(csv_path):
                st.info(f"Loading from CSV file: {csv_path}")
                ddf = dd.read_csv(csv_path, assume_missing=True, blocksize="64MB")
            elif os.path.exists(parquet_path):
                st.info(f"Loading from Parquet file: {parquet_path}")
                ddf = dd.read_parquet(parquet_path)
            else:
                raise FileNotFoundError("Could not find retail data in CSV or Parquet format")
            
            # Take a sample for interactive analysis
            # In a real app, you might want to use the full dataset with Dask
            # or implement more sophisticated sampling
            df = ddf.sample(frac=0.1).compute()
            
            # Convert date columns - using flexible format detection
            df['SALE_DATE'] = pd.to_datetime(df['SALE_DATE'], errors='coerce')
            df['SALE_DATE_TIME'] = pd.to_datetime(df['SALE_DATE_TIME'], errors='coerce')
            
            # Add derived columns
            df['MONTH'] = df['SALE_DATE'].dt.month
            df['MONTH_NAME'] = df['SALE_DATE'].dt.month_name()
            df['DAY_OF_WEEK'] = df['SALE_DATE'].dt.day_name()
            df['HOUR'] = df['SALE_DATE_TIME'].dt.hour
            df['IS_RETURN'] = df['RETURN_IND'] == 'Y'
            
            # Save to parquet for faster loading next time
            df.to_parquet('retail_data_sample.parquet')
            st.success("Data loaded and cached for future use.")
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Create a small sample dataset for demonstration
        df = pd.DataFrame({
            'SALE_DATE': pd.date_range(start='2024-12-01', end='2025-01-31'),
            'EXTENSION_AMOUNT': np.random.randint(10, 1000, size=62),
            'STORE_FORMAT': np.random.choice(['MAIN STORE', 'MARINE MART'], size=62),
            'COMMAND_NAME': np.random.choice(['29 PALMS', 'YUMA', 'CAMP PENDLETON'], size=62),
            'ITEM_DESC': np.random.choice(['PRODUCT A', 'PRODUCT B', 'PRODUCT C'], size=62),
            'QTY': np.random.randint(1, 10, size=62),
            'PRICE_STATUS': np.random.choice(['R', 'P', 'M'], size=62),
            'IS_RETURN': np.random.choice([True, False], p=[0.05, 0.95], size=62)
        })
        st.warning("Using demo data due to loading error.")
    
    return df

# Load the data
df = load_data()

# Date range filter
min_date = df['SALE_DATE'].min().date()
max_date = df['SALE_DATE'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['SALE_DATE'].dt.date >= start_date) & 
                     (df['SALE_DATE'].dt.date <= end_date)]
else:
    filtered_df = df

# Store format filter
store_formats = ['All'] + sorted(df['STORE_FORMAT'].unique().tolist())
selected_format = st.sidebar.selectbox("Store Format", store_formats)

if selected_format != 'All':
    filtered_df = filtered_df[filtered_df['STORE_FORMAT'] == selected_format]

# Command filter
commands = ['All'] + sorted(df['COMMAND_NAME'].unique().tolist())
selected_command = st.sidebar.selectbox("Command", commands)

if selected_command != 'All':
    filtered_df = filtered_df[filtered_df['COMMAND_NAME'] == selected_command]

# Price status filter
price_statuses = ['All'] + sorted(df['PRICE_STATUS'].unique().tolist())
selected_price_status = st.sidebar.selectbox("Price Status", price_statuses, 
                                            help="R=Regular, P=Promotion, M=Markdown")

if selected_price_status != 'All':
    filtered_df = filtered_df[filtered_df['PRICE_STATUS'] == selected_price_status]

# Include/exclude returns
include_returns = st.sidebar.checkbox("Include Returns", value=True)
if not include_returns:
    filtered_df = filtered_df[~filtered_df['IS_RETURN']]

# Display dataset info
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Rows in filtered data:** {len(filtered_df):,}")
st.sidebar.markdown(f"**Date range:** {start_date} to {end_date}")

# Main dashboard content
# Key metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_df['EXTENSION_AMOUNT'].sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">${total_sales:,.2f}</div>
        <div class="metric-label">Total Sales</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_transactions = filtered_df['SLIP_NO'].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_transactions:,}</div>
        <div class="metric-label">Transactions</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_transaction = total_sales / total_transactions if total_transactions > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">${avg_transaction:.2f}</div>
        <div class="metric-label">Avg Transaction Value</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    return_rate = filtered_df['IS_RETURN'].mean() * 100
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{return_rate:.2f}%</div>
        <div class="metric-label">Return Rate</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Temporal analysis
st.markdown('<div class="sub-header">Temporal Analysis</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Daily Trends", "Weekly Patterns", "Hourly Analysis"])

with tab1:
    # Daily sales trend
    daily_sales = filtered_df.groupby(filtered_df['SALE_DATE'].dt.date)['EXTENSION_AMOUNT'].sum().reset_index()
    daily_sales = daily_sales.sort_values('SALE_DATE')
    
    fig = px.line(daily_sales, x='SALE_DATE', y='EXTENSION_AMOUNT', 
                 title='Daily Sales Trend',
                 labels={'SALE_DATE': 'Date', 'EXTENSION_AMOUNT': 'Sales Amount ($)'},
                 markers=True)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Day of week analysis
    day_of_week_sales = filtered_df.groupby(filtered_df['DAY_OF_WEEK'])['EXTENSION_AMOUNT'].sum().reset_index()
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_of_week_sales['DAY_OF_WEEK'] = pd.Categorical(day_of_week_sales['DAY_OF_WEEK'], categories=day_order, ordered=True)
    day_of_week_sales = day_of_week_sales.sort_values('DAY_OF_WEEK')
    
    fig = px.bar(day_of_week_sales, x='DAY_OF_WEEK', y='EXTENSION_AMOUNT',
                title='Sales by Day of Week',
                labels={'DAY_OF_WEEK': 'Day of Week', 'EXTENSION_AMOUNT': 'Sales Amount ($)'})
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Hour of day analysis
    hourly_sales = filtered_df.groupby(filtered_df['HOUR'])['EXTENSION_AMOUNT'].sum().reset_index()
    
    fig = px.bar(hourly_sales, x='HOUR', y='EXTENSION_AMOUNT',
                title='Sales by Hour of Day',
                labels={'HOUR': 'Hour of Day (24h)', 'EXTENSION_AMOUNT': 'Sales Amount ($)'})
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Product analysis
st.markdown('<div class="sub-header">Product Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Top products by revenue
    top_products_revenue = filtered_df.groupby('ITEM_DESC')['EXTENSION_AMOUNT'].sum().reset_index()
    top_products_revenue = top_products_revenue.sort_values('EXTENSION_AMOUNT', ascending=False).head(10)
    
    fig = px.bar(top_products_revenue, y='ITEM_DESC', x='EXTENSION_AMOUNT', orientation='h',
                title='Top 10 Products by Revenue',
                labels={'ITEM_DESC': 'Product', 'EXTENSION_AMOUNT': 'Revenue ($)'})
    fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Top products by quantity
    top_products_quantity = filtered_df.groupby('ITEM_DESC')['QTY'].sum().reset_index()
    top_products_quantity = top_products_quantity.sort_values('QTY', ascending=False).head(10)
    
    fig = px.bar(top_products_quantity, y='ITEM_DESC', x='QTY', orientation='h',
                title='Top 10 Products by Quantity Sold',
                labels={'ITEM_DESC': 'Product', 'QTY': 'Quantity Sold'})
    fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Store analysis
st.markdown('<div class="sub-header">Store Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Sales by store format
    store_format_sales = filtered_df.groupby('STORE_FORMAT')['EXTENSION_AMOUNT'].sum().reset_index()
    
    fig = px.pie(store_format_sales, values='EXTENSION_AMOUNT', names='STORE_FORMAT',
                title='Sales by Store Format',
                hole=0.4)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Top stores
    store_sales = filtered_df.groupby('SITE_NAME')['EXTENSION_AMOUNT'].sum().reset_index()
    store_sales = store_sales.sort_values('EXTENSION_AMOUNT', ascending=False).head(10)
    
    fig = px.bar(store_sales, y='SITE_NAME', x='EXTENSION_AMOUNT', orientation='h',
                title='Top 10 Stores by Revenue',
                labels={'SITE_NAME': 'Store', 'EXTENSION_AMOUNT': 'Revenue ($)'})
    fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Price status analysis
st.markdown('<div class="sub-header">Price Status Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Sales by price status
    price_status_sales = filtered_df.groupby('PRICE_STATUS')['EXTENSION_AMOUNT'].sum().reset_index()
    
    fig = px.pie(price_status_sales, values='EXTENSION_AMOUNT', names='PRICE_STATUS',
                title='Sales by Price Status',
                labels={'PRICE_STATUS': 'Price Status (R=Regular, P=Promotion, M=Markdown)'},
                hole=0.4)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Transaction count by price status
    price_status_count = filtered_df.groupby('PRICE_STATUS').size().reset_index(name='COUNT')
    
    fig = px.bar(price_status_count, x='PRICE_STATUS', y='COUNT',
                title='Transaction Count by Price Status',
                labels={'PRICE_STATUS': 'Price Status (R=Regular, P=Promotion, M=Markdown)', 'COUNT': 'Number of Transactions'})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Add data explorer
st.markdown("---")
st.markdown('<div class="sub-header">Data Explorer</div>', unsafe_allow_html=True)

if st.checkbox("Show Raw Data Sample"):
    st.write(filtered_df.head(100))

# AI Insights
st.markdown("---")
st.markdown('<div class="sub-header">AI-Powered Insights</div>', unsafe_allow_html=True)

with st.expander("Generate AI Insights", expanded=False):
    st.write("Use OpenAI to generate insights from your retail data analysis.")
    
    # Input for OpenAI API key
    api_key = st.text_input("OpenAI API Key", type="password", 
                           help="Enter your OpenAI API key to generate insights. The key is not stored.")
    
    # Option to ask specific questions
    question_type = st.radio("Insight Type", ["General Analysis", "Specific Question"])
    
    question = None
    if question_type == "Specific Question":
        question = st.text_input("Enter your specific question about the retail data")
    
    # Button to generate insights
    if st.button("Generate Insights"):
        if not api_key:
            st.error("Please enter your OpenAI API key to generate insights.")
        else:
            with st.spinner("Generating AI insights... This may take a moment."):
                try:
                    # Read the summary report
                    summary_content = retail_llm_insights.read_summary_report()
                    
                    if summary_content:
                        # Configure OpenAI client
                        openai_client = retail_llm_insights.configure_openai_client(api_key)
                        
                        # Generate insights
                        insights = retail_llm_insights.generate_retail_insights(
                            summary_content=summary_content,
                            question=question if question_type == "Specific Question" else None,
                            openai_client=openai_client
                        )
                        
                        # Display insights
                        st.markdown("## AI-Generated Insights")
                        st.markdown(insights)
                        
                        # Option to save insights
                        if st.button("Save Insights to File"):
                            file_path = "retail_analysis_results/llm_insights.md"
                            retail_llm_insights.save_insights_to_file(insights, file_path)
                            st.success(f"Insights saved to {file_path}")
                    else:
                        st.error("Could not read summary report. Please run the static analysis first.")
                except Exception as e:
                    st.error(f"Error generating insights: {str(e)}")

# Footer
st.markdown("---")
st.markdown("MCCS Retail Sales Analysis Dashboard | Data Period: Dec 2024 - Jan 2025")
st.markdown("Powered by Streamlit, Plotly, and Dask | AI Insights by OpenAI")
