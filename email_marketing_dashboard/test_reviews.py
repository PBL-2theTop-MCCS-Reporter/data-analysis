import pytest
import re
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline

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

# ==========================================
# Fixtures
# ==========================================
@pytest.fixture
def sample_reviews():
    return [
        "The phone has a good camera and battery life.",
        "Terrible phone, battery drains too fast.",
        "The battery lasts long but the camera is disappointing.",
        "Camera quality is good, but phone overheats.",
        "Love the food and the staff!",
        "Battery life is decent but camera could be better."
    ]


# ==========================================
# 1. OR 匹配 + 正向情感
# ==========================================
def test_or_positive(sample_reviews):
    df = get_top_k_reviews(
        sample_reviews,
        is_negative=False,
        top_k=3,
        keywords=["phone", "battery"],
        match_all=False
    )
    assert isinstance(df, pd.DataFrame)
    assert len(df) <= 3
    # 所有评论必须包含关键词之一
    for review in df["review"]:
        assert "phone" in review.lower() or "battery" in review.lower()


# ==========================================
# 2. OR 匹配 + 负向情感
# ==========================================
def test_or_negative(sample_reviews):
    df = get_top_k_reviews(
        sample_reviews,
        is_negative=True,
        top_k=3,
        keywords=["phone", "battery"],
        match_all=False
    )
    assert isinstance(df, pd.DataFrame)
    # 所有分数必须小于 0
    if not df.empty:
        assert all(df["sentiment_score"] < 0)


# ==========================================
# 3. AND 匹配（match_all=True）
# ==========================================
def test_and_keywords(sample_reviews):
    df = get_top_k_reviews(
        sample_reviews,
        is_negative=False,
        keywords=["camera", "phone"],
        match_all=True
    )
    for review in df["review"]:
        assert "camera" in review.lower()
        assert "phone" in review.lower()


# ==========================================
# 4. AND 匹配但无结果
# ==========================================
def test_and_no_match(sample_reviews):
    df = get_top_k_reviews(
        sample_reviews,
        is_negative=False,
        keywords=["restaurant", "phone"],
        match_all=True
    )
    assert df.empty


# ==========================================
# 5. OR 匹配但全是负面 → 正面应返回空
# ==========================================
def test_only_negative_but_positive_requested(sample_reviews):
    df = get_top_k_reviews(
        sample_reviews,
        is_negative=False,
        keywords=["terrible"]
    )
    assert df.empty


# ==========================================
# 6. 情感不足阈值
# ==========================================
def test_sentiment_not_pass_threshold():
    reviews = ["Battery life is decent but camera could be better."]
    df = get_top_k_reviews(
        reviews,
        is_negative=False,
        keywords=["decent"],
        sentiment_threshold=0.3
    )
    assert df.empty


# ==========================================
# 7. top_k 截断
# ==========================================
def test_top_k_cut(sample_reviews):
    df = get_top_k_reviews(
        sample_reviews,
        is_negative=False,
        keywords=["camera"],
        top_k=1
    )
    assert len(df) <= 1


# ==========================================
# 8. top_k 大于实际数量
# ==========================================
def test_top_k_larger(sample_reviews):
    df = get_top_k_reviews(
        sample_reviews,
        is_negative=True,
        keywords=["battery"],
        top_k=100
    )
    assert len(df) <= len(sample_reviews)


# ==========================================
# 9. 空 review 列表
# ==========================================
def test_empty_reviews_list():
    df = get_top_k_reviews(
        [],
        is_negative=False
    )
    assert df.empty
    assert list(df.columns) == ["review", "sentiment_score"]


# ==========================================
# 10. 长文本（测试截断）
# ==========================================
def test_very_long_text():
    review = "good " * 1000
    df = get_top_k_reviews(
        [review],
        is_negative=False
    )
    # 只测试不报错且 DataFrame 正常
    assert isinstance(df, pd.DataFrame)


# ==========================================
# 11. 非英文文本
# ==========================================
def test_non_english_text():
    reviews = ["这是一个糟糕的产品"]
    df = get_top_k_reviews(
        reviews,
        is_negative=True
    )
    # 可能因 sentiment 分不满足阈值 → 为空 acceptable
    assert isinstance(df, pd.DataFrame)


# ==========================================
# 12. keywords=None
# ==========================================
def test_no_keywords(sample_reviews):
    df = get_top_k_reviews(
        sample_reviews,
        is_negative=False,
        keywords=None
    )
    # 只检查是否正常返回 DataFrame
    assert isinstance(df, pd.DataFrame)
