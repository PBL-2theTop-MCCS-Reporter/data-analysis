import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Set style for matplotlib
plt.style.use('ggplot')
sns.set(style="whitegrid")

# Create output directory for visualizations
os.makedirs('retail_analysis_results', exist_ok=True)

print("Starting Retail Sales Data Analysis...")
print("Loading data (this may take a few minutes due to the large file size)...")

# Load the data using Dask for better memory management with large files
# Use the CSV version as it's more accessible
df = dd.read_csv('data/convertedcsv/MCCS_RetailData.csv', 
                 assume_missing=True,
                 blocksize="64MB")  # Adjust blocksize as needed

# Convert date columns to datetime
df['SALE_DATE'] = dd.to_datetime(df['SALE_DATE'], format='%m/%d/%y')
df['SALE_DATE_TIME'] = dd.to_datetime(df['SALE_DATE_TIME'], format='%m/%d/%y %H:%M')

# Create a month column for monthly analysis
df['MONTH'] = df['SALE_DATE'].dt.month
df['MONTH_NAME'] = df['SALE_DATE'].dt.month_name()
df['DAY_OF_WEEK'] = df['SALE_DATE'].dt.day_name()
df['HOUR'] = df['SALE_DATE_TIME'].dt.hour

# Create a flag for returns
df['IS_RETURN'] = df['RETURN_IND'] == 'Y'

# Compute basic statistics
with ProgressBar():
    print("Computing basic statistics...")
    # Convert to pandas for easier analysis after aggregation
    total_sales = df['EXTENSION_AMOUNT'].sum().compute()
    total_transactions = df['SLIP_NO'].nunique().compute()
    total_items = df['ITEM_ID'].nunique().compute()
    total_quantity = df['QTY'].sum().compute()
    return_rate = df['IS_RETURN'].mean().compute() * 100
    
    # Get unique stores and commands
    stores = df['SITE_NAME'].unique().compute()
    commands = df['COMMAND_NAME'].unique().compute()
    store_formats = df['STORE_FORMAT'].unique().compute()

print(f"\nAnalysis Period: Dec 2024 - Jan 2025")
print(f"Total Sales: ${total_sales:,.2f}")
print(f"Total Transactions: {total_transactions:,}")
print(f"Total Unique Items: {total_items:,}")
print(f"Total Quantity Sold: {total_quantity:,}")
print(f"Return Rate: {return_rate:.2f}%")
print(f"Number of Stores: {len(stores)}")
print(f"Number of Commands: {len(commands)}")
print(f"Store Formats: {', '.join(store_formats)}")

# ----------------------
# Temporal Trend Analysis
# ----------------------
print("\nAnalyzing temporal trends...")

# Daily sales trend
daily_sales = df.groupby('SALE_DATE')['EXTENSION_AMOUNT'].sum().compute().reset_index()
daily_sales = daily_sales.sort_values('SALE_DATE')

# Plot daily sales trend
plt.figure(figsize=(15, 6))
plt.plot(daily_sales['SALE_DATE'], daily_sales['EXTENSION_AMOUNT'], marker='o', linestyle='-')
plt.title('Daily Sales Trend (Dec 2024 - Jan 2025)')
plt.xlabel('Date')
plt.ylabel('Sales Amount ($)')
plt.grid(True)
plt.tight_layout()
plt.savefig('retail_analysis_results/daily_sales_trend.png')

# Weekly sales trend
daily_sales['WEEK'] = daily_sales['SALE_DATE'].dt.isocalendar().week
weekly_sales = daily_sales.groupby('WEEK')['EXTENSION_AMOUNT'].sum().reset_index()

plt.figure(figsize=(12, 6))
plt.bar(weekly_sales['WEEK'], weekly_sales['EXTENSION_AMOUNT'])
plt.title('Weekly Sales Trend')
plt.xlabel('Week Number')
plt.ylabel('Sales Amount ($)')
plt.grid(True, axis='y')
plt.tight_layout()
plt.savefig('retail_analysis_results/weekly_sales_trend.png')

# Day of week analysis
day_of_week_sales = df.groupby('DAY_OF_WEEK')['EXTENSION_AMOUNT'].sum().compute().reset_index()
# Reorder days
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_of_week_sales['DAY_OF_WEEK'] = pd.Categorical(day_of_week_sales['DAY_OF_WEEK'], categories=day_order, ordered=True)
day_of_week_sales = day_of_week_sales.sort_values('DAY_OF_WEEK')

plt.figure(figsize=(12, 6))
sns.barplot(x='DAY_OF_WEEK', y='EXTENSION_AMOUNT', data=day_of_week_sales)
plt.title('Sales by Day of Week')
plt.xlabel('Day of Week')
plt.ylabel('Sales Amount ($)')
plt.grid(True, axis='y')
plt.tight_layout()
plt.savefig('retail_analysis_results/sales_by_day_of_week.png')

# Hour of day analysis
hourly_sales = df.groupby('HOUR')['EXTENSION_AMOUNT'].sum().compute().reset_index()

plt.figure(figsize=(14, 6))
sns.barplot(x='HOUR', y='EXTENSION_AMOUNT', data=hourly_sales)
plt.title('Sales by Hour of Day')
plt.xlabel('Hour of Day')
plt.ylabel('Sales Amount ($)')
plt.grid(True, axis='y')
plt.tight_layout()
plt.savefig('retail_analysis_results/sales_by_hour.png')

# ----------------------
# Product Analysis
# ----------------------
print("\nAnalyzing product trends...")

# Top selling products by revenue
top_products_revenue = df.groupby(['ITEM_ID', 'ITEM_DESC'])['EXTENSION_AMOUNT'].sum().compute().reset_index()
top_products_revenue = top_products_revenue.sort_values('EXTENSION_AMOUNT', ascending=False).head(20)

plt.figure(figsize=(15, 8))
sns.barplot(x='EXTENSION_AMOUNT', y='ITEM_DESC', data=top_products_revenue)
plt.title('Top 20 Products by Revenue')
plt.xlabel('Revenue ($)')
plt.ylabel('Product')
plt.grid(True, axis='x')
plt.tight_layout()
plt.savefig('retail_analysis_results/top_products_revenue.png')

# Top selling products by quantity
top_products_quantity = df.groupby(['ITEM_ID', 'ITEM_DESC'])['QTY'].sum().compute().reset_index()
top_products_quantity = top_products_quantity.sort_values('QTY', ascending=False).head(20)

plt.figure(figsize=(15, 8))
sns.barplot(x='QTY', y='ITEM_DESC', data=top_products_quantity)
plt.title('Top 20 Products by Quantity Sold')
plt.xlabel('Quantity Sold')
plt.ylabel('Product')
plt.grid(True, axis='x')
plt.tight_layout()
plt.savefig('retail_analysis_results/top_products_quantity.png')

# Price status analysis
price_status_sales = df.groupby('PRICE_STATUS')['EXTENSION_AMOUNT'].sum().compute().reset_index()
price_status_count = df.groupby('PRICE_STATUS').size().compute().reset_index(name='COUNT')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
sns.barplot(x='PRICE_STATUS', y='EXTENSION_AMOUNT', data=price_status_sales, ax=ax1)
ax1.set_title('Sales by Price Status')
ax1.set_xlabel('Price Status (R=Regular, P=Promotion, M=Markdown)')
ax1.set_ylabel('Sales Amount ($)')
ax1.grid(True, axis='y')

sns.barplot(x='PRICE_STATUS', y='COUNT', data=price_status_count, ax=ax2)
ax2.set_title('Transaction Count by Price Status')
ax2.set_xlabel('Price Status (R=Regular, P=Promotion, M=Markdown)')
ax2.set_ylabel('Number of Transactions')
ax2.grid(True, axis='y')

plt.tight_layout()
plt.savefig('retail_analysis_results/price_status_analysis.png')

# ----------------------
# Store Analysis
# ----------------------
print("\nAnalyzing store performance...")

# Sales by store format
store_format_sales = df.groupby('STORE_FORMAT')['EXTENSION_AMOUNT'].sum().compute().reset_index()

plt.figure(figsize=(10, 6))
sns.barplot(x='STORE_FORMAT', y='EXTENSION_AMOUNT', data=store_format_sales)
plt.title('Sales by Store Format')
plt.xlabel('Store Format')
plt.ylabel('Sales Amount ($)')
plt.grid(True, axis='y')
plt.tight_layout()
plt.savefig('retail_analysis_results/sales_by_store_format.png')

# Sales by command
command_sales = df.groupby('COMMAND_NAME')['EXTENSION_AMOUNT'].sum().compute().reset_index()
command_sales = command_sales.sort_values('EXTENSION_AMOUNT', ascending=False)

plt.figure(figsize=(15, 8))
sns.barplot(x='EXTENSION_AMOUNT', y='COMMAND_NAME', data=command_sales)
plt.title('Sales by Command')
plt.xlabel('Sales Amount ($)')
plt.ylabel('Command Name')
plt.grid(True, axis='x')
plt.tight_layout()
plt.savefig('retail_analysis_results/sales_by_command.png')

# Top performing stores
store_sales = df.groupby(['SITE_ID', 'SITE_NAME'])['EXTENSION_AMOUNT'].sum().compute().reset_index()
store_sales = store_sales.sort_values('EXTENSION_AMOUNT', ascending=False).head(20)

plt.figure(figsize=(15, 8))
sns.barplot(x='EXTENSION_AMOUNT', y='SITE_NAME', data=store_sales)
plt.title('Top 20 Stores by Revenue')
plt.xlabel('Revenue ($)')
plt.ylabel('Store Name')
plt.grid(True, axis='x')
plt.tight_layout()
plt.savefig('retail_analysis_results/top_stores_revenue.png')

# ----------------------
# Transaction Analysis
# ----------------------
print("\nAnalyzing transaction patterns...")

# Calculate transaction size (items per transaction)
transaction_size = df.groupby('SLIP_NO')['QTY'].sum().compute().reset_index()
transaction_size_stats = transaction_size['QTY'].describe()

plt.figure(figsize=(10, 6))
sns.histplot(transaction_size['QTY'], bins=30, kde=True)
plt.title('Distribution of Transaction Size (Items per Transaction)')
plt.xlabel('Number of Items')
plt.ylabel('Frequency')
plt.grid(True)
plt.tight_layout()
plt.savefig('retail_analysis_results/transaction_size_distribution.png')

# Calculate transaction value
transaction_value = df.groupby('SLIP_NO')['EXTENSION_AMOUNT'].sum().compute().reset_index()
transaction_value_stats = transaction_value['EXTENSION_AMOUNT'].describe()

plt.figure(figsize=(10, 6))
sns.histplot(transaction_value['EXTENSION_AMOUNT'], bins=30, kde=True)
plt.title('Distribution of Transaction Value')
plt.xlabel('Transaction Value ($)')
plt.ylabel('Frequency')
plt.grid(True)
plt.tight_layout()
plt.savefig('retail_analysis_results/transaction_value_distribution.png')

# ----------------------
# Return Analysis
# ----------------------
print("\nAnalyzing return patterns...")

# Return rate by product
return_by_product = df.groupby(['ITEM_ID', 'ITEM_DESC']).agg({'IS_RETURN': 'mean'}).compute().reset_index()
return_by_product = return_by_product.sort_values('IS_RETURN', ascending=False).head(20)
return_by_product['RETURN_RATE'] = return_by_product['IS_RETURN'] * 100

plt.figure(figsize=(15, 8))
sns.barplot(x='RETURN_RATE', y='ITEM_DESC', data=return_by_product)
plt.title('Top 20 Products by Return Rate')
plt.xlabel('Return Rate (%)')
plt.ylabel('Product')
plt.grid(True, axis='x')
plt.tight_layout()
plt.savefig('retail_analysis_results/top_products_return_rate.png')

# Return rate by store
return_by_store = df.groupby(['SITE_ID', 'SITE_NAME']).agg({'IS_RETURN': 'mean'}).compute().reset_index()
return_by_store = return_by_store.sort_values('IS_RETURN', ascending=False).head(20)
return_by_store['RETURN_RATE'] = return_by_store['IS_RETURN'] * 100

plt.figure(figsize=(15, 8))
sns.barplot(x='RETURN_RATE', y='SITE_NAME', data=return_by_store)
plt.title('Top 20 Stores by Return Rate')
plt.xlabel('Return Rate (%)')
plt.ylabel('Store')
plt.grid(True, axis='x')
plt.tight_layout()
plt.savefig('retail_analysis_results/top_stores_return_rate.png')

# ----------------------
# Generate Summary Report
# ----------------------
print("\nGenerating summary report...")

with open('retail_analysis_results/summary_report.txt', 'w') as f:
    f.write("MCCS Retail Sales Data Analysis Summary\n")
    f.write("======================================\n\n")
    f.write(f"Analysis Period: Dec 2024 - Jan 2025\n")
    f.write(f"Total Sales: ${total_sales:,.2f}\n")
    f.write(f"Total Transactions: {total_transactions:,}\n")
    f.write(f"Total Unique Items: {total_items:,}\n")
    f.write(f"Total Quantity Sold: {total_quantity:,}\n")
    f.write(f"Return Rate: {return_rate:.2f}%\n")
    f.write(f"Number of Stores: {len(stores)}\n")
    f.write(f"Number of Commands: {len(commands)}\n")
    f.write(f"Store Formats: {', '.join(store_formats)}\n\n")
    
    f.write("Key Insights:\n")
    f.write("-------------\n")
    
    # Top selling day of week
    top_day = day_of_week_sales.loc[day_of_week_sales['EXTENSION_AMOUNT'].idxmax()]
    f.write(f"1. Highest sales occur on {top_day['DAY_OF_WEEK']}s\n")
    
    # Top selling hour
    top_hour = hourly_sales.loc[hourly_sales['EXTENSION_AMOUNT'].idxmax()]
    f.write(f"2. Peak sales hour is {int(top_hour['HOUR'])}:00h (24-hour format)\n")
    
    # Top product
    top_product = top_products_revenue.iloc[0]
    f.write(f"3. Best-selling product by revenue: {top_product['ITEM_DESC']} (${top_product['EXTENSION_AMOUNT']:,.2f})\n")
    
    # Top store
    top_store = store_sales.iloc[0]
    f.write(f"4. Top performing store: {top_store['SITE_NAME']} (${top_store['EXTENSION_AMOUNT']:,.2f})\n")
    
    # Price status insight
    regular_sales = price_status_sales[price_status_sales['PRICE_STATUS'] == 'R']['EXTENSION_AMOUNT'].iloc[0]
    promo_sales = price_status_sales[price_status_sales['PRICE_STATUS'] == 'P']['EXTENSION_AMOUNT'].iloc[0] if 'P' in price_status_sales['PRICE_STATUS'].values else 0
    markdown_sales = price_status_sales[price_status_sales['PRICE_STATUS'] == 'M']['EXTENSION_AMOUNT'].iloc[0] if 'M' in price_status_sales['PRICE_STATUS'].values else 0
    
    f.write(f"5. Regular-priced items account for ${regular_sales:,.2f} in sales ({regular_sales/total_sales*100:.1f}% of total)\n")
    if promo_sales > 0:
        f.write(f"6. Promotional items account for ${promo_sales:,.2f} in sales ({promo_sales/total_sales*100:.1f}% of total)\n")
    if markdown_sales > 0:
        f.write(f"7. Markdown items account for ${markdown_sales:,.2f} in sales ({markdown_sales/total_sales*100:.1f}% of total)\n")
    
    # Transaction insights
    f.write(f"8. Average transaction value: ${transaction_value_stats['mean']:,.2f}\n")
    f.write(f"9. Average items per transaction: {transaction_size_stats['mean']:.2f}\n")
    
    # Return insights
    f.write(f"10. Product with highest return rate: {return_by_product.iloc[0]['ITEM_DESC']} ({return_by_product.iloc[0]['RETURN_RATE']:.2f}%)\n")

print("\nAnalysis complete! Results saved to 'retail_analysis_results' directory.")
print("Run the script with 'python retail_trends_analysis.py' to execute the analysis.")
