import pandas as pd
import os

def load_data():
    """Load all relevant CSV files and return as structured dictionary"""

    

    # Get the directory where the current script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(current_dir)
    # Construct the path to data directory
    base_path = os.path.join(project_root, "data", "convertedcsv")

    
    data = {
        'summary': {},
        'time_series': {},
        'breakdowns': {}
    }
    
    # Load summary metrics
    data['summary']['deliveries'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Deliveries', 'Advertising_Email_Deliveries.xlsx-Deliveries.csv'))
    data['summary']['sends'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Deliveries', 'Advertising_Email_Deliveries.xlsx-Sends.csv'))
    data['summary']['bounce_rate'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Deliveries', 'Advertising_Email_Deliveries.xlsx-Bounce_Rate.csv'))
    data['summary']['open_rate'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-Open_Rate.csv'))
    data['summary']['unique_opens'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-Unique_Opens.csv'))
    data['summary']['unique_clicks'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-Unique_Clicks.csv'))
    data['summary']['click_to_open_rate'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-Click_to_Open_Rate.csv'))
    data['summary']['unique_unsubscribes'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-Unique_Unsubscribes.csv'))
    data['summary']['unsubscribe_rate'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-Unsubscribe_Rate.csv'))
    
    # Load time series data - with more detailed debugging
    csv_path = os.path.join(base_path, 'Advertising_Email_Deliveries', 'Advertising_Email_Deliveries.xlsx-Email_Deliveries_Delivery_Timel.csv')
    print(f"Loading CSV from: {csv_path}")
    print(f"File exists: {os.path.exists(csv_path)}")
    
    try:
        delivery_time = pd.read_csv(csv_path)
        
        delivery_time['Daily'] = pd.to_datetime(delivery_time['Daily'])
        
        # Strip whitespace from all column names
        delivery_time.columns = delivery_time.columns.str.strip()

        # Create Bounce Rate column if it doesn't exist
        bounce_rate_col = None
        for col in delivery_time.columns:
            if 'bounce' in col.lower() and 'rate' in col.lower():
                bounce_rate_col = col
                break
                
        if bounce_rate_col and bounce_rate_col != 'Bounce Rate':
            delivery_time = delivery_time.rename(columns={bounce_rate_col: 'Bounce Rate'})
        elif not any('bounce' in col.lower() and 'rate' in col.lower() for col in delivery_time.columns):
            if 'Bounces' in delivery_time.columns and 'Sends' in delivery_time.columns:
                delivery_time['Bounce Rate'] = delivery_time['Bounces'] / delivery_time['Sends']
            
        data['time_series']['delivery'] = delivery_time
        
    except Exception as e:
        print(f"Error loading delivery time data: {e}")
        # Create an empty DataFrame with the required columns as a fallback
        data['time_series']['delivery'] = pd.DataFrame(columns=['Daily', 'Sends', 'Deliveries', 'Delivery Rate', 'Bounces', 'Bounce Rate'])
    
    # Load engagement time data
    try:
        engagement_time = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-Email_Engagement_Engagement_Tim.csv'))
        engagement_time['Daily'] = pd.to_datetime(engagement_time['Daily'])
        # Make sure all column names are stripped
        engagement_time.columns = engagement_time.columns.str.strip()
        data['time_series']['engagement'] = engagement_time
    except Exception as e:
        print(f"Error loading engagement time data: {e}")
        data['time_series']['engagement'] = pd.DataFrame(columns=['Daily', 'Open Rate', 'Click Rate', 'Click to Open Rate', 'Unsubscribe Rate'])
    
    # Load breakdowns
    try:
        data['breakdowns']['delivery_by_domain'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Deliveries', 'Advertising_Email_Deliveries.xlsx-By_Email_Domain.csv'))
        data['breakdowns']['engagement_by_domain'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-By_Email_Domain.csv'))
        data['breakdowns']['delivery_by_weekday'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Deliveries', 'Advertising_Email_Deliveries.xlsx-By_Day_of_the_Week.csv'))
        data['breakdowns']['engagement_by_weekday'] = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-By_Day_of_the_Week.csv'))
    except Exception as e:
        print(f"Error loading breakdown data: {e}")
    
    # Load details
    data['details'] = {}
    try:
        delivery_details = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Deliveries', 'Advertising_Email_Deliveries.xlsx-Email_Deliveries_Details.csv'))
        delivery_details['Send Date'] = pd.to_datetime(delivery_details['Send Date'])
        data['details']['delivery'] = delivery_details
        
        engagement_details = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-Email_Engagement_Details.csv'))
        engagement_details['Send Date'] = pd.to_datetime(engagement_details['Send Date'])
        data['details']['engagement'] = engagement_details
    except Exception as e:
        print(f"Error loading details data: {e}")
    
    return data

def get_email_funnel_data(data):
    """Extract email funnel metrics from the data"""
    funnel = {
        'Sends': data['summary']['sends']['Sends'].iloc[0],
        'Deliveries': data['summary']['deliveries']['Deliveries'].iloc[0],
        'Opens': data['summary']['unique_opens']['Unique Opens'].iloc[0],
        'Clicks': data['summary']['unique_clicks']['Unique Clicks'].iloc[0],
        'Unsubscribes': data['summary']['unique_unsubscribes']['Unique Unsubscribes'].iloc[0]
    }
    
    return funnel

def get_performance_vs_previous(data):
    """Extract performance vs previous period"""
    performance = {}
    
    for metric, df in data['summary'].items():
        if 'Diff' in df.columns:
            # Extract numeric value from diff string if needed
            diff_value = df['Diff'].iloc[0]
            if isinstance(diff_value, str) and '(' in diff_value:
                # Extract percentage
                performance[metric] = diff_value.split('(')[0].strip()
            else:
                performance[metric] = diff_value
    
    return performance

def load_data_simple():
    """Simple version that returns just the three main dataframes"""


    # Get the directory where the current script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(current_dir)
    # Construct the path to data directory
    base_path = os.path.join(project_root, "data", "convertedcsv")

    
    # Load delivery data
    delivery_daily = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Deliveries', 'Advertising_Email_Deliveries.xlsx-Email_Deliveries_Delivery_Timel.csv'))
    delivery_daily['Daily'] = pd.to_datetime(delivery_daily['Daily'])
    
    # Load engagement data
    engagement_daily = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-Email_Engagement_Engagement_Tim.csv'))
    engagement_daily['Daily'] = pd.to_datetime(engagement_daily['Daily'])
    
    # Load email details
    try:
        email_details = pd.read_csv(os.path.join(base_path, 'Advertising_Email_Engagement', 'Advertising_Email_Engagement.xlsx-Email_Engagement_Details.csv'))
        if 'Send Date' in email_details.columns:
            email_details['Send Date'] = pd.to_datetime(email_details['Send Date'])
    except:
        email_details = pd.DataFrame()
        
    return delivery_daily, engagement_daily, email_details
