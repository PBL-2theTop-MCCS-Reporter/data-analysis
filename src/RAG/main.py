from src.RAG.data_loader import build_faiss_index, get_faiss_index

build_faiss_index("social_media")

faiss, keys, data = get_faiss_index("social_media")
print(data)

# python -m RAG.main
# 生成时删除main.py 中的src. loader.py中的 src.
# 同时从data-analysis进入src路径下
# 生成完成后恢复
# 输入cd ../ 回到上一路径