from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns

def configure_openai_client(api_key=None):
    """Configure the OpenAI client with the provided API key"""
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        api_key=api_key
    )

def read_summary_report(file_path='retail_analysis_results/summary_report.txt'):
    """Read the summary report file and extract key metrics"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error reading summary report: {str(e)}")
        return None

def create_prompt_from_retail_data(summary_content, question=None):
    """Create a prompt based on the retail data and optional question"""
    if not summary_content:
        return "Error: No summary content provided."
    
    # Build data prompt
    data_prompt = f"""
    RETAIL SALES DATA ANALYSIS:
    
    {summary_content}
    
    ADDITIONAL CONTEXT:
    - This data represents retail sales from MCCS (Marine Corps Community Services) stores.
    - The analysis includes sales trends, product performance, store performance, and transaction patterns.
    - The data covers both MARINE MART and MAIN STORE formats.
    - Return rates and patterns are included in the analysis.
    """
    
    if question:
        prompt = f"""
        You are a retail analytics expert for MCCS. Based on the following retail sales data, answer this specific question: {question}
        
        {data_prompt}
        
        Provide a thorough answer with data-backed insights. Format your response with clear headings and bullet points where appropriate.
        """
    else:
        prompt = f"""
        You are a retail analytics expert for MCCS. Based on the following retail sales data, provide a comprehensive analysis:

        {data_prompt}
        
        In your analysis, include:
        1. Overall performance summary
        2. Key areas of strength and weakness
        3. Noticeable trends or patterns
        4. Specific recommendations to improve performance
        5. Suggestions for further analysis or experiments
        
        Format your response with clear headings, bullet points where appropriate, and focus on actionable insights.
        """
    
    return prompt

def generate_retail_insights(summary_content=None, question=None, openai_client=None):
    """Generate insights from the retail data using LangChain"""
    # Read summary report if not provided
    if not summary_content:
        summary_content = read_summary_report()
        if not summary_content:
            return "Error: Could not read summary report."
    
    # Use the provided client or create a new one
    if not openai_client:
        openai_client = configure_openai_client()
    
    try:
        # Create prompt
        prompt_content = create_prompt_from_retail_data(summary_content, question)
        
        # Set up LangChain components
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a retail analytics expert specializing in military exchange stores."),
            ("user", prompt_content)
        ])
        
        # Create and run chain
        chain = prompt | openai_client | StrOutputParser()
        insights = chain.invoke({})
        
        return insights
        
    except Exception as e:
        return f"Error generating insights: {str(e)}"

def save_insights_to_file(insights, file_path='retail_analysis_results/llm_insights.md'):
    """Save the generated insights to a file"""
    try:
        with open(file_path, 'w') as f:
            f.write(insights)
        print(f"Insights saved to {file_path}")
        return True
    except Exception as e:
        print(f"Error saving insights: {str(e)}")
        return False

if __name__ == "__main__":
    # This section runs when the script is executed directly
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate LLM insights from retail analysis data')
    parser.add_argument('--api_key', type=str, help='OpenAI API key')
    parser.add_argument('--question', type=str, help='Specific question to ask about the data')
    parser.add_argument('--output', type=str, default='retail_analysis_results/llm_insights.md', 
                        help='Output file path for insights')
    
    args = parser.parse_args()
    
    # Configure OpenAI client
    client = configure_openai_client(args.api_key)
    
    # Generate insights
    insights = generate_retail_insights(question=args.question, openai_client=client)
    
    # Save insights to file
    save_insights_to_file(insights, args.output)
    
    # Print insights to console
    print("\n" + "="*50)
    print("RETAIL ANALYSIS LLM INSIGHTS")
    print("="*50)
    print(insights)
