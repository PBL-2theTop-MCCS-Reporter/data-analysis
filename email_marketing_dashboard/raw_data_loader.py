import os
import pandas as pd
import re

base_path = "data/rawdata"

def load_raw_data(path = "Social_Media_Perfomance_Jan25.xlsx"):
    file_path = os.path.join(base_path, path)
    xls = pd.ExcelFile(file_path)

    # 用于存储所有 sheet 的数据
    all_sheets_data = {}

    # 遍历所有 sheet
    for sheet_name in xls.sheet_names:
        # 读取整个 sheet
        df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)

        # 解析第一行第一格中的信息
        metadata_text = str(df_raw.iloc[0, 0])  # 第一行第一列数据

        # 解析 Dashboard 名称
        dashboard_match = re.search(r"Dashboard:\s*(.+)", metadata_text)
        dashboard_name = dashboard_match.group(1) if dashboard_match else None

        # 解析 Widget 名称
        widget_match = re.search(r"Widget:\s*(.+)", metadata_text)
        widget_name = widget_match.group(1) if widget_match else None

        # 解析时间范围
        time_match = re.search(r"TIME_INTERVAL:\s*From:(\d{2}-\d{2}-\d{2})\s*To:(\d{2}-\d{2}-\d{2})", metadata_text)
        time_range = (time_match.group(1), time_match.group(2)) if time_match else (None, None)

        # 读取正式数据（从第 3 行开始，跳过前两行）
        df_data = pd.read_excel(xls, sheet_name=sheet_name, skiprows=2)

        # 存储该 sheet 的数据
        all_sheets_data[sheet_name] = {
            'dashboard_name': dashboard_name,
            'widget_name': widget_name,
            'time_range': time_range,
            'data': df_data
        }

    # 打印解析结果
    # for sheet_name, info in all_sheets_data.items():
    #     print(f"Sheet Name: {sheet_name}")
    #     print(f"Dashboard Name: {info['dashboard_name']}")
    #     print(f"Widget Name: {info['widget_name']}")
    #     print(f"Time Interval: {info['time_range']}")
    #     print("\nExtracted DataFrame:")
    #     print(info['data'].head())  # 打印前几行数据
    #     print("\n" + "=" * 50 + "\n")

    return all_sheets_data

# Engagement Summary
def get_engagement_summary(data):
    if data is None:
        data = load_raw_data()
    engagement_summary = data["Engagement Summary"].get('data')

    return engagement_summary

# Post Performance Summary
def get_post_performance_summary(data):
    if data is None:
        data = load_raw_data()
    post_performance_summary = data["Post Performance Summary"].get('data')

    return post_performance_summary

# Total Engagement Metrics on
def get_total_engagement_metrics_on(data):
    if data is None:
        data = load_raw_data()
    total_engagement_metrics_on = data["Total Engagement Metrics on "].get('data')

    total_engagement_metrics_on.rename(columns=lambda x: "Daily" if x == "Date" else x.replace(" (SUM)", ""), inplace=True)

    return total_engagement_metrics_on

# Social Engagement by Time of
def get_social_engagement_by_time_of(data):
    if data is None:
        data = load_raw_data()
    social_engagement_by_time_of = data["Social Engagement by Time of"].get('data')

    social_engagement_by_time_of.rename(columns=lambda x: x.replace(" (SUM)", ""),inplace=True)

    return social_engagement_by_time_of

# Post Engagement Scorecard ac
def get_post_engagement_scorecard_ac(data):
    if data is None:
        data = load_raw_data()
    post_engagement_scorecard_ac = data["Post Engagement Scorecard ac"].get('data')

    post_engagement_scorecard_ac.rename(columns=lambda x: x.replace(" (SUM)", ""), inplace=True)

    return post_engagement_scorecard_ac

# Engagement Distribution by M
# Engagement Reach by Media Ty
def get_media_type(data):
    if data is None:
        data = load_raw_data()
    engagement_distribution_by_m = data["Engagement Distribution by M"].get('data')
    engagement_reach_by_media_ty = data["Engagement Reach by Media Ty"].get('data')

    media_type = pd.merge(engagement_distribution_by_m, engagement_reach_by_media_ty, on='Media Type')

    media_type.rename(columns=lambda x: x.replace(" (SUM)", ""), inplace=True)

    return media_type

