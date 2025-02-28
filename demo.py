import streamlit as st
from openai import OpenAI
from langchain_ollama import OllamaLLM
from pandasai import SmartDataframe
import pyarrow.parquet as pq

table = pq.read_table("MCCS_RetailData.parquet")
df = table.to_pandas()

# 初始化 PandasAI（你可以换成本地 LLM）
llm = OllamaLLM(model="llama3:8b")
df = SmartDataframe(df, config={"llm": llm})

# 设置页面标题
st.title("💬AI Data Analysis Agent")

# 在侧边栏添加配置选项
with st.sidebar:
    # 提供一个文本输入框让用户可以手动输入API Key（可选）
    openai_api_key = False
    "[获取 DeepSeek API key](https://platform.deepseek.com/api_keys)"
    if st.button("开启新对话"):
        if "messages" in st.session_state and len(st.session_state.messages) > 0:
            # 保存当前对话到历史对话列表
            if "history_conversations" not in st.session_state:
                st.session_state.history_conversations = []
            st.session_state.history_conversations.append(st.session_state.messages)
            st.session_state.messages = [{"role": "assistant", "content": "欢迎使用对话机器人，你想知道什么?"}]

            # 显示历史对话列表
    st.subheader("历史对话")
    if "history_conversations" in st.session_state:
        for idx, conv in enumerate(st.session_state.history_conversations):
            if st.button(f"对话 {idx + 1}", key=f"load_conv_{idx}"):
                st.session_state.messages = conv
                # st.success(f"成功加载对话 {idx + 1}")

# 检查API Key是否已提供
if openai_api_key:
    st.info("请添加新的API Key")
else:
    # 初始化对话历史记录
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi, this is data analysis robot. What do you want to know?"}]

        # 显示对话历史
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

        # 获取用户输入
    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)

        # 调用DeepSeek API
        response = df.chat(prompt)
        st.chat_message("assistant").write(response)