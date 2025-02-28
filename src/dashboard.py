import streamlit as st
import base64

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

</style>
"""

# if "button_disabled" not in st.session_state:
#     st.session_state.button_disabled = True

# if "report_query" not in st.session_state:
#     st.session_state.report_query = ""

# def enable_button():
#     print(st.session_state.report_query)
#     if st.session_state.report_query.strip():
#         st.session_state.button_disabled = False
#     else:
#         st.session_state.button_disabled = True


st.markdown(style, unsafe_allow_html=True)
st.header("Report Generation Tool")
st.divider()

st.subheader("Quick Report Generation")
st.write("Information on effectiveness of digital marketing, sales, Marine Mart reviews, and more can be found here. Data is from 2023 to the present, but data updates may be delayed. ")

with st.form(key="quick_report_form"):
    # USER INPUT for quick report generation - report year
    report_year = st.selectbox(
        "Choose a year:",
        ["2020", "2021", "2022", "2023", "2024"]
    )
    # USER INPUT for quick report generation - report type
    report_type = st.selectbox(
        "Choose report:",
        ["Executive Report", "Social Media Report", "Email Report", "Comment Report"]
    )

    submit_button = st.form_submit_button(label="Generate Report")

    if submit_button:
        st.success(f"Report year selected: {report_year}, Report type selected: {report_type}")
        st.balloons()

st.subheader("Report Generation by Prompt")
# USER INPUT for prompt for AI report generation
st.write("Generate a report using your own prompt using our AI tool. The AI is not perfect and may misunderstand certain prompts. Always check the result manually before referring to it. Click here for more information on guidelines.")

with st.form(key="ai_report_form"):
    # report_query = st.text_input("Query", key="report_query", on_change=enable_button)
    # submit_button = st.form_submit_button(label="Generate Report", disabled=st.session_state.button_disabled)
    report_query = st.text_input("Query", key="report_query")
    submit_button = st.form_submit_button(label="Generate Report")

    if submit_button:
        st.balloons()
        st.success(f"Query entered: {report_query}")



    
        
