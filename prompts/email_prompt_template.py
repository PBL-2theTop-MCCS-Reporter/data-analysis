from langchain.prompts import PromptTemplate

# 邮件营销数据分析模板
email_marketing_template = PromptTemplate(
    input_variables=["total_sends", "delivery", "open_rate", "click_to_open_rate",
                     "diff_total_sends", "diff_delivery", "diff_open_rate", "diff_click_to_open_rate","search_results"],
    template="""
    You are a professional marketing analyst. Based on the following email marketing data and the retrieved relevant information, 
    provide a basic description and two actionable recommendations.

    **Current Data:**
    - Total Sends: {total_sends} (Change: {diff_total_sends}%)
    - Delivery: {delivery} (Change: {diff_delivery}%)
    - Open Rate: {open_rate}% (Change: {diff_open_rate}%)
    - Click to Open Rate: {click_to_open_rate}% (Change: {diff_click_to_open_rate}%)
    
    **Search Result:**
    {search_results}

    **Analysis:** Provide a concise summary of the current situation.

    **Recommendations:** Offer two actionable recommendations to improve email marketing performance.
    """
)

email_marketing_over_time_template = PromptTemplate(
    input_variables=["sends", "deliveries", "search_results"],
    template="""
    You are a professional marketing analyst. Based on the following email marketing data analysis results and the retrieved relevant information,
    provide a brief performance summary and two actionable recommendations to improve email monthly marketing performance.
    Your analysis should be grounded in the data insights provided below, and each recommendation must be supported by specific figures from the data.
    The analysis includes three key components: sends data, deliveries data, and search results.

    **Sends Data Analysis Result:**
    - {sends}
    
    **Deliveries Data Analysis Result:**
    - {deliveries}

    **Search Result:**
    - {search_results}
    
    **Instruction:**
    1.In the Performance Summary, highlight key trends or anomalies in sends and deliveries, using specific metrics (e.g., growth rate, peaks, weekday performance).
    2.In the Recommendations, suggest two specific improvements. Support each recommendation with evidence or statistics from the data and/or search results.
    3.Keep the tone clear, professional, and concise. Avoid generalizations—be data-driven.
    
    """
)

email_marketing_email_domain_day_of_week_template = PromptTemplate(
    input_variables=["email_domain", "weekday", "search_results"],
    template="""
    You are a professional marketing analyst. Based on the following email marketing data analysis results and the retrieved relevant information, 
    provide a brief performance summary and two actionable recommendations to improve email marketing performance.
    Your analysis should be grounded in the data insights provided below, and each recommendation must be supported by specific figures from the data.

    The analysis includes three key components: email domain performance, weekday performance, and search results.

    **Email Domain Data Analysis Result:**
    - {email_domain}

    **Weekday Data Analysis Result:**
    - {weekday}

    **Search Result:**
    - {search_results}

    **Instruction:**
    1. In the Performance Summary, highlight key trends or anomalies across email domains and weekdays, using specific metrics (e.g., highest/lowest sends or open rates).
    2. In the Recommendations, suggest two specific improvements. Support each recommendation with evidence or statistics from the data and/or search results.
    3. Maintain a clear, professional, and concise tone. Focus on data-driven insights and avoid vague statements.
    """

)

email_marketing_final_result_template = PromptTemplate(
    input_variables=["result_0", "result_1", "result_2"],
    template="""
    Act as a marketing analyst. Review the following three analysis results and summarize them into three final insights. Each insight must begin with a concise, clearly written conclusion sentence, followed by supporting details or proposed actions if applicable. Do not include any titles, explanations, or extra text—only output the three numbered insights. Strictly follow the writing style, tone, and structure shown in the example template below.
      
    **Example template:** 
    1.To boost overall CTR, Marketing will continue to improve clarity, attractiveness, and relatability of the call-to action‘s on emails and social media.
    2.The Labor Day Promotion generated a 6.8% increase in total sales compared to the previous year, with a majority of digitally available coupons being scanned through mobile (383 mobile scans vs. 172 email scans)
        - Marketing will continue to promote exclusive offers which will highlight time-sensitive deals to create urgency and increase CTR, like we saw with the 72 Hour Anniversary Sale and the Labor Day Promotion.
        - Marketing will consider a mobile-first strategy in which mobile-friendly promotions will be prioritized and integrated into email campaigns, social media, and in-store experiences to further drive conversion.
    3.Opportunity to ensure promotional strategies are executed clearly in-store and store associates are informed of promotions within department, Marketing will partner with Business Operations to identify ways to support.

    **Analysis Result 1:**
    - {result_0}
    
    **Analysis Result 2:**
    - {result_1}
    
    **Analysis Result 3:**
    - {result_2}

    """
)