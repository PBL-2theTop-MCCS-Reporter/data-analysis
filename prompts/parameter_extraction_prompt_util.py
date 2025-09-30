from .parameter_extraction_prompt_template import social_media_parameter_extraction_template
from langchain_core.output_parsers import StrOutputParser

def social_media_parameter_extraction(llm_client, user_feedback):
    # 加载prompt模版和GPT模型
    extraction_chain = social_media_parameter_extraction_template | llm_client | StrOutputParser()

    response = extraction_chain.invoke(user_feedback)

    return response
