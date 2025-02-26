# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
data = pd.read_csv('/Users/huawei/Spaces/pbl/DoD SAFE/convertedcsv/Advertising_Email_Engagement/Advertising_Email_Engagement.xlsx-Email_Engagement_Engagement_Tim.csv', header=0)  # Adjust header if necessary
data.columns = data.columns.str.strip()
print(data.columns)

# Convert 'Daily' column to datetime
data['Daily'] = pd.to_datetime(data['Daily'], format='%Y-%m-%d %H:%M:%S')
print(data['Daily'].iloc[0])  # Print first date value

# Set the index to the 'Daily' column
data.set_index('Daily', inplace=True)

# Display the title of the dashboard
st.title('Email Marketing Engagement Metrics Dashboard')

# Show the raw data
st.subheader('Raw Data')
st.write(data)

# Summary metrics
st.subheader('Summary Metrics')
total_deliveries = data['Deliveries'].sum()
total_unique_opens = data['Unique Opens'].sum()
average_open_rate = data['Open Rate'].mean()
average_click_rate = data['Click Rate'].mean()

st.write(f'Total Deliveries: {total_deliveries}')
st.write(f'Total Unique Opens: {total_unique_opens}')
st.write(f'Average Open Rate: {average_open_rate:.2f}%')
st.write(f'Average Click Rate: {average_click_rate:.2f}%')

# Trend Analysis
st.subheader('Engagement Trends')

# Plotting Deliveries and Unique Opens
fig, ax = plt.subplots(figsize=(10, 5))
data[['Deliveries', 'Unique Opens']].plot(ax=ax)
ax.set_title('Deliveries and Unique Opens Over Time')
ax.set_ylabel('Count')
ax.set_xlabel('Date')
st.pyplot(fig)

# Plotting Open Rate and Click Rate
fig, ax = plt.subplots(figsize=(10, 5))
data[['Open Rate', 'Click Rate']].plot(ax=ax)
ax.set_title('Open Rate and Click Rate Over Time')
ax.set_ylabel('Rate (%)')
ax.set_xlabel('Date')
st.pyplot(fig)

# Additional Analysis: Unsubscribes
st.subheader('Unsubscribe Rate Analysis')
fig, ax = plt.subplots(figsize=(10, 5))
data['Unsubscribe Rate'].plot(kind='bar', ax=ax)
ax.set_title('Unsubscribe Rate Over Time')
ax.set_ylabel('Unsubscribe Rate (%)')
ax.set_xlabel('Date')
st.pyplot(fig)

# Conclusion
st.subheader('Conclusion')
st.write("This dashboard provides insights into email marketing engagement metrics, including trends in deliveries, unique opens, open rates, click rates, and unsubscribe rates.")