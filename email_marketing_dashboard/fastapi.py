from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from data_loader import load_data
from raw_data_loader import (load_raw_data, get_engagement_summary, get_post_performance_summary, get_total_engagement_metrics_on, get_social_engagement_by_time_of)
from prompts import (email_key_performance_response, email_performance_over_time_response, social_media_key_performance_response,
                     email_domain_day_of_week_response, email_final_result_response, social_media_posts_over_time_response,
                     social_media_hourly_engagements_response, social_media_final_result_response, email_data_highlight_response, social_media_data_highlight_response)
from langchain_openai import ChatOpenAI
from PDF_generator_util import generate_pdf

import re
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline

load_dotenv()

# ===============================
# 1. 初始化模型
# ===============================
semantic_model = SentenceTransformer('all-mpnet-base-v2')

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=0 if torch.cuda.is_available() else -1
)

# ===============================
# 2. 情感打分函数（增强鲁棒性）
# ===============================
def get_sentiment_score(text: str) -> float:
    """
    返回一个情感得分:
    - 正面情感时接近 +1
    - 负面情感时接近 -1
    """
    try:
        result = sentiment_pipeline(text[:512])[0]  # 限制长度避免超长报错
        label = result['label']
        score = result['score']
        if label == 'NEGATIVE':
            score = -score
        return score
    except Exception as e:
        print(f"⚠️ 情感分析失败: {e}")
        return 0.0  # 出错时返回中性

# ===============================
# 3. 核心检索函数（优化版本）
# ===============================
def get_top_k_reviews(
    reviews: list[str],
    is_negative: bool = False,
    top_k: int = 3,
    keywords: list[str] | None = None,
    match_all: bool = False,
    sentiment_threshold: float = 0.3
) -> pd.DataFrame:
    """
    根据 query_text (“good reviews” / “bad reviews”) 筛选评论：
    - 支持关键词过滤 (AND / OR)
    - 支持情感方向过滤 (正/负)
    - 仅返回 top_k 条
    """

    if not reviews:
        return pd.DataFrame(columns=["review", "sentiment_score"])

    # ✅ Step 1: 关键词过滤
    filtered_reviews = reviews
    if keywords:
        if match_all:
            def match_all_keywords(text: str) -> bool:
                return all(re.search(re.escape(k), text, re.IGNORECASE) for k in keywords)
            filtered_reviews = [r for r in reviews if match_all_keywords(r)]
        else:
            pattern = re.compile(r"(" + "|".join(re.escape(k) for k in keywords) + r")", re.IGNORECASE)
            filtered_reviews = [r for r in reviews if pattern.search(r)]

    if not filtered_reviews:
        print(f"⚠️ 没有找到符合关键词 {keywords} 的评论。")
        return pd.DataFrame(columns=["review", "sentiment_score"])

    # ✅ Step 2: 情感分析
    sentiment_scores = [get_sentiment_score(r) for r in filtered_reviews]

    df = pd.DataFrame({
        "review": filtered_reviews,
        "sentiment_score": sentiment_scores
    })

    # ✅ Step 3: 确定情感方向（只关注好评 / 差评）

    if is_negative:
        df = df[df["sentiment_score"] < -sentiment_threshold]
        df = df.sort_values(by="sentiment_score", ascending=True)
    else:
        df = df[df["sentiment_score"] > sentiment_threshold]
        df = df.sort_values(by="sentiment_score", ascending=False)

    # ✅ Step 4: 输出 top_k（不足时自动调整）
    df = df.head(min(top_k, len(df))).reset_index(drop=True)

    return df



# ===============================
# 4. 输出函数（小优化）
# ===============================
def build_review_section(good_df, bad_df):
    text = "\n评论过滤的结果\n\n"

    text += "Top Good Reviews\n"
    if good_df.empty:
        text += "（无相关正面评论）\n"
    else:
        for i, row in good_df.iterrows():
            text += f"{i+1}. {row['review']}\n"

    text += "\nTop Bad Reviews\n"
    if bad_df.empty:
        text += "（无相关负面评论）\n"
    else:
        for i, row in bad_df.iterrows():
            text += f"{i+1}. {row['review']}\n"

    return text



# 创建 FastAPI 实例
app = FastAPI(title="废物服务")

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

    reviews = [
        "The phone has an good camera and battery life.",
        "Terrible phone, battery drains too fast.",
        "The battery lasts long but the camera is disappointing.",
        "Camera quality is good, but phone overheats.",
        "Love the food and the staff!",
        "Battery life is decent but camera could be better."
    ]

    top_good = get_top_k_reviews(
        reviews,
        is_negative=False,
        top_k=5,
        keywords=["phone", "battery"],
        match_all=False
    )
    top_bad = get_top_k_reviews(
        reviews,
        is_negative=True,
        top_k=5,
        keywords=["phone", "battery"],
        match_all=False
    )

    review_section = build_review_section(top_good, top_bad)

    print(review_section)

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

    pdf_buffer = generate_pdf(
        "Email Assessment" + "\n\n" + email_report +
        "\n\n" + "Social Media Assessment" + "\n\n" + social_media_report +
        "\n\n" + "Email Highlight" + "\n\n" + email_data_highlight_report +
        "\n\n" + "Social Media Highlight" + "\n\n" + social_media_data_highlight_report +
        "\n\n" + review_section
    )

    # 设置响应为 PDF 文件
    headers = {
        "Content-Disposition": 'inline; filename="assessment_report.pdf"'
        # 如果你想让浏览器直接下载，改成：
        # "Content-Disposition": 'attachment; filename="assessment_report.pdf"'
    }

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers=headers
    )

data = load_data()
sm_data = load_raw_data()
api_key = os.getenv("OPENAI_API_KEY")

# --- LLM Client Configuration ---
def get_llm_client(api_key):
    """
    Returns an LLM client. Prioritizes OpenAI if an API key is provided,
    otherwise falls back to a local Ollama model.
    """
    # Prioritize sidebar input, then environment variable
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=api_key)

llm_client = get_llm_client(api_key)

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

    # Step 5: 数据高光
    # email_data_highlight_report = email_data_highlight_response(llm_client, data['breakdowns']['delivery_by_domain'], data['breakdowns']['engagement_by_domain'],
    #     data['breakdowns']['delivery_by_weekday'], data['breakdowns']['engagement_by_weekday'], data['time_series']['delivery'][feature].rename(columns={'Daily': 'date'}))

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

    # Step 5: 数据高光
    # social_media_data_highlight_report = social_media_data_highlight_response(llm_client, total_engagement_metrics_on, social_engagement_by_time_of)

    return social_media_final_report

def build_review_section(good_df, bad_df):
    # 评论标题
    text = "\nResults of Comments Filtering\n\n"
    text += "Top Good Reviews\n"
    for i, row in good_df.iterrows():
        text += f"{i+1}. {row['review']}\n"

    text += "\nTop Bad Reviews\n"
    for i, row in bad_df.iterrows():
        text += f"{i+1}. {row['review']}\n"

    return text

