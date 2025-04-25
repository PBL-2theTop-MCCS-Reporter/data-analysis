import pandas as pd
import numpy as np

def generate_email_insights(delivery_data, engagement_data):
    """Generate insights from email marketing data"""
    
    # Calculate key metrics
    total_sends = delivery_data['Sends'].sum() if 'Sends' in delivery_data.columns else 0
    total_deliveries = delivery_data['Deliveries'].sum() if 'Deliveries' in delivery_data.columns else 0
    delivery_rate = total_deliveries / total_sends if total_sends > 0 else 0
    bounce_rate = delivery_data['Bounce Rate'].mean() if 'Bounce Rate' in delivery_data.columns else 0
    
    open_rate = engagement_data['Open Rate'].mean() if 'Open Rate' in engagement_data.columns else 0
    click_rate = engagement_data['Click Rate'].mean() if 'Click Rate' in engagement_data.columns else 0
    
    # Generate insights
    insights = f"""
    # Email Marketing Insights
    
    ## Key Metrics
    - Total Sends: {total_sends:,}
    - Total Deliveries: {total_deliveries:,}
    - Delivery Rate: {delivery_rate:.2%}
    - Average Bounce Rate: {bounce_rate:.2%}
    - Average Open Rate: {open_rate:.2%}
    - Average Click Rate: {click_rate:.2%}
    
    ## Insights
    1. The email campaigns show an overall delivery rate of {delivery_rate:.2%}, with a bounce rate of {bounce_rate:.2%}.
    2. The open rate is {open_rate:.2%}, which is {'above' if open_rate > 0.20 else 'below'} industry average.
    3. Click rates are at {click_rate:.2%}, suggesting {'good' if click_rate > 0.02 else 'room for improvement in'} content engagement.
    
    ## Recommendations
    - Focus on improving email deliverability by cleaning your email lists regularly.
    - Test different subject lines to improve open rates.
    - Enhance call-to-action elements to improve click rates.
    """
    
    return insights