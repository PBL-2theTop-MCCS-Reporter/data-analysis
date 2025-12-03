import torch
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import re

# ===============================
# 1. 初始化模型
# ===============================
# SBERT语义编码器
semantic_model = SentenceTransformer('all-mpnet-base-v2')

# 情感分析模型 (英语二分类)
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=0 if torch.cuda.is_available() else -1
)

# ===============================
# 2. 情感打分函数
# ===============================
def get_sentiment_score(text: str) -> float:
    """
    返回一个情感得分:
    - 正面情感时接近 +1
    - 负面情感时接近 -1
    """
    result = sentiment_pipeline(text)[0]
    label = result['label']
    score = result['score']
    if label == 'NEGATIVE':
        score = -score
    return score

# ===============================
# 3. 核心检索函数
# ===============================
def get_top_k_reviews(
    reviews: list[str],
    query_text: str,
    top_k: int = 3,
    candidate_N: int = 50,
    keywords: list[str] | None = None,
    match_all: bool = False
) -> pd.DataFrame:
    """
    从评论中筛选与 query_text 语义最相近的评论，并用情感模型进一步排序
    - reviews: 评论列表
    - query_text: 查询语义，比如 "good reviews" 或 "bad reviews"
    - top_k: 输出的Top K
    - candidate_N: 初筛N条
    - keywords: 关键词列表，比如 ["phone", "battery"]
    - match_all: 若为 True，则评论需同时包含所有关键词（逻辑AND）；否则任意匹配即可（逻辑OR）
    """

    # Step 0: 关键词过滤
    if keywords:
        if match_all:
            # 同时包含所有关键词（AND逻辑）
            def match_all_keywords(text: str) -> bool:
                return all(re.search(re.escape(k), text, re.IGNORECASE) for k in keywords)
            filtered_reviews = [r for r in reviews if match_all_keywords(r)]
        else:
            # 包含任意一个关键词（OR逻辑）
            pattern = re.compile(r"(" + "|".join(re.escape(k) for k in keywords) + r")", re.IGNORECASE)
            filtered_reviews = [r for r in reviews if pattern.search(r)]

        if not filtered_reviews:
            print(f"⚠️ 没有找到符合关键词 {keywords}（match_all={match_all}）的评论。")
            return pd.DataFrame(columns=["review", "semantic_score", "sentiment_score"])
    else:
        filtered_reviews = reviews

    # Step 1: 向量化
    review_embeddings = semantic_model.encode(filtered_reviews, convert_to_tensor=True)
    query_embedding = semantic_model.encode(query_text, convert_to_tensor=True)

    # Step 2: 相似度计算
    cosine_scores = util.cos_sim(query_embedding, review_embeddings)[0].cpu().numpy()

    # Step 3: 初筛Top N
    top_indices = np.argsort(-cosine_scores)[:candidate_N]
    candidate_reviews = [filtered_reviews[i] for i in top_indices]
    candidate_scores = [cosine_scores[i] for i in top_indices]

    # Step 4: 情感分析
    sentiment_scores = [get_sentiment_score(r) for r in candidate_reviews]

    # Step 5: 情感排序
    df = pd.DataFrame({
        'review': candidate_reviews,
        'semantic_score': candidate_scores,
        'sentiment_score': sentiment_scores
    })

    if "bad" in query_text.lower() or "negative" in query_text.lower():
        df = df.sort_values(by=['sentiment_score', 'semantic_score'], ascending=[True, False])
    else:
        df = df.sort_values(by=['sentiment_score', 'semantic_score'], ascending=[False, False])

    return df.head(top_k).reset_index(drop=True)

def build_review_section(good_df, bad_df):
    # 评论标题
    text = "\n评论过滤的结果\n\n"
    text += "Top Good Reviews\n"
    for i, row in good_df.iterrows():
        text += f"{i+1}. {row['review']}\n"

    text += "\nTop Bad Reviews\n"
    for i, row in bad_df.iterrows():
        text += f"{i+1}. {row['review']}\n"

    return text

if __name__ == "__main__":
    reviews = [
        "The phone has an amazing camera and battery life.",
        "Terrible phone, battery drains too fast.",
        "The battery lasts long but the camera is disappointing.",
        "Camera quality is good, but phone overheats.",
        "Love the food and the staff!",
        "Battery life is decent but camera could be better."
    ]

    # 1️⃣ OR 逻辑：只要包含 phone 或 battery 即可
    top_good_or = get_top_k_reviews(
        reviews,
        query_text="good reviews",
        top_k=3,
        keywords=["phone", "battery"],
        match_all=False
    )
    print("=== Top 3 Good Reviews (OR logic) ===")
    print(top_good_or)

    # 2️⃣ AND 逻辑：必须同时包含 phone 和 battery
    top_bad_and = get_top_k_reviews(
        reviews,
        query_text="bad reviews",
        top_k=3,
        keywords=["phone", "battery"],
        match_all=True
    )
    print("\n=== Top 3 Bad Reviews (AND logic) ===")
    print(top_bad_and)



