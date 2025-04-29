from .parameter_extraction_prompt_template import social_media_parameter_extraction_template
from langchain_ollama import OllamaLLM

gpt_model = "llama3:8b"

def social_media_parameter_extraction(user_feedback):
    # 加载GPT模型
    llm = OllamaLLM(model=gpt_model)
    # 加载prompt模版和GPT模型
    email_chain = social_media_parameter_extraction_template | llm

    response = email_chain.invoke(user_feedback)

    return response
