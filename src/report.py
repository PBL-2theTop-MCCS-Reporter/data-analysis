import streamlit as st
from nltk import align
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfgen import canvas
from io import BytesIO
from ContentBlock import ContentBlock, Alignment
import base64
import sys
import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#
# from email_marketing_dashboard.data_loader import load_data, get_email_funnel_data, get_performance_vs_previous

# Refer to ContentBlock.py for list of useful functions. Use a list within the report_content to activate a bullet list
report_content = [
    ContentBlock("September 2024 MCCS Marketing Analytics Assessment",
                 bold=True,
                 font_size=15,
                 color="#24446C",
                 alignment=Alignment.CENTER,
                 new_paragraph=True),
    ContentBlock("Purpose:",
                 bold=True,
                 underline=True),
    ContentBlock(" To support leaders and subject matter experts in their decision-making process while aiming to generate smart revenue, increase brand affinity, and reduce stress on Marines and their families.",
                 new_paragraph=True),
    ContentBlock("Findings - Review of digital performance, advertising campaigns, and sales:",
                 bold=True,
                 new_line=True),
    [
         ContentBlock("The industry standard open rate (OPR) for emails in retail is 15-25% - MCX average for September was "),
         ContentBlock("38.08%", bold=True, color="#000071"),
         ContentBlock(" (32.61% in August, 30.10% in July)", new_line=True),

         ContentBlock("The industry standard click through rate (CTR) is 1-5% - MCX average for September was "),
         ContentBlock("0.65%", bold=True, color="#000071"),
         ContentBlock(" (0.45% in August, 0.53% in July)", new_line=True),

         ContentBlock("Performance by email blast (highlights):", new_line=True),

         ContentBlock("09-13 - \"For a limited time only - our 72 Hour Anniversary deals start today!\" 39.60% OPR 1.24% CTR", indent=True, new_line=True),

         ContentBlock("Quantico Firearms - \"Attention NOVA MCX Customers!\" 44.60% OPR 0.52% CTR", indent=True, new_line=True),

         ContentBlock("Labor Day (3 Emails w/ Coupons)", bold=True, color="#000071"),
         ContentBlock(" (28-Aug - 02-Sept TY; 23-Aug - 5-Sept LY):", new_line=True),

         ContentBlock("Average OPR: 34.0% I Average CTR: 0.56% I Coupon Scans - Email: 172, Mobile: 383, In-Store Print: 4,230", indent=True, new_line=True),

         ContentBlock("Total Sales: $12.6M TY; $11.8M LY I Average Daily Sales 2024: $64K; Average Daily Sales 2023: $60K", indent=True, new_line=True),

         ContentBlock("2024 Promotion through email with coupons, 2022 and 2023 promotion through print and coupons", indent=True, new_line=True),

         ContentBlock("Anniversary", bold=True, color="#000071"),
         ContentBlock(" (4-Sept -17-Sept TY; 6-Sept -19-Sept LY):", new_line=True),

         ContentBlock("Advertised Sales: $3.30M TY (22.28% of Participating MS); $3.27M LY (24.40% of Participating MS)", indent=True, new_line=True),

         ContentBlock("EMAG page views: 79,455 I Main Exchange Total Sales: $15.7M TY/ 15.4M LY; Trans: 273K TY/ 272K LY", indent=True, new_line=True),

         ContentBlock("Glamorama", bold=True, color="#000071"),
         ContentBlock(" (4-Sept - 17-Sept TY; 6-Sept- 19-Sept LY):", new_line=True),

         ContentBlock("Advertised Sales: $405K TY (3.20% of Participating MS TY), $422K (3.19% of Participating MS LY)", indent=True, new_line=True),

         ContentBlock("EMAG page views: 43,282 I Main Exchange Total Sales: $15.7M TY/ 15.4M LY; Trans: 273K TY/ 272K LY", indent=True, new_line=True),

         ContentBlock("Fall Sight & Sound", bold=True, color="#000071"),
         ContentBlock(" (18-Sept - 1-Oct TY; 20-Sept- 3-Oct LY):", new_line=True),

         ContentBlock("Advertised Sales: $466K TY (4.22% of Participating MS TY), $591K (5.08% of Participating MS LY)", indent=True, new_line=True),

         ContentBlock("EMAG page views: 19,342 I Main Exchange Total Sales: $13.3M TY/ 13.9M LY; Trans: 246K TY/ 262K LY", indent=True, new_line=True),

         ContentBlock("Sept Designer/Fall Trend", bold=True, color="#000071"),
         ContentBlock(" (18-Sept - 1-Oct TY; 20-Sept- 3-Oct LY):", new_line=True),

         ContentBlock("Advertised Sales: $405K TY (4.22% of Participating MS TY), $961K (5.08% of Participating MS LY)", indent=True, new_line=True),

         ContentBlock("EMAG page views: 13,435 I Main Exchange Total Sales: $13.3M TY/ 13.9M LY; Trans: 246K TY/ 262K LY", indent=True, new_line=True),

         ContentBlock("Other Initiatives", bold=True, color="#000071"),
         ContentBlock(": Baby & Me: 19 coupons used I Hallmark: 14 coupons used I Case Wine 10%: 35 coupons used", new_paragraph=True),
    ],
    ContentBlock("Findings - Review of Main Exchanges, Marine Marts, and MCHS CSAT Surveys and Google Reviews:",
                 bold=True,
                 new_line=True),
    [
        ContentBlock("92% of 382 Main Exchange survey respondents reported overall satisfaction with their experience.", color="#000071", bold=True, new_line=True),
        ContentBlock("15.7% said they were shopping sales that were advertised, indicating MCX advertisements are successfully driving footsteps in the door. 45.5% were picking up needed supplies.", indent=True, new_line=True),
        ContentBlock("96% of 520 Marine Mart survey respondents reported overall satisfaction with their experience.", color="#000071", bold=True, new_line=True),
        ContentBlock("42 customers were unable to purchase everything they intended. 50% of these customers said it was because MCX did not carry the item they were looking for. (See Enclosure 2 for sought after items comments)", indent=True, new_line=True),
        ContentBlock("There were 392 MCHS survey respondents, with an average CSAT score of 91.8.", color="#000071", bold=True, new_line=True),
        ContentBlock("In September 2023, there were 603 survey respondents with an average CSAT score of 88.1", indent=True, new_line=True),
        ContentBlock("40.8% of respondents were T AD/TDY. 32.1% of respondents were traveling for leisure.", indent=True, new_line=True),
        ContentBlock("Respondents traveling for leisure averaged a CSAT score of 90.1. Respondents T AD/TDY averaged 87.6.", indent=True, new_line=True),
        ContentBlock("All time ", indent=True),
        ContentBlock("Google Reviews", bold=True, color="#000071"),
        ContentBlock(" have an average rating of 4.4 out of 5 and there has been a total of 10,637 reviews.", new_paragraph=True),
    ],
    ContentBlock("Assessments",
                 bold=True,
                 new_paragraph=True),
]

def content_block_to_formatted_text(block):
    tagged = block.text
    if block.bold:
        tagged = f"<b>{tagged}</b>"
    if block.underline:
        tagged = f"<u>{tagged}</u>"
    if block.font_size != 10:
        tagged = f"<font size={block.font_size}>{tagged}</font>"
    if block.color:
        tagged = f"<font color='{block.color}'>{tagged}</font>"
    return tagged

def make_bullet_list(styles, bullet_points, format):
    bullet_list = []
    tagged = ""
    indent_block = False
    for bullet in bullet_points:
        if format == "pdf":
            tagged = tagged + content_block_to_formatted_text(bullet)
            if bullet.indent:
                indent_block = True
            if bullet.new_paragraph:
                paragraph = Paragraph(tagged, styles["Normal"])
                if indent_block:
                    bullet_list.append(ListItem(paragraph, bulletColor='black', leftIndent = 36))
                else:
                    bullet_list.append(ListItem(paragraph, bulletColor='black'))
                bullet_list.append(Spacer(1, 6))
                tagged = ""
                indent_block = False
            elif bullet.new_line:
                paragraph = Paragraph(tagged, styles["Normal"])
                if indent_block:
                    bullet_list.append(ListItem(paragraph, bulletColor='black', leftIndent = 36))
                else:
                    bullet_list.append(ListItem(paragraph, bulletColor='black'))
                tagged = ""
                indent_block = False
        else:
            bullet_list.append(f"{bullet}")

    if format == "pdf":
        return ListFlowable(
            bullet_list,
            bulletType="bullet",
            bulletFontName="Montserrat-Medium",
            bulletFontSize=10,
            spaceBefore=12
        )
    return bullet_list

def create_pdf():
    # Register fonts and font family
    pdfmetrics.registerFont(TTFont("Montserrat-Light", "./fonts/Montserrat/static/Montserrat-Light.ttf"))
    pdfmetrics.registerFont(TTFont("Montserrat-Medium", "./fonts/Montserrat/static/Montserrat-Medium.ttf"))

    registerFontFamily("Montserrat", normal="Montserrat-Light", bold="Montserrat-Medium")

    # Create and set up doc
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,  # 0.5 inch on all sides
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    # Styles and fonts
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = "Montserrat-Light"
    center_style = ParagraphStyle(
        "Title",
        fontName="Montserrat-Medium",
        leading=12,
        spaceAfter=10,
        alignment=1
    )
    indent_style = ParagraphStyle(
        "Indent",
        leftIndent=36,
    )

    # Process through report_content list and inject reportlab paragraphs into content_list
    content_list = []
    tagged = ""
    indent_block = False
    for block in report_content:
        if isinstance(block, ContentBlock):
            tagged = tagged + content_block_to_formatted_text(block)
            if block.indent:
                indent_block = True
            if block.alignment == Alignment.CENTER:
                paragraph = Paragraph(tagged, center_style)
                content_list.append(paragraph)
                content_list.append(Spacer(1, 12))
                tagged = ""
                indent_block = False
            elif block.new_line:
                style = indent_style if indent_block else styles["Normal"]
                paragraph = Paragraph(tagged, style)
                content_list.append(paragraph)
                tagged = ""
                indent_block = False
            elif block.new_paragraph:
                style = indent_style if indent_block else styles["Normal"]
                paragraph = Paragraph(tagged, style)
                content_list.append(paragraph)
                content_list.append(Spacer(1, 6))
                tagged = ""
                indent_block = False
        elif isinstance(block, list):
            bullet_list = make_bullet_list(styles, block, "pdf")
            content_list.append(bullet_list)

    # Use content list to build a doc
    doc.build(content_list)

    # Set seeker to the beginning of the doc and return the buffer
    buffer.seek(0)
    return buffer

def create_doc():
    document = Document()

    # Register fonts
    # pdfmetrics.registerFont(TTFont("Montserrat-Light", "./fonts/Montserrat/static/Montserrat-Light.ttf"))
    # pdfmetrics.registerFont(TTFont("Montserrat-Medium", "./fonts/Montserrat/static/Montserrat-Medium.ttf"))
    #
    # registerFontFamily("Montserrat", normal="Montserrat-Light", bold="Montserrat-Medium")

    # Set margins
    section = document.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    # Title
    title_para = document.add_paragraph()
    title_run = title_para.add_run(title_text)
    title_run.bold = True
    title_run.font.size = Pt(15)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Purpose
    purpose_para = document.add_paragraph()
    purpose_run = purpose_para.add_run("Purpose: ")
    purpose_run.bold = True
    purpose_run.underline = True
    purpose_para.add_run(
        "To support leaders and subject matter experts in their decision-making process while aiming to generate smart revenue, increase brand affinity, and reduce stress on Marines and their families.")

    # Findings - Digital
    document.add_paragraph("Findings - Review of digital performance, advertising campaigns, and sales:",
                           style="Heading 2")
    for item in make_bullet_list(None, digital_findings_bullet_points, "word"):
        document.add_paragraph(item, style="List Bullet")

    # Findings - Main Exchanges
    document.add_paragraph(
        "Findings - Review of Main Exchanges, Marine Marts, and MCHS CSA T Surveys and Google Reviews:",
        style="Heading 2")
    for item in make_bullet_list(None, main_exchanges_findings_bullet_points, "word"):
        document.add_paragraph(item, style="List Bullet")

    # Assessments
    document.add_paragraph("Assessments", style="Heading 2")

    # Build document
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer