import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pyarrow.parquet as pq
import sys
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import custom modules
from data_loader import load_data, get_email_funnel_data, get_performance_vs_previous
from visualizations import (
    plot_metrics_over_time, plot_email_funnel, plot_domain_comparison, plot_basic_metrics,
    plot_weekly_pattern, plot_audience_performance, plot_campaign_performance, plot_weekly_social_media_data,
    plot_heatmap
)
from llm_insights import generate_insights
from prompts import email_key_performance_response, email_performance_over_time_response, social_media_key_performance_response, email_domain_day_of_week_response, email_final_result_response, social_media_posts_over_time_response, social_media_hourly_engagements_response, social_media_final_result_response
from raw_data_loader import (load_raw_data, get_engagement_summary,get_post_engagement_scorecard_ac, get_media_type,
                             get_post_performance_summary, get_total_engagement_metrics_on, get_social_engagement_by_time_of)

from PDF_generator_util import generate_pdf, show_pdf

# Page configuration
st.set_page_config(
    page_title="MCCS Email Marketing Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables from .env file
load_dotenv()

# --- LLM Client Configuration ---
def get_llm_client(env_api_key, sidebar_api_key):
    """
    Returns an LLM client. Prioritizes OpenAI if an API key is provided,
    otherwise falls back to a local Ollama model.
    """
    # Prioritize sidebar input, then environment variable
    api_key = sidebar_api_key or env_api_key

    if api_key:
        st.sidebar.success("OpenAI API key is active.", icon="✅")
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=api_key)
    else:
        from langchain_ollama import OllamaLLM
        st.sidebar.warning("OpenAI API key not found. Falling back to local Ollama model. Responses may be slower or less accurate.", icon="⚠️")
        return OllamaLLM(model="llama3:8b")



# Load data
@st.cache_data
def get_data():
    return load_data()

@st.cache_data
def get_raw_data():
    return load_raw_data()


try:
    data = get_data()
    sm_data = get_raw_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# 初始化 session_state 的字段
if 'email_key_performance_response' not in st.session_state:
    st.session_state.email_key_performance_response = ""
if 'email_performance_over_time_response' not in st.session_state:
    st.session_state.email_performance_over_time_response = ""
if 'email_domain_day_of_week_response' not in st.session_state:
    st.session_state.email_domain_day_of_week_response = ""
if 'social_media_posts_over_time_response' not in st.session_state:
    st.session_state.social_media_posts_over_time_response = ""
if 'social_media_key_performance_response' not in st.session_state:
    st.session_state.social_media_key_performance_response = ""
if 'social_media_hourly_engagements_response' not in st.session_state:
    st.session_state.social_media_hourly_engagements_response = ""
if 'email_final_text' not in st.session_state:
    st.session_state.email_final_text = ""
if 'social_media_final_text' not in st.session_state:
    st.session_state.social_media_final_text = ""

# Sidebar
st.sidebar.title("📊 MCCS Email Analytics")

# --- API Key Management ---
env_api_key = os.environ.get("OPENAI_API_KEY")

# Determine the help text based on whether a key is found in the .env file
if env_api_key:
    help_text = "A key from .env is loaded. You can enter a new key here to override it."
    placeholder = "Using key from .env"
else:
    help_text = "Provide an OpenAI key to use GPT models. If left blank, a local model will be used."
    placeholder = "Enter your OpenAI API key"

sidebar_api_key = st.sidebar.text_input(
    "OpenAI API Key (Optional)", type="password",
    placeholder=placeholder, help=help_text
)

page = st.sidebar.radio(
    "Navigation", 
    ["Dashboard", "Delivery Analysis", "Engagement Analysis", "Campaign Analysis", "Audience Analysis", "Social Media Dashboard", "LLM Insights","AI Data Analysis Agent"]
)

# Get the appropriate LLM client based on API key availability
llm_client = get_llm_client(env_api_key, sidebar_api_key)

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

    st.write("AI response")

    col1, col2 = st.columns([1, 1])  # 可以调整宽度比例
    with col1:
        if st.button("Start AI Analysis", key="button_0"):
            with st.spinner("AI processing..."):
                email_key_performance = {
                    "total_sends": sends,
                    "delivery": deliveries,
                    "open_rate": open_rate,
                    "click_to_open_rate": click_rate,
                    "diff_total_sends": sends_diff,
                    "diff_delivery": deliveries_diff,
                    "diff_open_rate": open_rate_diff,
                    "diff_click_to_open_rate": click_rate_diff
                }
                st.session_state.email_key_performance_response = email_key_performance_response(llm_client, email_key_performance, 6)
    with col2:
        if st.button("❌ Reset", key="button_clear_0"):
            st.session_state.email_key_performance_response = ""

    if st.session_state.email_key_performance_response:
        st.write(st.session_state.email_key_performance_response)

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

            col1, col2 = st.columns([1, 1])  # 可以调整宽度比例

            with col1:
                if st.button("Start AI Analysis", key="button_1"):
                    with st.spinner("AI processing..."):
                        feature = ["Sends", "Deliveries", "Daily"]
                        print(data['time_series']['delivery'][feature])
                        st.session_state.email_performance_over_time_response = email_performance_over_time_response(llm_client,
                            data['time_series']['delivery'][feature].rename(columns={'Daily': 'date'}))
            with col2:
                if st.button("❌ Reset", key="button_clear_1"):
                    st.session_state.email_performance_over_time_response = ""

            if st.session_state.email_performance_over_time_response:
                st.write(st.session_state.email_performance_over_time_response)

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

    col1, col2 = st.columns([1, 1])  # 可以调整宽度比例

    with col1:
        if st.button("Start AI Analysis", key="button_2"):
            with st.spinner("AI processing..."):
                st.session_state.email_domain_day_of_week_response = email_domain_day_of_week_response(llm_client, data['breakdowns']['delivery_by_domain'], data['breakdowns']['engagement_by_domain'], data['breakdowns']['delivery_by_weekday'], data['breakdowns']['engagement_by_weekday'])
    with col2:
        if st.button("❌ Reset", key="button_clear_2"):
            st.session_state.email_domain_day_of_week_response = ""

    if st.session_state.email_domain_day_of_week_response:
        st.write(st.session_state.email_domain_day_of_week_response)

    if st.button("📄 Generate & Preview PDF"):
        final_report = email_final_result_response(llm_client, st.session_state.email_key_performance_response,
                                                   st.session_state.email_performance_over_time_response,
                                                   st.session_state.email_domain_day_of_week_response)

        st.session_state.email_final_text = st.session_state.email_key_performance_response + "\n\n" + st.session_state.email_performance_over_time_response + "\n\n" + st.session_state.email_domain_day_of_week_response + "\n\n" + "Assessment" + "\n\n" + final_report

    if  st.session_state.email_final_text:
        pdf_buffer = generate_pdf( st.session_state.email_final_text)

        # PDF 预览
        st.subheader("📄 PDF Preview：")
        show_pdf(pdf_buffer)

        # 下载按钮
        st.download_button(
            label="📥 Download PDF",
            data=pdf_buffer,
            file_name="ai_report.pdf",
            mime="application/pdf"
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

# Dashboard page
elif page == "Social Media Dashboard":
    st.title("📧 Social Media Marketing Dashboard")

    # Overview metrics
    st.subheader("Posts Engagement Summary")

    # Summary metrics layout
    col1, col2, col3, col4, col5 = st.columns(5)

    engagement_summary_data = get_engagement_summary(sm_data)
    post_performance_summary = get_post_performance_summary(sm_data)
    with col1:
        brand_posts = post_performance_summary["Brand Posts"].iloc[0]
        brand_posts_diff = post_performance_summary['Change in Volume of Published Messages'].iloc[0]
        brand_posts_diff_rate = post_performance_summary['% change in Volume of Published Messages'].iloc[0]
        st.metric("Brand Posts", f"{int(brand_posts):,}", f"{brand_posts_diff_rate}({int(brand_posts_diff)})")

    with col2:
        total_engagements= post_performance_summary["Total Engagements (SUM)"].iloc[0]
        total_engagements_diff = post_performance_summary['Change in Total Engagements'].iloc[0]
        total_engagements_diff_rate = post_performance_summary['% change in Total Engagements'].iloc[0]
        st.metric("Total Engagements", f"{int(total_engagements):,}", f"{brand_posts_diff_rate}({int(total_engagements_diff)})")

    with col3:
        post_like_and_reaction = engagement_summary_data["Post Likes And Reactions (SUM)"].iloc[0]
        post_like_and_reaction_diff = engagement_summary_data['Change in Post Likes And Reactions'].iloc[0]
        post_like_and_reaction_diff_rate = engagement_summary_data['% change in Post Likes And Reactions'].iloc[0]
        st.metric("Post Likes And Reactions", f"{int(post_like_and_reaction):,}", f"{post_like_and_reaction_diff_rate}({int(post_like_and_reaction_diff)})")

    with col4:
        posts_shares = engagement_summary_data['Post Shares (SUM)'].iloc[0]
        posts_shares_diff = engagement_summary_data['Change in Post Shares'].iloc[0]
        posts_shares_diff_rate = engagement_summary_data['% change in Post Shares'].iloc[0]
        st.metric("Post Shares", f"{int(posts_shares):,}", f"{posts_shares_diff_rate}({int(posts_shares_diff)})")

    with col5:
        post_comments = engagement_summary_data['Post Comments (SUM)'].iloc[0]
        post_comments_diff = engagement_summary_data['Change in Post Comments'].iloc[0]
        post_comments_diff_rate = engagement_summary_data['% change in Post Comments'].iloc[0]
        st.metric("Post Comments", f"{int(post_comments):,}", f"{post_comments_diff_rate}({int(post_comments_diff)})")

    st.write("AI response")

    # 用户反馈输入框
    user_feedback_input = st.text_input("If you have any idea or advice with my response, Please feel free to come up with!")

    col1, col2 = st.columns([1, 1])  # 可以调整宽度比例

    with col1:
        if st.button("Start AI Analysis", key="button_3"):
            with st.spinner("AI processing..."):
                social_media_key_performance = {
                    "brand_posts": brand_posts,
                    "total_engagements": total_engagements,
                    "post_like_and_reaction": post_like_and_reaction,
                    "posts_shares": posts_shares,
                    "post_comments": post_comments,
                    "brand_posts_diff": brand_posts_diff,
                    "total_engagements_diff": total_engagements_diff,
                    "post_like_and_reaction_diff": post_like_and_reaction_diff,
                    "posts_shares_diff": posts_shares_diff,
                    "post_comments_diff": post_comments_diff
                }
                st.session_state.social_media_key_performance_response = social_media_key_performance_response(llm_client, social_media_key_performance, user_feedback_input or "", 5)
    with col2:
        if st.button("❌ Reset", key="button_clear_3"):
            st.session_state.social_media_key_performance_response = ""

    if st.session_state.social_media_key_performance_response:
        st.write(st.session_state.social_media_key_performance_response)



    total_engagement_metrics_on = get_total_engagement_metrics_on(sm_data)
    social_engagement_by_time_of = get_social_engagement_by_time_of(sm_data)
    post_engagement_scorecard_ac = get_post_engagement_scorecard_ac(sm_data)
    media_type_data = get_media_type(sm_data)

    st.subheader("Performance Over Time")
    ps_tabs = st.tabs(["Posts Metrics", "Channel Metrics", "Media Type Metrics"])

    with ps_tabs[0]:
        posts_metrics = st.multiselect(
            "Select posts metrics to display:",
            options=["Total Engagements", "Post Likes And Reactions", "Post Comments", "Post Shares", "Post Reach", "Estimated Clicks"],
            default=["Total Engagements", "Post Likes And Reactions"]
        )
        st.plotly_chart(
            plot_metrics_over_time(
                total_engagement_metrics_on,
                posts_metrics,
                "Posts Metrics Over Time"
            ))

    with ps_tabs[1]:
        channel_metrics = st.multiselect(
            "Select channel metrics to display:",
            options=["Total Engagements", "Post Likes And Reactions", "Post Comments", "Post Shares", "Post Reach",
                     "Estimated Clicks"],
            default=["Total Engagements", "Post Likes And Reactions"]
        )
        st.plotly_chart(
            plot_basic_metrics(
                post_engagement_scorecard_ac.columns[0],
                post_engagement_scorecard_ac,
                channel_metrics,
                "Channel Metrics "
            ))

    with ps_tabs[2]:
        media_type_metrics = st.multiselect(
            "Select Media Type metrics to display:",
            options=["Total Engagements", "Post Likes And Reactions", "Post Comments", "Post Shares", "Post Reach",
                     "Volume of Published Messages"],
            default=["Total Engagements", "Post Likes And Reactions"]
        )
        st.plotly_chart(
            plot_basic_metrics(
                media_type_data.columns[0],
                media_type_data,
                media_type_metrics,
                "Media Type Metrics "
            ))

    st.write("AI response")

    col1, col2 = st.columns([1, 1])  # 可以调整宽度比例

    with col1:
        if st.button("Start AI Analysis", key="button_4"):
            with st.spinner("AI processing..."):
                st.session_state.social_media_posts_over_time_response = social_media_posts_over_time_response(
                    llm_client, total_engagement_metrics_on)
    with col2:
        if st.button("❌ Reset", key="button_clear_4"):
            st.session_state.social_media_posts_over_time_response = ""

    if st.session_state.social_media_posts_over_time_response:
        st.write(st.session_state.social_media_posts_over_time_response)

    st.plotly_chart(
        plot_weekly_social_media_data(
            social_engagement_by_time_of,
            social_engagement_by_time_of.columns,
            "Total Engagements by Time and Day"
        ))

    st.write("AI response")

    col1, col2 = st.columns([1, 1])  # 可以调整宽度比例

    with col1:
        if st.button("Start AI Analysis", key="button_5"):
            with st.spinner("AI processing..."):
                st.session_state.social_media_hourly_engagements_response = social_media_hourly_engagements_response(
                    llm_client, social_engagement_by_time_of)
    with col2:
        if st.button("❌ Reset", key="button_clear_5"):
            st.session_state.social_media_hourly_engagements_response = ""

    if st.session_state.social_media_hourly_engagements_response:
        st.write(st.session_state.social_media_hourly_engagements_response)

    if st.button("📄 Generate & Preview PDF"):
        final_report = social_media_final_result_response(llm_client, st.session_state.social_media_hourly_engagements_response,
                                                   st.session_state.social_media_posts_over_time_response,
                                                   st.session_state.social_media_key_performance_response)

        st.session_state.social_media_final_text = st.session_state.social_media_key_performance_response + "\n\n" + st.session_state.social_media_posts_over_time_response + "\n\n" + st.session_state.social_media_hourly_engagements_response + "\n\n" + "Assessment" + "\n\n" + final_report

    if st.session_state.social_media_final_text:
        pdf_buffer = generate_pdf(st.session_state.social_media_final_text)

        # PDF 预览
        st.subheader("📄 PDF Preview：")
        show_pdf(pdf_buffer)

        # 下载按钮
        st.download_button(
            label="📥 Download PDF",
            data=pdf_buffer,
            file_name="ai_report.pdf",
            mime="application/pdf"
        )


# LLM Insights page
elif page == "LLM Insights":
    st.title("🤖 AI-Generated Insights")
    
    if env_api_key or sidebar_api_key:
        openai_client = llm_client
        
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

elif page == "AI Data Analysis Agent":
    st.title("📊 Report Generator")
    if st.button("Start Generate"):
        progress = st.progress(0)
        status_text = st.empty()

        # Step 1: 数据预处理
        status_text.text("Step 1/8: Analyzing key metrics comparisons from two months before and after the email data...")
        progress.progress(0.125)
        sends = data['summary']['sends']['Sends'].iloc[0]
        sends_diff = data['summary']['sends']['Diff'].iloc[0]

        deliveries = data['summary']['deliveries']['Deliveries'].iloc[0]
        deliveries_diff = data['summary']['deliveries']['Diff'].iloc[0]

        open_rate = data['summary']['open_rate']['Open Rate'].iloc[0]
        open_rate_diff = data['summary']['open_rate']['Diff'].iloc[0]

        click_rate = data['summary']['click_to_open_rate']['Click To Open Rate'].iloc[0]
        click_rate_diff = data['summary']['click_to_open_rate']['Diff'].iloc[0]

        email_key = {
            "total_sends": sends,
            "delivery": deliveries,
            "open_rate": open_rate,
            "click_to_open_rate": click_rate,
            "diff_total_sends": sends_diff,
            "diff_delivery": deliveries_diff,
            "diff_open_rate": open_rate_diff,
            "diff_click_to_open_rate": click_rate_diff
        }
        email_key_performance = email_key_performance_response(llm_client, email_key, 6)

        # Step 2: 模型分析
        status_text.text("Step 2/8: Analyzing monthly email delivery and send performance...")
        progress.progress(0.25)

        feature = ["Sends", "Deliveries", "Daily"]

        email_performance_over_time = email_performance_over_time_response(llm_client,
            data['time_series']['delivery'][feature].rename(columns={'Daily': 'date'}))

        # Step 3: 图表生成
        status_text.text("Step 3/8: Analyzing email engagement by address selection and day of the week...")
        progress.progress(0.375)

        email_domain_day_of_week = email_domain_day_of_week_response(llm_client,
            data['breakdowns']['delivery_by_domain'], data['breakdowns']['engagement_by_domain'],
            data['breakdowns']['delivery_by_weekday'], data['breakdowns']['engagement_by_weekday'])

        # Step 4: 结论总结
        status_text.text("Step 4/8: Writing the conclusion of the email analysis report...")
        progress.progress(0.5)

        email_final_report = email_final_result_response(llm_client, email_key_performance,
                                                   email_performance_over_time,
                                                   email_domain_day_of_week)


        # Step 1: 数据预处理
        status_text.text("Step 5/8: Analyzing key metrics comparisons from two months before and after the social media post...")
        progress.progress(0.625)

        engagement_summary_data = get_engagement_summary(sm_data)
        post_performance_summary = get_post_performance_summary(sm_data)

        brand_posts = post_performance_summary["Brand Posts"].iloc[0]
        brand_posts_diff = post_performance_summary['Change in Volume of Published Messages'].iloc[0]

        total_engagements = post_performance_summary["Total Engagements (SUM)"].iloc[0]
        total_engagements_diff = post_performance_summary['Change in Total Engagements'].iloc[0]

        post_like_and_reaction = engagement_summary_data["Post Likes And Reactions (SUM)"].iloc[0]
        post_like_and_reaction_diff = engagement_summary_data['Change in Post Likes And Reactions'].iloc[0]

        posts_shares = engagement_summary_data['Post Shares (SUM)'].iloc[0]
        posts_shares_diff = engagement_summary_data['Change in Post Shares'].iloc[0]

        post_comments = engagement_summary_data['Post Comments (SUM)'].iloc[0]
        post_comments_diff = engagement_summary_data['Change in Post Comments'].iloc[0]

        social_media_key = {
            "brand_posts": brand_posts,
            "total_engagements": total_engagements,
            "post_like_and_reaction": post_like_and_reaction,
            "posts_shares": posts_shares,
            "post_comments": post_comments,
            "brand_posts_diff": brand_posts_diff,
            "total_engagements_diff": total_engagements_diff,
            "post_like_and_reaction_diff": post_like_and_reaction_diff,
            "posts_shares_diff": posts_shares_diff,
            "post_comments_diff": post_comments_diff
        }

        social_media_key_performance = social_media_key_performance_response(llm_client, social_media_key, "", 5)

        # Step 2: 模型分析
        status_text.text("Step 6/8: Analyzing all metrics of monthly social media posts...")
        progress.progress(0.75)

        total_engagement_metrics_on = get_total_engagement_metrics_on(sm_data)

        social_media_posts_over_time = social_media_posts_over_time_response(llm_client,
            total_engagement_metrics_on)

        # Step 3: 图表生成
        status_text.text("Step 7/8: Analyzing daily engagement data from social media...")
        progress.progress(0.875)

        social_engagement_by_time_of = get_social_engagement_by_time_of(sm_data)

        social_media_hourly_engagements = social_media_hourly_engagements_response(llm_client,
            social_engagement_by_time_of)

        # Step 4: 结论总结
        status_text.text("Step 8/8: Writing the conclusion of the social media analysis report...")
        progress.progress(1.0)

        social_media_final_report = social_media_final_result_response(llm_client, social_media_key_performance,
                                                         social_media_posts_over_time,
                                                         social_media_hourly_engagements)

        if email_final_report and social_media_final_report:
            st.success("✅ Report generated successfully！🎉")

            pdf_buffer = generate_pdf("Email Assessment" + "\n\n" + email_final_report + "\n\n" + "Social Media Assessment" + "\n\n" + social_media_final_report)

            # PDF 预览
            st.subheader("📄 PDF Preview：")
            show_pdf(pdf_buffer)

            # 下载按钮
            st.download_button(
                label="📥 Download PDF",
                data=pdf_buffer,
                file_name="ai_report.pdf",
                mime="application/pdf"
            )


# Footer
st.sidebar.markdown("---")
st.sidebar.info("MCCS Email Marketing Analytics Dashboard v1.0")
st.sidebar.markdown("Developed for MCCS marketing team")