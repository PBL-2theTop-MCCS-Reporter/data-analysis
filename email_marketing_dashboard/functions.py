import streamlit as st

from email_marketing_dashboard.data_loader import load_data
from email_marketing_dashboard.raw_data_loader import get_engagement_summary, get_post_performance_summary, \
    load_raw_data, get_total_engagement_metrics_on, get_social_engagement_by_time_of
from prompts import email_key_performance_response, email_performance_over_time_response, \
    email_domain_day_of_week_response, email_final_result_response, social_media_key_performance_response, \
    social_media_posts_over_time_response, social_media_hourly_engagements_response, social_media_final_result_response
from langchain_ollama import OllamaLLM

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

def generate_email_report():
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
    email_key_performance = email_key_performance_response(email_key, 6)

    # Step 2: 模型分析
    feature = ["Sends", "Deliveries", "Daily"]

    email_performance_over_time = email_performance_over_time_response(
        data['time_series']['delivery'][feature].rename(columns={'Daily': 'date'}))

    # Step 3: 图表生成
    email_domain_day_of_week = email_domain_day_of_week_response(
        data['breakdowns']['delivery_by_domain'], data['breakdowns']['engagement_by_domain'],
        data['breakdowns']['delivery_by_weekday'], data['breakdowns']['engagement_by_weekday'])

    # Step 4: 结论总结
    email_final_report = email_final_result_response(email_key_performance,
                                                     email_performance_over_time,
                                                     email_domain_day_of_week)
    print("==========================================BEGIN GENERATE EMAIL REPORT INFORMATION==========================================")
    return email_final_report

def generate_social_media_report():
    # Step 1: 数据预处理
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

    social_media_key_performance = social_media_key_performance_response(social_media_key, "", 5)

    # Step 2: 模型分析
    total_engagement_metrics_on = get_total_engagement_metrics_on(sm_data)

    social_media_posts_over_time = social_media_posts_over_time_response(
        total_engagement_metrics_on)

    # Step 3: 图表生成
    social_engagement_by_time_of = get_social_engagement_by_time_of(sm_data)

    social_media_hourly_engagements = social_media_hourly_engagements_response(
        social_engagement_by_time_of)

    # Step 4: 结论总结
    social_media_final_report = social_media_final_result_response(social_media_key_performance,
                                                                   social_media_posts_over_time,
                                                                   social_media_hourly_engagements)
    print("==========================================BEGIN GENERATE SOCIAL REPORT INFORMATION==========================================")
    return social_media_final_report