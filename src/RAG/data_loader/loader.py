from src.RAG.vector_db import save_index, save_metadata, load_json_data, load_index, load_metadata
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

def build_faiss_index(db_name, model = 'paraphrase-MiniLM-L6-v2'):
    """构建 FAISS 索引"""
    # 加载 JSON文件
    data = load_json_data(db_name)

    # 加载 SentenceTransformer 模型
    embedder = SentenceTransformer(model)

    # 解析 JSON 并转换为文本格式
    documents = []
    keys = []

    for key, content in data.items():
        # 使用动态获取键和值并拼接文本
        text = f"{key}: "
        # 动态构建内容（避免硬编码）
        for sub_key, value in content.items():
            text += f"{sub_key}: {value} "
        documents.append(text.strip())  # 移除最后多余的空格
        keys.append(key)

    # 生成嵌入向量
    document_embeddings = embedder.encode(documents, convert_to_numpy=True)

    index = faiss.IndexFlatL2(document_embeddings.shape[1])
    index.add(document_embeddings)

    save_index(index, db_name)
    save_metadata(keys, db_name)
    print(f"向量数据库 `{db_name}` 构建完成！")

def get_faiss_index(db_name):
    # 返回 FAISS 索引文件
    index = load_index(db_name)
    # 返回 Keys 文件
    keys = load_metadata(db_name)
    # 返回 Data json文件
    data = load_json_data(db_name)
    return index, keys, data