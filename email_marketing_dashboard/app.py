import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os
from data_loader import load_data

# Import custom modules
from data_loader import load_data, get_email_funnel_data, get_performance_vs_previous
from visualizations import (
    plot_metrics_over_time, plot_email_funnel, plot_domain_comparison,
    plot_weekly_pattern, plot_audience_performance, plot_campaign_performance,
    plot_heatmap
)
from llm_insights import generate_insights, configure_openai_client

# Page configuration
st.set_page_config(
    page_title="MCCS Email Marketing Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def get_data():
    return load_data()

try:
    data = get_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar
st.sidebar.title("📊 MCCS Email Analytics")
page = st.sidebar.radio(
    "Navigation", 
    ["Dashboard", "Delivery Analysis", "Engagement Analysis", "Campaign Analysis", "Audience Analysis", "LLM Insights"]
)

# Dashboard page
if page == "Dashboard":
    st.title("📧 Email Marketing Dashboard")
    
    # Overview metrics
    st.subheader("Key Performance Indicators")
    
    # Summary metrics layout
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        sends = data['summary']['sends']['Sends'].iloc[0]
        sends_diff = data['summary']['sends']['Diff'].iloc[0]
        st.metric("Total Sends", f"{sends:,}", sends_diff)
    
    with col2:
        deliveries = data['summary']['deliveries']['Deliveries'].iloc[0]
        deliveries_diff = data['summary']['deliveries']['Diff'].iloc[0]
        st.metric("Deliveries", f"{deliveries:,}", deliveries_diff)

    with col3:
        open_rate = data['summary']['open_rate']['Open Rate'].iloc[0]
        open_rate_diff = data['summary']['open_rate']['Diff'].iloc[0]
        st.metric("Open Rate", f"{open_rate:.2%}", open_rate_diff)
    
    with col4:
        click_rate = data['summary']['click_to_open_rate']['Click To Open Rate'].iloc[0]
        click_rate_diff = data['summary']['click_to_open_rate']['Diff'].iloc[0]
        st.metric("Click to Open Rate", f"{click_rate:.2%}", click_rate_diff)
    
    # Email funnel
    st.subheader("Email Marketing Funnel")
    funnel_data = get_email_funnel_data(data)
    st.plotly_chart(plot_email_funnel(funnel_data), use_container_width=True)
    
    # Time series analysis in tabs
    st.subheader("Performance Over Time")
    ts_tabs = st.tabs(["Delivery Metrics", "Engagement Metrics"])
    
    with ts_tabs[0]:  # Delivery Metrics
        delivery_metrics = st.multiselect(
            "Select delivery metrics to display:",
            options=["Sends", "Deliveries", "Delivery Rate", "Bounce Rate"],
            default=["Sends", "Deliveries"]
        )
        if delivery_metrics:
            st.plotly_chart(
                plot_metrics_over_time(
                    data['time_series']['delivery'], 
                    delivery_metrics, 
                    "Delivery Metrics Over Time"
                ),
                use_container_width=True
            )
    
    with ts_tabs[1]:  # Engagement Metrics
        engagement_metrics = st.multiselect(
            "Select engagement metrics to display:",
            options=["Open Rate", "Click Rate", "Click to Open Rate", "Unsubscribe Rate"],
            default=["Open Rate", "Click Rate"]
        )
        if engagement_metrics:
            st.plotly_chart(
                plot_metrics_over_time(
                    data['time_series']['engagement'], 
                    engagement_metrics, 
                    "Engagement Metrics Over Time"
                ),
                use_container_width=True
            )

    # Domain and weekday distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Email Domain Distribution")
        st.plotly_chart(
            plot_domain_comparison(
                data['breakdowns']['delivery_by_domain'],
                data['breakdowns']['engagement_by_domain']
            ),
            use_container_width=True
        )
    
    with col2:
        st.subheader("Day of Week Performance")
        st.plotly_chart(
            plot_weekly_pattern(
                data['breakdowns']['delivery_by_weekday'],
                data['breakdowns']['engagement_by_weekday']
            ),
            use_container_width=True
        )

# Delivery Analysis page
elif page == "Delivery Analysis":
    st.title("📬 Email Delivery Analysis")
    
    # Delivery stats and trends
    st.subheader("Delivery Metrics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        delivery_rate = data['time_series']['delivery']['Delivery Rate'].mean()
        st.metric("Average Delivery Rate", f"{delivery_rate:.2%}")
    
    with col2:
        try:
            bounce_rate = data['time_series']['delivery']['Bounce Rate'].mean()
        except KeyError:
            # Use the bounce rate from summary data instead
            bounce_rate = data['summary']['bounce_rate']['Bounce Rate'].iloc[0]
            print(f"Using summary bounce rate: {bounce_rate}")
        st.metric("Average Bounce Rate", f"{bounce_rate:.2%}")
    
    with col3:
        total_bounces = data['time_series']['delivery']['Bounces'].sum()
        st.metric("Total Bounces", f"{total_bounces:,}")
    
    # Daily delivery trend chart
    st.subheader("Daily Delivery Trends")
    delivery_metrics = st.multiselect(
        "Select delivery metrics:",
        options=["Sends", "Deliveries", "Delivery Rate", "Bounce Rate"],
        default=["Deliveries", "Bounce Rate"]
    )
    if delivery_metrics:
        st.plotly_chart(
            plot_metrics_over_time(
                data['time_series']['delivery'], 
                delivery_metrics, 
                "Delivery Metrics Over Time"
            ),
            use_container_width=True
        )
    
    # Bounce rate distribution
    st.subheader("Bounce Rate Distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    try:
        bounce_rate_data = data['time_series']['delivery']['Bounce Rate'].dropna()
        if len(bounce_rate_data) > 0:
            sns.histplot(bounce_rate_data, kde=True, ax=ax)
        else:
            ax.text(0.5, 0.5, "No bounce rate data available", 
                    horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    except KeyError:
        # Handle the case where 'Bounce Rate' column doesn't exist
        ax.text(0.5, 0.5, "Bounce Rate data not available", 
                horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    st.pyplot(fig)
    
    # Email domains
    st.subheader("Email Domains Analysis")
    st.write("Top 10 email domains by sends:")
    st.dataframe(data['breakdowns']['delivery_by_domain'].head(10))
    
    # Weekday distribution
    st.subheader("Sends by Day of Week")
    st.plotly_chart(
        px.bar(
            data['breakdowns']['delivery_by_weekday'].sort_values('Sends', ascending=False),
            x='Weekday',
            y='Sends',
            title="Email Sends by Day of Week"
        ),
        use_container_width=True
    )

# Engagement Analysis page
elif page == "Engagement Analysis":
    st.title("👀 Email Engagement Analysis")
    
    # Engagement stats
    st.subheader("Engagement Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        open_rate = data['time_series']['engagement']['Open Rate'].mean()
        st.metric("Average Open Rate", f"{open_rate:.2%}")
    
    with col2:
        click_rate = data['time_series']['engagement']['Click Rate'].mean()
        st.metric("Average Click Rate", f"{click_rate:.2%}")
    
    with col3:
        cto_rate = data['time_series']['engagement']['Click to Open Rate'].mean()
        st.metric("Average Click-to-Open Rate", f"{cto_rate:.2%}")
    
    with col4:
        unsub_rate = data['time_series']['engagement']['Unsubscribe Rate'].mean()
        st.metric("Average Unsubscribe Rate", f"{unsub_rate:.4%}")
    
    # Daily engagement trend chart
    st.subheader("Daily Engagement Trends")
    eng_metrics = st.multiselect(
        "Select engagement metrics:",
        options=["Open Rate", "Click Rate", "Click to Open Rate", "Unsubscribe Rate"],
        default=["Open Rate", "Click Rate"]
    )
    if eng_metrics:
        st.plotly_chart(
            plot_metrics_over_time(
                data['time_series']['engagement'], 
                eng_metrics, 
                "Engagement Metrics Over Time"
            ),
            use_container_width=True
        )
    
    # Correlation analysis
    st.subheader("Correlation Between Metrics")
    corr_metrics = ['Open Rate', 'Click Rate', 'Click to Open Rate', 'Unsubscribe Rate']
    corr_data = data['time_series']['engagement'][corr_metrics].corr()
    
    fig = plt.figure(figsize=(10, 8))
    sns.heatmap(corr_data, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    st.pyplot(fig)
    
    # Email domains analysis for engagement
    st.subheader("Engagement by Email Domain")
    st.write("Top 10 email domains by opens:")
    st.dataframe(data['breakdowns']['engagement_by_domain'].head(10))
    
    # Day of week analysis for engagement
    st.subheader("Engagement by Day of Week")
    st.plotly_chart(
        plot_weekly_pattern(None, data['breakdowns']['engagement_by_weekday']),
        use_container_width=True
    )

# Campaign Analysis page
elif page == "Campaign Analysis":
    st.title("🚀 Campaign Performance Analysis")
    
    if 'campaigns' in data:
        # Campaign performance metrics
        st.subheader("Campaign Performance Overview")
        campaigns_df = data['campaigns']
        
        # Show campaign table
        st.dataframe(campaigns_df.sort_values('Send Date', ascending=False))
        
        # Campaign comparison chart
        st.subheader("Campaign Comparison")
        metric_to_compare = st.selectbox(
            "Select metric to compare:", 
            ["Open Rate", "Click Rate", "Click to Open Rate", "Unsubscribe Rate"]
        )
        
        st.plotly_chart(
            plot_campaign_performance(campaigns_df, metric_to_compare),
            use_container_width=True
        )
        
        # Campaign details
        st.subheader("Campaign Details")
        selected_campaign = st.selectbox("Select Campaign:", campaigns_df['Message Name'].unique())
        
        campaign_data = campaigns_df[campaigns_df['Message Name'] == selected_campaign]
        
        if not campaign_data.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Open Rate", f"{campaign_data['Open Rate'].iloc[0]:.2%}")
            col2.metric("Click Rate", f"{campaign_data['Click Rate'].iloc[0]:.2%}")
            col3.metric("Click to Open Rate", f"{campaign_data['Click to Open Rate'].iloc[0]:.2%}")
            col4.metric("Unsubscribe Rate", f"{campaign_data['Unsubscribe Rate'].iloc[0]:.4%}")
            
            send_date = campaign_data['Send Date'].iloc[0]
            st.info(f"Campaign sent on: {send_date}")
            
            # Get performance relative to average
            campaign_vs_avg = get_performance_vs_previous(campaign_data, campaigns_df, metric_to_compare)
            st.write(f"Performance compared to average: {campaign_vs_avg}")
    else:
        st.info("Campaign data is not available in the provided files.")

# Audience Analysis page
elif page == "Audience Analysis":
    st.title("👥 Audience Analysis")
    
    if 'by_audience' in data['breakdowns']:
        # Audience performance metrics
        st.subheader("Audience Performance Overview")
        audience_df = data['breakdowns']['by_audience']
        
        # Show audience table
        st.dataframe(audience_df.sort_values('Sends', ascending=False))
        
        # Audience comparison chart
        st.subheader("Audience Comparison")
        metric_to_compare = st.selectbox(
            "Select metric to compare:", 
            ["Open Rate", "Click Rate", "Click to Open Rate", "Unsubscribe Rate", "Bounce Rate"]
        )
        
        top_n = st.slider("Number of audiences to display:", min_value=5, max_value=20, value=10)
        
        st.plotly_chart(
            plot_audience_performance(audience_df, metric_to_compare, top_n),
            use_container_width=True
        )
        
        # Audience details
        st.subheader("Audience Details")
        selected_audience = st.selectbox("Select Audience:", audience_df['Audience Name'].unique())
        
        audience_data = audience_df[audience_df['Audience Name'] == selected_audience]
        
        if not audience_data.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            if 'Open Rate' in audience_data.columns:
                col1.metric("Open Rate", f"{audience_data['Open Rate'].iloc[0]:.2%}")
            if 'Click Rate' in audience_data.columns:
                col2.metric("Click Rate", f"{audience_data['Click Rate'].iloc[0]:.2%}")
            if 'Bounce Rate' in audience_data.columns:
                col3.metric("Bounce Rate", f"{audience_data['Bounce Rate'].iloc[0]:.2%}")
            if 'Unsubscribe Rate' in audience_data.columns:
                col4.metric("Unsubscribe Rate", f"{audience_data['Unsubscribe Rate'].iloc[0]:.4%}")
    else:
        st.info("Audience data is not available in the provided files.")

# LLM Insights page
elif page == "LLM Insights":
    st.title("🤖 AI-Generated Insights")
    
    # API key input
    api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password")
    
    if api_key:
        openai_client = configure_openai_client(api_key)
        
        # Insight type selection
        insight_type = st.selectbox(
            "Select the type of insights you want:",
            [
                "Overall Performance Summary",
                "Delivery Analysis",
                "Engagement Analysis",
                "Recommendations for Improvement",
                "Custom Query"
            ]
        )
        
        # Custom query input if selected
        if insight_type == "Custom Query":
            user_query = st.text_area("Enter your specific question about the email marketing data:")
        else:
            user_query = insight_type
        
        # Generate insights button
        if st.button("Generate Insights"):
            with st.spinner("Analyzing data and generating insights..."):
                insights = generate_insights(data, user_query, openai_client)
                
                st.markdown("## AI-Generated Insights")
                st.markdown(insights)
                
                # Option to export insights
                st.download_button(
                    "Export Insights as Text",
                    insights,
                    file_name="mccs_email_marketing_insights.txt",
                    mime="text/plain"
                )
    else:
        st.warning("Please enter your OpenAI API key in the sidebar to generate AI insights.")
        st.info("The LLM will analyze your email marketing data and provide actionable insights.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("MCCS Email Marketing Analytics Dashboard v1.0")
st.sidebar.markdown("Developed for MCCS marketing team")