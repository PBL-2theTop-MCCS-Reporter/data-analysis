import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import time
import base64
from report import create_pdf, create_doc
import sys
import os


# Import retail_llm_insights
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
import retail_llm_insights
from email_marketing_dashboard.functions import generate_email_report, generate_social_media_report

load_dotenv()

# def get_img_as_base64(file):
#     with open(file, "rb") as f:
#         data = f.read()
#     return base64.b64encode(data).decode()
#
#
# header_img = get_img_as_base64("images/MCCS-header.png")

# style = f"""
# <style>
# [data-testid="stHeader"] {{
#     background-image: url("data:image/png;base64,{header_img}");
#     background-size: cover;
# }}

style = f"""
<style>
[data-testid="stForm"] {{
    background-color: rgb(250,250,250);
    border: none;
}}

[data-testid="stSelectbox"] > div > div {{
    background-color: white;
}}

[data-testid="stFormSubmitButton"] {{
    align: center;
}}

[data-testid="stFormSubmitButton"] > button {{
    background-color: #052c65;
    color: white;
    border: none;
}}

[data-testid="stTextInputRootElement"] > div > input {{
    background-color: white;
}}

# background-color: rgb(232, 244, 233);
# color: rgb(23, 114, 51);
# background-color: rgb(252, 233, 233);
# color: rgb(125, 53, 58);

</style>
"""
# session states
if "quick_options_status" not in st.session_state:
    st.session_state.quick_options_status = "Not Active"

if "query_status" not in st.session_state:
    st.session_state.query_status = "Not Active"

if "generated_pdf" not in st.session_state:
    st.session_state.generated_pdf = ""

if "generated_doc" not in st.session_state:
    st.session_state.generated_doc = ""

if "query" not in st.session_state:
    st.session_state.query = ""

# functions
def quick_options_status_update(new_state):
    st.session_state.quick_options_status = new_state
    st.session_state.query_status = "Not Active"

def query_status_update(new_state):
    st.session_state.query_status = new_state
    st.session_state.quick_options_status = "Not Active"

def generate_report():
    assessments = generate_email_report()
    social_media_report = generate_social_media_report()
    # For testing:
#     assessments = """
# 1. To boost overall email performance, Marketing will optimize subject lines and A/B test different options to increase open rates. Additionally, regular cleaning and purging of the email list is crucial to maintain a healthy list and improve delivery rates.
# 2. Marketing will capitalize on high-engagement days by amplifying specific content or campaigns that drove high engagement during peak days, which account for 40.7% of total sends.
# 3. To improve email marketing performance, Marketing will optimize email content for low-performing domains like aol.com and leverage best-performing weekdays like Friday for maximum impact, with the highest sends (304,410) and opens (96,472).
#     """
#
#     social_media_report = """
# 1. The social media campaign's engagement levels vary across different time slots and days of the week, with the most active time slot being 19:00. It is crucial to optimize the content strategy for peak engagement hours by leveraging the audience's preferences for interactive content such as polls, questions, or giveaways.
#     - Evidence: The most active time slot is 19:00, with an average engagement of 711.14.
#
# 2. With Thursday having the highest total engagement at 10220, it is essential to develop content strategies that cater to this day specifically. This could involve sharing more engaging and informative content such as educational posts, news updates, or industry insights, which are likely to resonate with the audience on weekdays.
#     - Evidence: Thursday has the highest total engagement at 10220, indicating a strong audience response to content shared on this day.
#
# 3. To boost social media engagement, it is necessary to focus on creating high-quality, relevant, and diverse content that resonates with the audience. This can be achieved by asking thought-provoking questions, sharing user-generated content, or hosting social media contests that drive brand loyalty and advocacy.
#     - Evidence: The provided social media marketing data shows a decline in engagement metrics (Posts, Total Engagements, Post Likes and Reactions) despite an increase in post shares and comments.
#
#     """
    pdf_buffer = create_pdf(report_time_range[0], report_time_range[1], assessments, social_media_report)
    st.session_state.generated_pdf = pdf_buffer
    doc_buffer = create_doc(report_time_range[0], report_time_range[1], assessments, social_media_report)
    st.session_state.generated_doc = doc_buffer

def generate_report_with_prompt(prompt):
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key is None:
        raise ValueError("OPENAI_API_KEY not found in environment. Did you forget to load .env? If so, please create .env in your root directory, and store your api key in the OPENAI_API_KEY environment variable.")
    open_ai_client = retail_llm_insights.configure_openai_client(api_key=api_key)

    summary_content = retail_llm_insights.read_summary_report()
    insights = retail_llm_insights.generate_retail_insights(
        summary_content=summary_content,
        question=prompt,
        openai_client=open_ai_client,
    )
    pdf_buffer = retail_llm_insights.markdown_to_pdf_buffer(insights)
    st.session_state.generated_pdf = pdf_buffer

current_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime("%Y-%m")
date_range = pd.date_range(start="2024-08", end=current_month, freq="MS").strftime("%b %Y").tolist()

# Page Content
st.markdown(style, unsafe_allow_html=True)
st.header("Report Generation Tool")
st.divider()
st.write(
    "Information on effectiveness of digital marketing, sales, Marine Mart reviews, and more can be found here. Data is from 2023 to the present, but data updates may be delayed. THIS MAY TAKE SEVERAL (5 - 10) MINUTES TO GENERATE.")

st.subheader("Quick Report Generation")
with st.form(key="quick_report_form"):
    # USER INPUT for quick report generation - report year
    report_time_range = st.select_slider(
        "Choose a time range:",
        options=date_range,
        value=(date_range[0], date_range[-1])
    )
    st.caption(
        "Select a start and end month, inclusive on both ends. (e.g. \"Aug 2024 - Aug 2024\" = Report for August 2024, \"Aug 2024 - Sep 2024\" = Report for both August and September 2024)")
    report_type = "report"

    if st.session_state.quick_options_status == "Loading":
        submit_button = st.form_submit_button(label="Generate Report", disabled=True)
    else:
        submit_button = st.form_submit_button(label="Generate Report",
                                              on_click=lambda: quick_options_status_update("Loading"))

if st.session_state.quick_options_status == "Loading":
    generate_report()
    quick_options_status_update("Success")
    st.rerun()
elif st.session_state.quick_options_status == "Success":
    st.balloons()
    st.toast(f"Generating a {report_type} from {report_time_range[0]} to {report_time_range[1]}", icon="✅")
    if report_time_range[0] == report_time_range[1]:
        filename = f"{report_time_range[0]} MCCS Marketing Analytics Assessment"
    else:
        filename = f"{report_time_range[0]} - {report_time_range[1]} MCCS Marketing Analytics Assessment"
    st.download_button(
        label="Get Report as PDF",
        data=st.session_state.generated_pdf,
        file_name=filename + ".pdf",
        mime="application/pdf"
    )
    st.download_button(
        label="Get Report as Word Document",
        data=st.session_state.generated_doc,
        file_name=filename + ".docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    quick_options_status_update("Not Active")
elif st.session_state.quick_options_status == "Failure":
    st.toast("Report failed to generate", icon="❌")
    quick_options_status_update("Not Active")
elif st.session_state.quick_options_status == "Not Active":
    if st.session_state.generated_pdf != "" and st.session_state.generated_doc != "":
        if report_time_range[0] == report_time_range[1]:
            filename = f"{report_time_range[0]} MCCS Marketing Analytics Assessment"
        else:
            filename = f"{report_time_range[0]} - {report_time_range[1]} MCCS Marketing Analytics Assessment"
        st.download_button(
            label="Get Report as PDF",
            data=st.session_state.generated_pdf,
            file_name=filename + ".pdf",
            mime="application/pdf"
        )
        st.download_button(
            label="Get Report as Word Document",
            data=st.session_state.generated_doc,
            file_name=filename + ".docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

st.subheader("Report Generation by Prompt")
# USER INPUT for prompt for AI report generation
st.write(
    "Generate a report using your own prompt using our AI tool. The AI is not perfect and may misunderstand certain prompts. Always check the result manually before referring to it. Click here for more information on guidelines.")

with st.form(key="ai_report_form"):
    # report_query = st.text_input("Query", key="report_query", on_change=enable_button)
    # submit_button = st.form_submit_button(label="Generate Report", disabled=st.session_state.button_disabled)
    st.session_state.query = st.text_input("Query", key="report_query")

    if st.session_state.query_status == "Loading":
        submit_button = st.form_submit_button(label="Generate Report", disabled=True)
    else:
        submit_button = st.form_submit_button(label="Generate Report", on_click=lambda: query_status_update("Loading"))

if st.session_state.query_status == "Loading":
    generate_report_with_prompt(st.session_state.query)
    query_status_update("Success")
    st.rerun()
elif st.session_state.query_status == "Success":
    st.balloons()
    st.toast(f"Generating a report using the prompt {st.session_state.query}", icon="✅")
    filename = f"MCCS Marketing Analytics Assessment"
    st.download_button(
        label="Get Report as PDF",
        data=st.session_state.generated_pdf,
        file_name=filename + ".pdf",
        mime="application/pdf"
    )
    query_status_update("Not Active")
elif st.session_state.quick_options_status == "Failure":
    st.toast("Report failed to generate", icon="❌")
    query_status_update("Not Active")





