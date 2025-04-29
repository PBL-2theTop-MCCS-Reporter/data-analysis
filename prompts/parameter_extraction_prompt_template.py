# 参数解析层，如果用户给出了反馈/需求，首先进行解析和提取用户给出的关键信息
# 将这些关键的信息嵌入JSON中并将这些重要的参数提供给下一层进行结果的输出

from langchain.prompts import PromptTemplate

# 社交媒体营销数据分析模板
social_media_parameter_extraction_template = PromptTemplate(
    input_variables=["user_feedback"],
    template="""
    You are a JSON format parameter extract device. Extract the following parameters from the user feedback:

    1. **Number of recommendations** (default: 2)  

    **User Feedback:** "{user_feedback}"

    Return the extracted parameters in JSON format
    {{
        "recommendation_count": <integer>
    }}

    **Important** 
    You MUST only return the JSON and I don't need any other sentences or words
    """
)
