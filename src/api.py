from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from email_marketing_dashboard.data_loader import load_data
from email_marketing_dashboard.raw_data_loader import (load_raw_data, get_engagement_summary, get_post_performance_summary, get_total_engagement_metrics_on, get_social_engagement_by_time_of)
from prompts import (email_key_performance_response, email_performance_over_time_response, social_media_key_performance_response,
                     email_domain_day_of_week_response, email_final_result_response, social_media_posts_over_time_response,
                     social_media_hourly_engagements_response, social_media_final_result_response, email_data_highlight_response, social_media_data_highlight_response)
from langchain_openai import ChatOpenAI
from email_marketing_dashboard.PDF_generator_util import generate_pdf

# 创建 FastAPI 实例
app = FastAPI(title="GoodBye")

# 定义请求体（可选）
class Item(BaseModel):
    name: str

# 暴露 GET 接口
@app.get("/")
def echo_item():
    return {"message": "PDF Generation Function"}

@app.get("/download-pdf")
def read_root():
    email_report = generate_email_report()
    social_media_report = generate_social_media_report()

    # 数据高光
    total_engagement_metrics_on = get_total_engagement_metrics_on(sm_data)
    social_engagement_by_time_of = get_social_engagement_by_time_of(sm_data)
    social_media_data_highlight_report = social_media_data_highlight_response(llm_client, total_engagement_metrics_on,
                                                                              social_engagement_by_time_of)
    feature = ["Sends", "Deliveries", "Daily"]
    email_data_highlight_report = email_data_highlight_response(llm_client, data['breakdowns']['delivery_by_domain'],
                                                                data['breakdowns']['engagement_by_domain'],
                                                                data['breakdowns']['delivery_by_weekday'],
                                                                data['breakdowns']['engagement_by_weekday'],
                                                                data['time_series']['delivery'][feature].rename(
                                                                    columns={'Daily': 'date'}))

    # pdf_buffer = generate_pdf(
    #     "Email Assessment" + "\n\n" + email_report +
    #     "\n\n" + "Social Media Assessment" + "\n\n" + social_media_report +
    #     "\n\n" + "Email Highlight" + "\n\n" + email_data_highlight_report +
    #     "\n\n" + "Social Media Highlight" + "\n\n" + social_media_data_highlight_report
    # )
    #
    # # 设置响应为 PDF 文件
    # headers = {
    #     "Content-Disposition": 'inline; filename="assessment_report.pdf"'
    #     # 如果你想让浏览器直接下载，改成：
    #     # "Content-Disposition": 'attachment; filename="assessment_report.pdf"'
    # }

    return (
            "Email Assessment\n\n" + email_report +
            "\n\nSocial Media Assessment\n\n" + social_media_report +
            "\n\nEmail Highlight\n\n" + email_data_highlight_report +
            "\n\nSocial Media Highlight\n\n" + social_media_data_highlight_report
    )

    # return StreamingResponse(
    #     pdf_buffer,
    #     media_type="application/pdf",
    #     headers=headers
    # )

data = load_data()
sm_data = load_raw_data()
# --- LLM Client Configuration ---
def get_llm_client():
    """
    Returns an LLM client. Prioritizes OpenAI if an API key is provided,
    otherwise falls back to a local Ollama model.
    """
    # Prioritize sidebar input, then environment variable
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    print(api_key)
    if api_key and api_key.startswith(("'", '"')):
        api_key = api_key.strip("'\"")
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=api_key)

llm_client = get_llm_client()

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
    email_key_performance = email_key_performance_response(llm_client, email_key, 6)

    # Step 2: 模型分析
    feature = ["Sends", "Deliveries", "Daily"]

    email_performance_over_time = email_performance_over_time_response(llm_client,
        data['time_series']['delivery'][feature].rename(columns={'Daily': 'date'}))

    # Step 3: 图表生成
    email_domain_day_of_week = email_domain_day_of_week_response(llm_client,
        data['breakdowns']['delivery_by_domain'], data['breakdowns']['engagement_by_domain'],
        data['breakdowns']['delivery_by_weekday'], data['breakdowns']['engagement_by_weekday'])

    # Step 4: 结论总结
    email_final_report = email_final_result_response(llm_client, email_key_performance,
                                                     email_performance_over_time,
                                                     email_domain_day_of_week)

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

    social_media_key_performance = social_media_key_performance_response(llm_client, social_media_key, "", 5)

    # Step 2: 模型分析
    total_engagement_metrics_on = get_total_engagement_metrics_on(sm_data)

    social_media_posts_over_time = social_media_posts_over_time_response(llm_client,
        total_engagement_metrics_on)

    # Step 3: 图表生成
    social_engagement_by_time_of = get_social_engagement_by_time_of(sm_data)

    social_media_hourly_engagements = social_media_hourly_engagements_response(llm_client,
        social_engagement_by_time_of)

    # Step 4: 结论总结
    social_media_final_report = social_media_final_result_response(llm_client, social_media_key_performance,
                                                                   social_media_posts_over_time,
                                                                   social_media_hourly_engagements)

    return social_media_final_report

