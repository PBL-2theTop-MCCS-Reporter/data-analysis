from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

def configure_openai_client(api_key=None):
    """Configure the OpenAI client with the provided API key"""
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        api_key=api_key
    )

def create_prompt_from_data(data, question=None):
    """Create a prompt based on the data and optional question"""
    # Extract key metrics
    sends = data['summary']['sends']['Sends'].iloc[0]
    sends_diff = data['summary']['sends']['Diff'].iloc[0]
    
    deliveries = data['summary']['deliveries']['Deliveries'].iloc[0]
    deliveries_diff = data['summary']['deliveries']['Diff'].iloc[0]
    
    bounce_rate = data['summary']['bounce_rate']['Bounce Rate'].iloc[0]
    bounce_rate_diff = data['summary']['bounce_rate']['Diff'].iloc[0]
    
    open_rate = data['summary']['open_rate']['Open Rate'].iloc[0]
    open_rate_diff = data['summary']['open_rate']['Diff'].iloc[0]
    
    click_rate = data['summary']['click_to_open_rate']['Click To Open Rate'].iloc[0]
    click_rate_diff = data['summary']['click_to_open_rate']['Diff'].iloc[0]
    
    unsubscribe_rate = data['summary']['unsubscribe_rate']['Unsubscribe Rate'].iloc[0]
    unsubscribe_rate_diff = data['summary']['unsubscribe_rate']['Diff'].iloc[0]
    
    # Include top domains
    top_domains = data['breakdowns']['delivery_by_domain'].head(5).to_string()
    
    # Include top weekdays
    weekday_data = data['breakdowns']['delivery_by_weekday'].sort_values('Sends', ascending=False).to_string()
    
    # Get audience data if available
    audience_data = ""
    if 'by_audience' in data['breakdowns']:
        audience_data = data['breakdowns']['by_audience'].head(5).to_string()
    
    # Build data prompt
    audience_section = f"Top Audiences:\n{audience_data}" if audience_data else ""

    data_prompt = f"""
    EMAIL MARKETING METRICS:

    Overall Metrics:
    - Total Sends: {sends:,} ({sends_diff})
    - Total Deliveries: {deliveries:,} ({deliveries_diff})
    - Bounce Rate: {bounce_rate:.2%} ({bounce_rate_diff})
    - Open Rate: {open_rate:.2%} ({open_rate_diff})
    - Click to Open Rate: {click_rate:.2%} ({click_rate_diff})
    - Unsubscribe Rate: {unsubscribe_rate:.4%} ({unsubscribe_rate_diff})

    Top Email Domains:
    {top_domains}

    Sends by Day of Week:
    {weekday_data}

    {audience_section}
    """
    
    if question:
        prompt = f"""
        You are an email marketing analyst for MCCS. Based on the following email marketing data, answer this specific question: {question}
        
        {data_prompt}
        
        Provide a thorough answer with data-backed insights. Format your response with clear headings and bullet points where appropriate.
        """
    else:
        prompt = f"""
        You are an email marketing analyst for MCCS. Based on the following email marketing data, provide a comprehensive analysis:

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

def generate_insights(data, question=None, openai_client=None):
    """Generate insights from the data using LangChain"""
    # Use the provided client or create a new one
    if not openai_client:
        openai_client = configure_openai_client()
    
    try:
        # Create prompt
        prompt_content = create_prompt_from_data(data, question)
        
        # Set up LangChain components
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an email marketing analytics expert."),
            ("user", prompt_content)
        ])
        
        # Create and run chain
        chain = prompt | openai_client | StrOutputParser()
        insights = chain.invoke({})
        
        return insights
        
    except Exception as e:
        return f"Error generating insights: {str(e)}"
