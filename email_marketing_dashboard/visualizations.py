import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def plot_metrics_over_time(data, metrics, title=None):
    """Create a time series plot for multiple metrics"""
    if not title:
        title = "Metrics Over Time"
    
    # Create a copy of the data to avoid modifying the original
    data_copy = data.copy()
    
    # Filter to only include metrics that exist in the dataframe
    available_metrics = [m for m in metrics if m in data_copy.columns]
    missing_metrics = [m for m in metrics if m not in data_copy.columns]
    
    if missing_metrics:
        print(f"Warning: Metrics not found in data: {missing_metrics}")
    
    if not available_metrics:
        # Create an empty figure with a message if no metrics are available
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected metrics",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title=title)
        return fig
    
    # Create the figure with available metrics
    fig = px.line(
        data_copy,
        x="Daily",
        y=available_metrics,
        title=title
    )
    
    # Format the chart
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Value",
        legend_title="Metric"
    )
    
    return fig

# Add your other visualization functions below
def plot_email_funnel(funnel_data):
    """Create a funnel chart for email marketing metrics"""
    stages = ['Sends', 'Deliveries', 'Opens', 'Clicks']
    values = [funnel_data[stage] for stage in stages]
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial"
    ))
    
    fig.update_layout(
        title="Email Marketing Funnel",
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def plot_domain_comparison(delivery_domain, engagement_domain):
    """Create a visualization comparing domains for delivery and engagement"""
    if delivery_domain is None or engagement_domain is None:
        # Return empty figure if data is missing
        fig = go.Figure()
        fig.add_annotation(
            text="Domain comparison data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Merge data on Email Domain
    merged = pd.merge(
        delivery_domain, 
        engagement_domain, 
        on='Email Domain', 
        how='outer'
    ).fillna(0)
    
    # Get top 10 domains by sends
    top_domains = merged.sort_values('Sends', ascending=False).head(10)
    
    # Create figure
    fig = px.bar(
        top_domains,
        x='Email Domain',
        y=['Sends', 'Unique Opens'],
        title="Top Email Domains",
        barmode='group'
    )
    
    return fig

def plot_weekly_pattern(delivery_weekday, engagement_weekday):
    """Create a weekly pattern comparison visualization"""
    # Handle None inputs
    if delivery_weekday is None and engagement_weekday is None:
        fig = go.Figure()
        fig.add_annotation(
            text="Weekly pattern data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Create empty DataFrame if None
    if delivery_weekday is None:
        delivery_weekday = pd.DataFrame(columns=['Weekday', 'Sends'])
    
    if engagement_weekday is None:
        engagement_weekday = pd.DataFrame(columns=['Weekday', 'Unique Opens'])
    
    # Order weekdays correctly
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Create figure based on available data
    if not delivery_weekday.empty and 'Sends' in delivery_weekday.columns:
        fig = go.Figure()
        
        # Add delivery data if available
        day_sends = delivery_weekday.set_index('Weekday').reindex(weekday_order).reset_index()
        fig.add_trace(go.Bar(
            x=day_sends['Weekday'], 
            y=day_sends['Sends'],
            name='Sends'
        ))
        
        # Add engagement data if available
        if not engagement_weekday.empty and 'Unique Opens' in engagement_weekday.columns:
            day_opens = engagement_weekday.set_index('Weekday').reindex(weekday_order).reset_index()
            fig.add_trace(go.Bar(
                x=day_opens['Weekday'], 
                y=day_opens['Unique Opens'],
                name='Opens'
            ))
        
        fig.update_layout(
            title="Email Performance by Day of Week",
            xaxis_title="Day of Week",
            yaxis_title="Count",
            barmode='group'
        )
    else:
        # Only engagement data available
        day_opens = engagement_weekday.set_index('Weekday').reindex(weekday_order).reset_index()
        fig = px.bar(
            day_opens,
            x='Weekday',
            y='Unique Opens',
            title="Opens by Day of Week"
        )
    
    return fig

def plot_campaign_performance(campaigns_df, metric):
    """Create a bar chart showing campaign performance by a specific metric"""
    if campaigns_df is None or campaigns_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Campaign data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Check if metric exists
    if metric not in campaigns_df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Metric '{metric}' not found in campaign data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
        
    # Sort campaigns by the metric
    sorted_campaigns = campaigns_df.sort_values(metric, ascending=False)
    
    fig = px.bar(
        sorted_campaigns,
        x='Message Name',
        y=metric,
        title=f"Campaign Performance by {metric}",
        hover_data=['Send Date']
    )
    
    fig.update_layout(
        xaxis_title="Campaign",
        xaxis_tickangle=45
    )
    
    return fig

def plot_audience_performance(audience_df, metric, top_n=10):
    """Create a bar chart showing audience performance by a specific metric"""
    if audience_df is None or audience_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Audience data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Check if metric exists
    if metric not in audience_df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Metric '{metric}' not found in audience data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
        
    # Sort audiences by the metric and take top N
    sorted_audiences = audience_df.sort_values(metric, ascending=False).head(top_n)
    
    fig = px.bar(
        sorted_audiences,
        x='Audience Name',
        y=metric,
        title=f"Top {top_n} Audiences by {metric}"
    )
    
    fig.update_layout(
        xaxis_title="Audience",
        xaxis_tickangle=45
    )
    
    return fig

def plot_heatmap(data, x_axis, y_axis, value_col, title=None):
    """Create a heatmap visualization"""
    if data is None or data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for heatmap",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
        
    # Check if all required columns exist
    required_cols = [x_axis, y_axis, value_col]
    if not all(col in data.columns for col in required_cols):
        fig = go.Figure()
        fig.add_annotation(
            text="One or more required columns missing for heatmap",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Create pivot table
    pivot_data = data.pivot_table(
        values=value_col,
        index=y_axis,
        columns=x_axis,
        aggfunc='mean'
    ).fillna(0)
    
    # Create heatmap
    fig = px.imshow(
        pivot_data,
        title=title or f"Heatmap of {value_col} by {x_axis} and {y_axis}",
        color_continuous_scale='Viridis'
    )
    
    return fig

def plot_weekly_social_media_data(data, metric, title):

    df = pd.DataFrame(data)
    print(df)

    # 使用 Plotly 绘制折线图
    fig = px.line(
        df,
        x = metric[1],
        y = metric[2],
        color = metric[0],  # 按星期分类
        title = title
    )

    # 设置图表格式
    fig.update_layout(
        xaxis_title = metric[1],
        yaxis_title = metric[2],
        legend_title = metric[0],
        xaxis = dict(tickmode="array", tickangle=45)  # 旋转 X 轴刻度，避免重叠
    )

    return fig

def plot_basic_metrics(id_name, data, metric, title):
    # 只保留选中的列
    df_long = data.melt(id_vars=id_name, value_vars=metric, var_name="Metric", value_name="Value")

    # 绘制柱状图
    fig = px.bar(
        df_long,
        x=id_name,
        y="Value",
        color="Metric",  # 不同指标用不同颜色
        barmode="group",  # 分组柱状图
        title=title
    )

    # 更新坐标轴标签
    fig.update_layout(
        xaxis_title=id_name,
        yaxis_title="Value",
        legend_title="Metric"
    )

    return fig
