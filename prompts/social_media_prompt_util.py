import json

from sentence_transformers import SentenceTransformer
from langchain_ollama import OllamaLLM
from src.RAG.data_loader import get_faiss_index
from .social_media_prompt_template import social_media_marketing_template, social_media_posts_over_time_template, social_media_hourly_engagements_template, social_media_final_result_template
from .parameter_extraction_prompt_util import social_media_parameter_extraction
from .data_analysis_util import analyze_monthly_feature, analyze_hourly_engagements

db_name = "social_media"
transformer_model = "paraphrase-MiniLM-L6-v2"
gpt_model = "llama3:8b"

def social_media_key_performance_response(social_media_data, user_feedback,  k_num = 4):
    print(user_feedback)

    parameter_extraction = json.loads(social_media_parameter_extraction(user_feedback))

    print(parameter_extraction)
    print(type(parameter_extraction))

    # 获取向量数据库
    index, keys, data = get_faiss_index(db_name)
    # 加载嵌入模型
    embedder = SentenceTransformer(transformer_model)
    # 加载GPT模型
    llm = OllamaLLM(model=gpt_model)
    # 加载prompt模版和GPT模型
    email_chain = social_media_marketing_template | llm

    # 生成查询的嵌入
    query_embedding = embedder.encode([str(social_media_data)], convert_to_numpy=True)
    # 在 FAISS 中搜索，获取多个相关的结果（例如，k=3表示返回3个最相关术语）

    distances, indices = index.search(query_embedding, k_num)

    # 获取最相关的术语和文档
    retrieved_terms = [keys[idx] for idx in indices[0]]
    retrieved_documents = [data[term] for term in retrieved_terms]

    # 显示所有相关术语的结果
    for i, retrieved_term in enumerate(retrieved_terms):
        retrieved_document = retrieved_documents[i]
        print(f"Best match {i+1}: {retrieved_term}")
        print(f"Definition: {retrieved_document['Definition']}")
        print(f"Meaning: {retrieved_document['Meaning']}")
        print(f"Analysis Suggestions: {retrieved_document['Analysis Suggestions']}")
        print("-" * 50)

    # 合并所有相关文档作为上下文
    search_results = "\n".join([f"{term}: {document['Definition']} {document['Meaning']} {document['Analysis Suggestions']}"
                         for term, document in zip(retrieved_terms, retrieved_documents)])
    social_media_data["search_results"] = search_results
    social_media_data["user_feedback"] = user_feedback
    social_media_data["recommendations_count"] = parameter_extraction.get("recommendation_count")

    print(social_media_data)

    response = email_chain.invoke(social_media_data)
    return response

def social_media_posts_over_time_response(social_media_data, k_num = 6):
    # 获取向量数据库
    index, keys, data = get_faiss_index(db_name)
    # 加载嵌入模型
    embedder = SentenceTransformer(transformer_model)
    # 加载GPT模型
    llm = OllamaLLM(model=gpt_model)
    # 加载prompt模版和GPT模型
    email_chain = social_media_posts_over_time_template | llm

    # 生成查询的嵌入
    query_embedding = embedder.encode([', '.join(social_media_data.columns.tolist())], convert_to_numpy=True)
    # 在 FAISS 中搜索，获取多个相关的结果（例如，k=3表示返回3个最相关术语）

    distances, indices = index.search(query_embedding, k_num)

    # 获取最相关的术语和文档
    retrieved_terms = [keys[idx] for idx in indices[0]]
    retrieved_documents = [data[term] for term in retrieved_terms]

    # 显示所有相关术语的结果
    for i, retrieved_term in enumerate(retrieved_terms):
        retrieved_document = retrieved_documents[i]
        print(f"Best match {i+1}: {retrieved_term}")
        print(f"Definition: {retrieved_document['Definition']}")
        print(f"Meaning: {retrieved_document['Meaning']}")
        print(f"Analysis Suggestions: {retrieved_document['Analysis Suggestions']}")
        print("-" * 50)

    # 合并所有相关文档作为上下文
    search_results = "\n".join([f"{term}: {document['Definition']} {document['Meaning']} {document['Analysis Suggestions']}"
                         for term, document in zip(retrieved_terms, retrieved_documents)])


    social_media_data = social_media_data.rename(columns={'Daily': 'date'})

    total_engagements = analyze_monthly_feature(social_media_data[["date", "Total Engagements"]],"Total Engagements")
    post_likes_and_reactions = analyze_monthly_feature(social_media_data[["date", "Post Likes And Reactions"]], "Post Likes And Reactions")
    post_comments = analyze_monthly_feature(social_media_data[["date", "Post Comments"]], "Post Comments")
    post_shares = analyze_monthly_feature(social_media_data[["date", "Post Shares"]], "Post Shares")
    post_reach = analyze_monthly_feature(social_media_data[["date", "Post Reach"]], "Post Reach")
    estimated_clicks = analyze_monthly_feature(social_media_data[["date", "Estimated Clicks"]], "Estimated Clicks")

    context = {
        "total_engagements": total_engagements,
        "post_likes_and_reactions": post_likes_and_reactions,
        "post_comments": post_comments,
        "post_shares": post_shares,
        "post_reach": post_reach,
        "estimated_clicks": estimated_clicks,
        "search_results": search_results
    }

    print(context)

    response = email_chain.invoke(context)
    return response

def social_media_hourly_engagements_response(social_media_data, k_num = 1):
    # 获取向量数据库
    index, keys, data = get_faiss_index(db_name)
    # 加载嵌入模型
    embedder = SentenceTransformer(transformer_model)
    # 加载GPT模型
    llm = OllamaLLM(model=gpt_model)
    # 加载prompt模版和GPT模型
    email_chain = social_media_hourly_engagements_template | llm

    # 生成查询的嵌入
    query_embedding = embedder.encode([', '.join(social_media_data.columns.tolist())], convert_to_numpy=True)
    # 在 FAISS 中搜索，获取多个相关的结果（例如，k=3表示返回3个最相关术语）

    distances, indices = index.search(query_embedding, k_num)

    # 获取最相关的术语和文档
    retrieved_terms = [keys[idx] for idx in indices[0]]
    retrieved_documents = [data[term] for term in retrieved_terms]

    # 显示所有相关术语的结果
    for i, retrieved_term in enumerate(retrieved_terms):
        retrieved_document = retrieved_documents[i]
        print(f"Best match {i+1}: {retrieved_term}")
        print(f"Definition: {retrieved_document['Definition']}")
        print(f"Meaning: {retrieved_document['Meaning']}")
        print(f"Analysis Suggestions: {retrieved_document['Analysis Suggestions']}")
        print("-" * 50)

    # 合并所有相关文档作为上下文
    search_results = "\n".join([f"{term}: {document['Definition']} {document['Meaning']} {document['Analysis Suggestions']}"
                         for term, document in zip(retrieved_terms, retrieved_documents)])

    hourly_engagements = analyze_hourly_engagements(social_media_data)

    context = {
        "hourly_engagements": hourly_engagements,
        "search_results": search_results
    }

    response = email_chain.invoke(context)
    return response

def social_media_final_result_response(result_0, result_1, result_2):
    # 加载GPT模型
    llm = OllamaLLM(model=gpt_model)
    # 加载prompt模版和GPT模型
    social_media_chain = social_media_final_result_template | llm

    context = {
        "result_0": result_0,
        "result_1": result_1,
        "result_2": result_2
    }

    response = social_media_chain.invoke(context)
    return response