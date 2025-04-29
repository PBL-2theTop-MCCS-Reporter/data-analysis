import os
import faiss
import pickle
import json

BASE_DB_PATH = os.path.join(os.path.dirname(__file__), "storage")

FAISS_INDEX = "faiss_index.bin"

KEYS = "keys.pkl"

DATA = "data.json"

def get_db_path(db_name):
    """获取指定数据库的存储路径"""
    db_path = os.path.join(BASE_DB_PATH, db_name)
    return db_path

def save_index(index, db_name):
    """存储 FAISS 索引"""
    path = os.path.join(get_db_path(db_name), FAISS_INDEX)
    faiss.write_index(index, path)
    print(f"FAISS 已存储: {path}")

def save_metadata(keys, db_name):
    """存储 keys """
    path = os.path.join(get_db_path(db_name), KEYS)
    with open(path, "wb") as f:
        pickle.dump(keys, f)
    print(f"Keys 已存储: {path}")

def load_index(db_name):
    """加载 FAISS 索引"""
    path = os.path.join(get_db_path(db_name), FAISS_INDEX)
    if not os.path.exists(path):
        raise FileNotFoundError(f"FAISS 文件 {path} 不存在")
    index = faiss.read_index(path)
    print(f"FAISS 索引已加载: {path}")
    return index

def load_metadata(db_name):
    """加载 keys """
    path = os.path.join(get_db_path(db_name), KEYS)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Keys文件 {path} 不存在")
    with open(path, "rb") as f:
        keys = pickle.load(f)
    print(f"Keys 文件已加载: {path}")
    return keys

def load_json_data(db_name):
    """从 JSON 文件加载数据"""
    path = os.path.join(get_db_path(db_name), DATA)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data文件 {path} 不存在")
    with open(path, "r") as f:
        data = json.load(f)
    return data
