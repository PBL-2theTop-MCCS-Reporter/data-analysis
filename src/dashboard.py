import streamlit as st
import pandas as pd
import time
import base64
from report import create_pdf, create_doc


def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


header_img = get_img_as_base64("images/MCCS-header.png")

style = f"""
<style>
[data-testid="stHeader"] {{
    background-image: url("data:image/png;base64,{header_img}");
    background-size: cover;
}}

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


# functions
def quick_options_status_update(new_state):
    st.session_state.quick_options_status = new_state
    st.session_state.query_status = "Not Active"


def query_status_update(new_state):
    st.session_state.query_status = new_state
    st.session_state.quick_options_status = "Not Active"


def generate_report():
    pdf_buffer = create_pdf()
    st.session_state.generated_pdf = pdf_buffer
    doc_buffer = create_doc()
    st.session_state.generated_doc = doc_buffer


current_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime("%Y-%m")
date_range = pd.date_range(start="2024-08", end="2024-09", freq="MS").strftime("%b %Y").tolist()

# Page Content
st.markdown(style, unsafe_allow_html=True)
st.header("Report Generation Tool")
st.divider()
st.write(
    "Information on effectiveness of digital marketing, sales, Marine Mart reviews, and more can be found here. Data is from 2023 to the present, but data updates may be delayed. ")

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
    # USER INPUT for quick report generation - report type
    # report_type = st.selectbox(
    #     "Choose report:",
    #     ["Executive Report", "Social Media Report", "Email Report", "Comment Report"]
    # )
    report_type = "report"

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

st.subheader("Report Generation by Prompt")
# USER INPUT for prompt for AI report generation
st.write(
    "Generate a report using your own prompt using our AI tool. The AI is not perfect and may misunderstand certain prompts. Always check the result manually before referring to it. Click here for more information on guidelines.")

with st.form(key="ai_report_form"):
    # report_query = st.text_input("Query", key="report_query", on_change=enable_button)
    # submit_button = st.form_submit_button(label="Generate Report", disabled=st.session_state.button_disabled)
    report_query = st.text_input("Query", key="report_query")

    if st.session_state.query_status == "Loading":
        submit_button = st.form_submit_button(label="Generate Report", disabled=True)
    else:
        submit_button = st.form_submit_button(label="Generate Report", on_click=lambda: query_status_update("Loading"))

    if st.session_state.query_status == "Loading":
        if report_query.strip():
            with st.spinner(''):
                generate_report()
            query_status_update("Success")
        else:
            query_status_update("Failure")
        st.rerun()
    elif st.session_state.query_status == "Success":
        st.balloons()
        st.toast(f"Generating a report using \"{report_query}\"", icon="✅")
        query_status_update("Not Active")
    elif st.session_state.query_status == "Failure":
        st.toast("Prompt cannot be empty", icon="❌")
        query_status_update("Not Active")





