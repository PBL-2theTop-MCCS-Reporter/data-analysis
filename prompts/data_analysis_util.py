import pandas as pd
import numpy as np

def analyze_monthly_feature(df_origin, feature):
    df = df_origin.copy()

    # 基本指标
    avg_feature = df[feature].mean()
    median_feature = df[feature].median()
    std_feature = df[feature].std()
    max_feature = df[feature].max()
    min_feature = df[feature].min()
    max_date = df.loc[df[feature].idxmax(), "date"].strftime("%b %d").lstrip("0").replace(" 0", " ")
    min_date = df.loc[df[feature].idxmin(), "date"].strftime("%b %d").lstrip("0").replace(" 0", " ")

    result_str = (
        f"The average daily {feature} this month is {avg_feature:.0f}, "
        f"with a median of {median_feature:.0f} and a standard deviation of {std_feature:.0f}."
        f"The highest {feature} was on {max_date} ({max_feature} interactions), "
        f"and the lowest was on {min_date} ({min_feature} interactions)."
    )

    # Top 5 占比
    df_sorted = df.sort_values(by=feature, ascending=False)
    top5_sum = df_sorted.head(5)[feature].sum()
    total_sum = df[feature].sum()
    top5_ratio = top5_sum / total_sum * 100
    top5_dates = (
        df_sorted.head(5)["date"]
        .dt.strftime("%b %d")  # 格式化日期为字符串，例如 "Jan 01"
        .str.replace(" 0", " ", regex=False)  # 将 " 0" 替换为 " "，例如 "Jan 01" -> "Jan 1"
    )

    # 峰值检测
    df["prev"] = df[feature].shift(1)
    df["next"] = df[feature].shift(-1)
    df["is_peak"] = df.apply(
        lambda row: row[feature] > 1.3 * max(row["prev"] or 0, row["next"] or 0), axis=1
    )
    peaks = df[df["is_peak"]]
    peak_dates = peaks["date"].dt.strftime("%b %d").str.replace(" 0", " ", regex=False)

    extra_str = (
        f"Top 5 high-engagement days ({', '.join(top5_dates)}) account for {top5_ratio:.1f}% of total {feature}, "
        f"{'indicating a concentration of performance likely driven by specific events.' if top5_ratio > 40 else 'showing a balanced distribution, suggesting effective content management.'}"
        f"Peak detection identified the following days as abnormal high-engagement peaks (possibly driven by special content or campaigns): {', '.join(peak_dates)}."
    )

    print(result_str + extra_str)

    return result_str + extra_str

def analyze_email_domain_performance(sends_domain_df, opens_domain_df) -> str:
    # 标准化
    sends_domain_df["Email Domain"] = sends_domain_df["Email Domain"].str.lower()
    opens_domain_df["Email Domain"] = opens_domain_df["Email Domain"].str.lower()

    # 合并
    merged = pd.merge(sends_domain_df, opens_domain_df, on="Email Domain", how="outer").fillna(0)
    merged["Open Rate"] = merged["Unique Opens"] / merged["Sends"].replace(0, pd.NA)

    # 去除无意义数据
    merged = merged.dropna(subset=["Open Rate"])

    # 排序
    top_sends = merged.sort_values(by="Sends", ascending=False).iloc[0]
    low_sends = merged.sort_values(by="Sends", ascending=True).iloc[0]
    top_opens = merged.sort_values(by="Unique Opens", ascending=False).iloc[0]
    low_opens = merged.sort_values(by="Unique Opens", ascending=True).iloc[0]
    top_rate = merged.sort_values(by="Open Rate", ascending=False).iloc[0]
    low_rate = merged.sort_values(by="Open Rate", ascending=True).iloc[0]

    report = f"""📧 **Email Domain Performance**
- **Most Sent**: {top_sends['Email Domain']} ({int(top_sends['Sends']):,} sends)
- **Least Sent**: {low_sends['Email Domain']} ({int(low_sends['Sends']):,} sends)
- **Most Opens**: {top_opens['Email Domain']} ({int(top_opens['Unique Opens']):,} unique opens)
- **Least Opens**: {low_opens['Email Domain']} ({int(low_opens['Unique Opens']):,} unique opens)
- **Highest Open Rate**: {top_rate['Email Domain']} ({top_rate['Open Rate']:.2%})
- **Lowest Open Rate**: {low_rate['Email Domain']} ({low_rate['Open Rate']:.2%})
"""
    return report


def analyze_weekday_performance(sends_weekday_df, opens_weekday_df) -> str:
    # 合并
    merged = pd.merge(sends_weekday_df, opens_weekday_df, on="Weekday", how="outer").fillna(0)
    merged["Open Rate"] = merged["Unique Opens"] / merged["Sends"].replace(0, pd.NA)
    merged = merged.dropna(subset=["Open Rate"])

    # 排序
    top_sends = merged.sort_values(by="Sends", ascending=False).iloc[0]
    low_sends = merged.sort_values(by="Sends", ascending=True).iloc[0]
    top_opens = merged.sort_values(by="Unique Opens", ascending=False).iloc[0]
    low_opens = merged.sort_values(by="Unique Opens", ascending=True).iloc[0]
    top_rate = merged.sort_values(by="Open Rate", ascending=False).iloc[0]
    low_rate = merged.sort_values(by="Open Rate", ascending=True).iloc[0]

    report = f"""📅 **Weekday Performance**
- **Most Sent**: {top_sends['Weekday']} ({int(top_sends['Sends']):,} sends)
- **Least Sent**: {low_sends['Weekday']} ({int(low_sends['Sends']):,} sends)
- **Most Opens**: {top_opens['Weekday']} ({int(top_opens['Unique Opens']):,} unique opens)
- **Least Opens**: {low_opens['Weekday']} ({int(low_opens['Unique Opens']):,} unique opens)
- **Highest Open Rate**: {top_rate['Weekday']} ({top_rate['Open Rate']:.2%})
- **Lowest Open Rate**: {low_rate['Weekday']} ({low_rate['Open Rate']:.2%})
"""
    return report

def analyze_hourly_engagements(df_origin):
    df = df_origin.copy()

    # 将 'Time Of Day' 列转换为小时整数
    df['Hour'] = pd.to_datetime(df['Time Of Day'], format='%H:%M').dt.hour

    # 设置星期的顺序
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['Day Of Week'] = pd.Categorical(df['Day Of Week'], categories=days_order, ordered=True)

    # 计算每小时平均互动量
    hourly_avg = df.groupby('Hour')['Total Engagements'].mean()

    # 计算每周每日互动总量
    daily_total = df.groupby('Day Of Week')['Total Engagements'].sum()

    # 识别高峰互动时段
    peak_hour = hourly_avg.idxmax()
    peak_hour_value = hourly_avg.max()

    # 识别互动总量最高的星期几
    peak_day = daily_total.idxmax()
    peak_day_value = daily_total.max()

    # 生成文本总结
    summary = []

    # 每小时平均互动量总结
    summary.append("📊 Average Engagement per Hour:")
    for hour in range(24):
        avg = hourly_avg.get(hour, 0)
        summary.append(f"  - {hour:02d}:00: Average engagement is {avg:.2f}")

    # 每周每日互动总量总结
    summary.append("\n📅 Total Engagement per Day of the Week:")
    for day in days_order:
        total = daily_total.get(day, 0)
        summary.append(f"  - {day}: Total engagement is {total}")

    # 高峰互动时段识别总结
    summary.append(f"\n🚀 Peak Engagement Periods:\n  - The most active time slot is {peak_hour:02d}:00, with an average engagement of {peak_hour_value:.2f}")
    summary.append(f"  - The day with the highest total engagement is {peak_day}, with a total engagement of {peak_day_value}")

    print(summary)

    # 返回总结文本
    return "\n".join(summary)


