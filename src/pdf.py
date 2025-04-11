import streamlit as st
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfgen import canvas
from io import BytesIO
import base64
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email_marketing_dashboard.data_loader import load_data, get_email_funnel_data, get_performance_vs_previous

def make_bullet_list(styles, bullet_points):
    list = []
    for bullet in bullet_points:
        if "indent" in bullet:
            bullet = bullet.replace("[indent]", "").strip()
            finding = ListItem(Paragraph(f"{bullet}", styles["Normal"]), bulletColor='black', leftIndent=36)
        else:
            finding = ListItem(Paragraph(f"{bullet}", styles["Normal"]), bulletColor='black')
        list.append(finding)

    return ListFlowable(
        list,
        bulletType="bullet",
        bulletFontName="Montserrat-Medium",
        bulletFontSize=10,
        spaceBefore=12
    )

def create_pdf():
    pdfmetrics.registerFont(TTFont("Montserrat-Light", "src/fonts/Montserrat/static/Montserrat-Light.ttf"))
    pdfmetrics.registerFont(TTFont("Montserrat-Medium", "src/fonts/Montserrat/static/Montserrat-Medium.ttf"))

    registerFontFamily("Montserrat", normal="Montserrat-Light", bold="Montserrat-Medium")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,  # 0.5 inch
        rightMargin=36,  # 0.5 inch
        topMargin=36,  # 0.5 inch
        bottomMargin=36  # 0.5 inch
    )

    # styles and fonts
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        fontName="Montserrat-Medium",  # You can replace with your preferred font
        fontSize=15,
        leading=12,
        textColor=(0.141, 0.267, 0.424),  # Set text color to blue
        spaceAfter=10,
        alignment=1
    )
    styles['Normal'].fontName = "Montserrat-Light"

    # Title
    title = Paragraph("September 2024 MCCS Marketing Analytics Assessment", title_style)

    # Purpose
    purpose_text = Paragraph(
        """<b><u>Purpose:</u></b> To support leaders and subject matter experts in their decision-making process while aiming to generate 
        smart revenue, increase brand affinity, and reduce stress on Marines and their families.""",
        styles['Normal']
    )

    # Findings - Digital
    digital_findings_subheading = Paragraph("<b>Findings - Review of digital performance, advertising campaigns, and sales:</b>", styles['Normal'])

    digital_findings_bullet_points = [
        "The industry standard open rate (OPR) for emails in retail is 15-25% - MCX average for September was <b><font color='#000071'>38.08%</font></b> (32.61% in August, 30.10% in July)",
        "The industry standard click through rate (CTR) is 1-5% - MCX average for September was <b><font color='#000071'>0.65%</font></b> (0.45% in August, 0.53% in July)",
        "Performance by email blast (highlights):",
        "[indent]09-13 - \"For a limited time only - our 72 Hour Anniversary deals start today!\" 39.60% OPR 1.24% CTR",
        "[indent]Quantico Firearms - \"Attention NOVA MCX Customers!\" 44.60% OPR 0.52% CTR",
        "<b><font color='#000071'>Labor Day (3 Emails w/ Coupons)</font></b> (28-Aug - 02-Sept TY; 23-Aug - 5-Sept LY):",
        "[indent]Average OPR: 34.0% I Average CTR: 0.56% I Coupon Scans - Email: 172, Mobile: 383, In-Store Print: 4,230",
        "[indent]Total Sales: $12.6M TY; $11.8M LY I Average Daily Sales 2024: $64K; Average Daily Sales 2023: $60K",
        "[indent]2024 Promotion through email with coupons, 2022 and 2023 promotion through print and coupons",
        "<b><font color='#000071'>Anniversary</font></b> (4-Sept -17-Sept TY; 6-Sept -19-Sept LY):",
        "[indent]Advertised Sales: $3.30M TY (22.28% of Participating MS); $3.27M LY (24.40% of Participating MS)",
        "[indent]EMAG page views: 79,455 I Main Exchange Total Sales: $15.7M TY/ 15.4M LY; Trans: 273K TY/ 272K LY",
        "<b><font color='#000071'>Glamorama</font></b> (4-Sept - 17-Sept TY; 6-Sept- 19-Sept LY):",
        "[indent]Advertised Sales: $405K TY (3.20% of Participating MS TY), $422K (3.19% of Participating MS LY)",
        "[indent]EMAG page views: 43,282 I Main Exchange Total Sales: $15.7M TY/ 15.4M LY; Trans: 273K TY/ 272K LY",
        "<b><font color='#000071'>Fall Sight & Sound</font></b> (18-Sept - 1-Oct TY; 20-Sept- 3-Oct LY):",
        "[indent]Advertised Sales: $466K TY (4.22% of Participating MS TY), $591K (5.08% of Participating MS LY)",
        "[indent]EMAG page views: 19,342 I Main Exchange Total Sales: $13.3M TY/ 13.9M LY; Trans: 246K TY/ 262K LY",
        "<b><font color='#000071'>Sept Designer/Fall Trend</font></b> (18-Sept - 1-Oct TY; 20-Sept- 3-Oct LY):",
        "[indent]Advertised Sales: $405K TY (4.22% of Participating MS TY), $961K (5.08% of Participating MS LY)",
        "[indent]EMAG page views: 13,435 I Main Exchange Total Sales: $13.3M TY/ 13.9M LY; Trans: 246K TY/ 262K LY",
        "<b><font color='#000071'>Other Initiatives</font></b>: Baby & Me: 19 coupons used I Hallmark: 14 coupons used I Case Wine 10%: 35 coupons used",
    ]

    digital_findings_bullet_list = make_bullet_list(styles, digital_findings_bullet_points)

    # Findings - Main Exchanges
    main_exchanges_findings_subheading = Paragraph(
        "<b>Findings - Review of Main Exchanges, Marine Marts, and MCHS CSA T Surveys and Google Reviews:</b>", styles['Normal'])

    main_exchanges_findings_bullet_points = [
        "<b><font color='#000071'>92% of 382 Main Exchange survey respondents reported overall satisfaction with their experience.</font></b>",
        "[indent]15.7% said they were shopping sales that were advertised, indicating MCX advertisements are successfully driving footsteps in the door. 45.5% were picking up needed supplies.",
        "<b><font color='#000071'>96% of 520 Marine Mart survey respondents reported overall satisfaction with their experience.</font></b>",
        "[indent]42 customers were unable to purchase everything they intended. 50% of these customers said it was because MCX did not carry the item they were looking for. (See Enclosure 2 for sought after items comments)",
        "<b><font color='#000071'>There were 392 MCHS survey respondents, with an average CSAT score of 91.8.</font></b>",
        "[indent]In September 2023, there were 603 survey respondents with an average CSAT score of 88.1",
        "[indent]40.8% of respondents were T AD/TDY. 32.1% of respondents were traveling for leisure.",
        "[indent]Respondents traveling for leisure averaged a CSAT score of 90.1. Respondents T AD/TDY averaged 87.6.",
        "All time <b><font color='#000071'>Google Reviews</font></b> have an average rating of 4.4 out of 5 and there has been a total of 10,637 reviews.",
    ]

    main_exchanges_findings_bullet_list = make_bullet_list(styles, main_exchanges_findings_bullet_points)

    # Assessments
    assessments_subheading = Paragraph("<b>Assessment</b>", styles["Normal"])

    # Build document
    doc.build([
        title, Spacer(1, 12), 
        purpose_text, Spacer(1, 6),
        digital_findings_subheading, digital_findings_bullet_list, Spacer(1, 6),
        main_exchanges_findings_subheading, main_exchanges_findings_bullet_list, Spacer(1, 6),
        assessments_subheading
    ])

    buffer.seek(0)
    return buffer

if st.button("Generate PDF"):
    pdf_buffer = create_pdf()

    # Convert to base64
    pdf_base64 = base64.b64encode(pdf_buffer.read()).decode("utf-8")
    pdf_url = f"data:application/pdf;base64,{pdf_base64}"

    # Create the HTML embed
    st.markdown(f'<a href="{pdf_url}" target="_blank">Open PDF in New Tab</a>', unsafe_allow_html=True)

    # Display the PDF
    # st.markdown(pdf_display, unsafe_allow_html=True)