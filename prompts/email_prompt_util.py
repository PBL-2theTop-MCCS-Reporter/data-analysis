from src.RAG.data_loader import get_faiss_index
from langchain_core.output_parsers import StrOutputParser
from .email_prompt_template import email_marketing_template, email_marketing_over_time_template, email_marketing_email_domain_day_of_week_template, email_marketing_final_result_template
from .data_analysis_util import analyze_monthly_feature, analyze_email_domain_performance, analyze_weekday_performance
from src.RAG.embedding_client import EmbeddingClient
import numpy as np

db_name = "email"

# Lazily initialize the embedder to be shared across functions
_embedder = None
def get_embedder(llm_client):
    global _embedder
    if _embedder is None:
        api_key = getattr(llm_client, 'api_key', None)
        _embedder = EmbeddingClient(openai_api_key=api_key)
    return _embedder

def email_key_performance_response(llm_client, email_data, recommendations_count=6, k_num=4):
    # 获取向量数据库
    index, keys, data = get_faiss_index(db_name)
    # 加载prompt模版和GPT模型
    email_chain = email_marketing_template | llm_client | StrOutputParser()

    embedder = get_embedder(llm_client)
    query_embedding = np.array(embedder.encode([str(email_data)]))
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
    email_data["search_results"] = search_results
    email_data["recommendations_count"] = recommendations_count

    response = email_chain.invoke(email_data)
    return response

def email_performance_over_time_response(llm_client, email_data, k_num = 2):
    # 获取向量数据库
    index, keys, data = get_faiss_index(db_name)
    # 加载prompt模版和GPT模型
    email_chain = email_marketing_over_time_template | llm_client | StrOutputParser()

    embedder = get_embedder(llm_client)
    query_embedding = np.array(embedder.encode([', '.join(email_data.columns.tolist())]))
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

    sends = analyze_monthly_feature(email_data[["date", "Sends"]], "Sends")
    deliveries = analyze_monthly_feature(email_data[["date", "Deliveries"]], "Deliveries")

    context = {
        "sends": sends,
        "deliveries": deliveries,
        "search_results": search_results
    }

    response = email_chain.invoke(context)
    return response

def email_domain_day_of_week_response(llm_client, email_domain_sends, email_domain_unique_opens, email_weekday_sends, email_weekday_unique_opens, k_num = 2):
    # 获取向量数据库
    index, keys, data = get_faiss_index(db_name)
    # 加载prompt模版和GPT模型
    email_chain = email_marketing_email_domain_day_of_week_template | llm_client | StrOutputParser()

    embedder = get_embedder(llm_client)
    query_embedding = np.array(embedder.encode(['Sends, Unique Opens']))
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


    email_domain = analyze_email_domain_performance(email_domain_sends, email_domain_unique_opens)
    weekday = analyze_weekday_performance(email_weekday_sends, email_weekday_unique_opens)

    print(email_domain)
    print(weekday)

    context = {
        "email_domain": email_domain,
        "weekday": weekday,
        "search_results": search_results
    }

    response = email_chain.invoke(context)
    return response

def email_final_result_response(llm_client, result_0, result_1, result_2):
    # 加载prompt模版和GPT模型
    email_chain = email_marketing_final_result_template | llm_client | StrOutputParser()

    context = {
        "result_0": result_0,
        "result_1": result_1,
        "result_2": result_2
    }

    response = email_chain.invoke(context)
    return response
