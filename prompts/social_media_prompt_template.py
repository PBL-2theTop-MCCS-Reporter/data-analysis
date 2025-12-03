from langchain.prompts import PromptTemplate

# 社交媒体营销数据分析模板
social_media_marketing_template = PromptTemplate(
    input_variables=["brand_posts", "total_engagements", "post_like_and_reaction", "posts_shares", "post_comments",
                     "brand_posts_diff", "total_engagements_diff", "post_like_and_reaction_diff", "posts_shares_diff",
                     "post_comments_diff",
                     "search_results",
                     "user_feedback",
                     "recommendations_count"],
    template="""
    You are a professional marketing analyst. Based on the provided social media marketing data, relevant information, and user requirement, provide a basic description and {recommendations_count} actionable recommendations.

    **Social Media Marketing Data:**
    - **Brand Posts:** {brand_posts} (Change: {brand_posts_diff})
    - **Total Engagements:** {total_engagements} (Change: {total_engagements_diff})
    - **Post Likes and Reactions:** {post_like_and_reaction} (Change: {post_like_and_reaction_diff})
    - **Post Shares:** {posts_shares} (Change: {posts_shares_diff})
    - **Post Comments:** {post_comments} (Change: {post_comments_diff})

    **Relevant Information:**
    {search_results}

    **User Requirement:**
    {user_feedback}

    **Task:**
    You must prioritize the user's requirement, even if it conflicts with existing goals. Always consider the user's requirement first and ensure your recommendations align with their input.
    """
)

social_media_posts_over_time_template = PromptTemplate(
    input_variables=["total_engagements", "post_likes_and_reactions", "post_comments", "post_shares", "post_reach", "estimated_clicks", "search_results"],
    template="""
    You are a professional marketing analyst. Based on the following social media marketing data analysis results and the retrieved relevant information,
    provide a brief performance summary and two actionable recommendations to improve social media monthly marketing performance.
    Your analysis should be grounded in the data insights provided below, and each recommendation must be supported by specific figures from the data.
    
    **Estimated Clicks Data Analysis Result:**
    - {estimated_clicks}
    
    **Total Engagements Data Analysis Result:**
    - {total_engagements}
    
    **Post Likes and Reactions Data Analysis Result:**
    - {post_likes_and_reactions}
    
    **Post Comments Data Analysis Result:**
    - {post_comments}
    
    **Post Shares Data Analysis Result:**
    - {post_shares}
    
    **Post Reach Data Analysis Result:**
    - {post_reach}
    
    **Search Results:**
    - {search_results}

    **Instruction:**
    1.In the Performance Summary, describing Total Engagements, Post Likes and Reactions, Post Comments, Post Shares, Post Reach and Estimated Clicks with each Data Analysis Result (e.g., date).
    2.In the Recommendations, suggest two specific improvements. Support each recommendation with evidence or statistics from the data and/or search results.
    3.Keep the tone clear, professional, and concise. Avoid generalizations—be data-driven.
 
    """
)

social_media_hourly_engagements_template = PromptTemplate(
    input_variables=["hourly_engagements", "search_results"],
    template="""
    You are a professional marketing analyst. Based on the following social media Total Engagement data for each time slot of each day of the week data analysis results and the retrieved relevant information,
    provide a brief performance summary and two actionable recommendations to improve social media monthly marketing performance.
    Your analysis should be grounded in the data insights provided below, and each recommendation must be supported by specific figures from the data.

    **Estimated Clicks Data Analysis Result:**
    - {hourly_engagements}

    **Search Results:**
    - {search_results}

    **Instruction:**
    1.In the Performance Summary, describing Total engagement data for each time slot of each day of the week data with specific metrics (e.g., date).
    2.In the Recommendations, suggest two specific improvements. Support each recommendation with evidence or statistics from the data and/or search results.
    3.Keep the tone clear, professional, and concise. Avoid generalizations—be data-driven.

    """
)

social_media_final_result_template = PromptTemplate(
    input_variables=["result_0", "result_1", "result_2"],
    template="""
    Act as a marketing analyst. Review the following three analysis results and summarize them into three final insights. Each insight must begin with a concise, clearly written conclusion sentence, followed by supporting details or proposed actions if applicable. 
    
    **Warning**
    Do not include any titles, explanations, or extra text—only output the three numbered insights. Strictly follow the writing style, tone, and structure shown in the example template below.

    **Analysis Result 1:**
    - {result_0}

    **Analysis Result 2:**
    - {result_1}

    **Analysis Result 3:**
    - {result_2}
    
    **Example template:** 
    1.The September 12th post on Instagram was video content created by Buyers, Business OperationsDirectorate, Business & Support Services Division (MR), to drive customers into the store for Deals of theDay. The video featured various products and their prices from a shopper's point of view, similar to another post created from March 11th, 2024, that also had higher than average engagement.
        - Content creation that involves the customer point of view, often showing a customer with a shopping cart that they load with the advertised deals, is tried and true content used by competitors as well - such asTarget.
    2.September 4th and 5th posts both were related to contests for eligible patrons who follow our social media.Historically, contest promotion through social media generates higher than average engagement, and these posts are no exception.
    3.So What: Marketing to continue creation of content that resonates with followers, including video content featuring advertised deals and sharing events that happen at specific installations. to drive social media engagement, which drives brand affinity and encourage footsteps in the door. At present, available resources do not support creation of quality video content required

    """
)

social_media_data_highlight_template = PromptTemplate(
    input_variables=["total_engagements", "post_likes_and_reactions", "post_comments", "post_shares", "post_reach", "estimated_clicks", "hourly_engagements"],
    template="""
    You are an expert in social media. Based on the following metrics summaries, 
    write a **4-point highlight report** summarizing the key social media performance insights.
    
    **Output Requirements:**
    - Output exactly 4 numbered insights (1., 2., 3., 4.).
    - Each point must start with a number and a period (e.g., "1. ...").
    - Each point must be on a separate line.
    - The writing style should be **concise, professional, and data-driven**.
    - The report should summarize *this month’s highlights* — high performance, anomalies, and engagement concentration.
    
    **Analytical Inputs:**
    
    **Estimated Clicks Data Analysis Result:**
    - {estimated_clicks}
    
    **Total Engagements Data Analysis Result:**
    - {total_engagements}
    
    **Post Likes and Reactions Data Analysis Result:**
    - {post_likes_and_reactions}
    
    **Post Comments Data Analysis Result:**
    - {post_comments}
    
    **Post Shares Data Analysis Result:**
    - {post_shares}
    
    **Post Reach Data Analysis Result:**
    - {post_reach}
    
    **Estimated Clicks Data Analysis Result:**
    - {hourly_engagements}
    
    Now write the final 4-point highlight report in English following the exact numbered format.
    """
)