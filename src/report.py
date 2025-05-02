import copy
from datetime import datetime

import streamlit as st
from dateutil.relativedelta import relativedelta
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT, WD_BREAK
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfgen import canvas
from io import BytesIO
from ContentBlock import ContentBlock, Alignment
from docx.oxml.ns import qn
import base64
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email_marketing_dashboard.functions import generate_email_report, generate_social_media_report

# from email_marketing_dashboard.data_loader import load_data, get_email_funnel_data, get_performance_vs_previous

# Refer to ContentBlock.py for list of useful functions. Use a list within the report_content to activate a bullet list
# {DateRange} gets replaced with the date range
# {PrevMonth} gets replaced with the month before the beginning month
# {TwoPrevMonth} gets replaced with two months before the beginning month

report_content = [
    ContentBlock("{DateRange} MCCS Marketing Analytics Assessment",
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
         ContentBlock("The industry standard open rate (OPR) for emails in retail is 15-25% - MCX average for {DateRange} was "),
         ContentBlock("38.08%", bold=True, color="#000071"),
         ContentBlock(" (32.61% in {PrevMonth}, 30.10% in {TwoPrevMonth})", new_line=True),

         ContentBlock("The industry standard click through rate (CTR) is 1-5% - MCX average for {DateRange} was "),
         ContentBlock("0.65%", bold=True, color="#000071"),
         ContentBlock(" (0.45% in {PrevMonth}, 0.53% in {TwoPrevMonth})", new_line=True),

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
                 new_line=True),

]

def add_raw_output_to_report_content(raw_assessments, raw_social_media_report):
    # Process assessments and social_media_report raw output
    assessments = raw_assessments.split("\n")
    cleaned_assessments = []
    for assessment in assessments:
        cleaned_assessment = assessment.partition(".")[2].strip()
        if len(cleaned_assessment.strip()) > 0:
            cleaned_assessments.append(cleaned_assessment)

    social_media_findings = raw_social_media_report.split("\n\n")
    cleaned_social_media_findings = []
    for finding in social_media_findings:
        if len(finding.strip()) > 0:
            cleaned_finding = finding.partition(".")[2].strip()
            parts = cleaned_finding.split("\n")
            if len(parts) == 2:
                cleaned_line = parts[0] + " (Evidence: " + parts[1].strip()[len("- Evidence:"):].strip() + ")"
                cleaned_social_media_findings.append(cleaned_line)
            else:
                cleaned_social_media_findings.append(cleaned_finding)

    # Turn it into content blocks
    assessments_content = []
    for i, assessment in enumerate(cleaned_assessments):
        if i == len(cleaned_assessments) - 1:
            content_block = ContentBlock(assessment, new_paragraph=True)
        else:
            content_block = ContentBlock(assessment, new_line=True)
        assessments_content.append(content_block)

    social_media_content = []
    for i, finding in enumerate(cleaned_social_media_findings):
        if i == len(cleaned_social_media_findings) - 1:
            content_block = ContentBlock(finding, new_paragraph=True)
        else:
            content_block = ContentBlock(finding, new_line=True)
        social_media_content.append(content_block)

    # Build the report using the existing template + new Ollama Information
    current_report = copy.deepcopy(report_content)
    current_report.append(assessments_content)
    current_report.append(ContentBlock("{DateRange} MCX Email Highlights",
                                       bold=True,
                                       font_size=15,
                                       color="#24446C",
                                       underline=True,
                                       alignment=Alignment.CENTER,
                                       new_paragraph=True)),
    current_report.append(ContentBlock("{DateRange} MCX Social Media Highlights",
                                       bold=True,
                                       font_size=15,
                                       color="#24446C",
                                       underline=True,
                                       alignment=Alignment.CENTER,
                                       new_paragraph=True)),
    current_report.append(social_media_content),
    current_report.append(ContentBlock("{DateRange} MCX Customer Satisfaction Highlights",
                                       bold=True,
                                       font_size=15,
                                       color="#24446C",
                                       underline=True,
                                       alignment=Alignment.CENTER,
                                       new_paragraph=True)),
    return current_report

def parse_time(begin, end):
    begin_dt = datetime.strptime(begin, "%b %Y")
    end_dt = datetime.strptime(end, "%b %Y")

    # Build replacement strings
    if begin_dt == end_dt:
        date_range = begin_dt.strftime("%B %Y")
    else:
        date_range = f"{begin_dt.strftime('%B')} - {end_dt.strftime('%B %Y')}"

    prev_month = (begin_dt - relativedelta(months=1)).strftime("%B")
    two_prev_month = (begin_dt - relativedelta(months=2)).strftime("%B")
    return date_range, prev_month, two_prev_month

def replace_placeholders(current_report, beginning_month, ending_month):
    # Get month strings for replacement
    date_range, prev_month, two_prev_month = parse_time(beginning_month, ending_month)

    # Replace strings
    for item in current_report:
        if isinstance(item, ContentBlock):
            item.text = item.text.replace("{DateRange}", date_range)
            item.text = item.text.replace("{PrevMonth}", prev_month)
            item.text = item.text.replace("{TwoPrevMonth}", two_prev_month)
        elif isinstance(item, list):
            for block in item:
                if isinstance(block, ContentBlock):
                    block.text = block.text.replace("{DateRange}", date_range)
                    block.text = block.text.replace("{PrevMonth}", prev_month)
                    block.text = block.text.replace("{TwoPrevMonth}", two_prev_month)

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

def pdf_bullet_list(styles, bullet_points):
    bullet_items = []
    tagged = ""
    indent_block = False

    for bullet in bullet_points:
        tagged += content_block_to_formatted_text(bullet)
        if bullet.indent:
            indent_block = True

        if bullet.new_paragraph or bullet.new_line:
            paragraph = Paragraph(tagged, styles["Normal"])
            item = ListItem(paragraph, bulletColor='black',
                            leftIndent=36 if indent_block else 18)
            bullet_items.append(item)
            tagged = ""
            indent_block = False

    return ListFlowable(
        bullet_items,
        bulletType="bullet",
        bulletFontName="Montserrat-Medium",
        bulletFontSize=10,
        spaceBefore=12
    )

def create_pdf(beginning_month, ending_month, assessments, social_media_report):
    # Get current report (combines template + Ollama)
    current_report = add_raw_output_to_report_content(assessments, social_media_report)

    # Replace all placeholders
    replace_placeholders(current_report, beginning_month, ending_month)

    # Register fonts and font family
    pdfmetrics.registerFont(TTFont("Montserrat-Light", "src/fonts/Montserrat/static/Montserrat-Light.ttf"))
    pdfmetrics.registerFont(TTFont("Montserrat-Medium", "src/fonts/Montserrat/static/Montserrat-Medium.ttf"))

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

    # Process through current_report list and inject reportlab paragraphs into content_list
    content_list = []
    tagged = ""
    indent_block = False
    for block in current_report:
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
            bullet_list = pdf_bullet_list(styles, block)
            content_list.append(bullet_list)
            content_list.append(Spacer(1, 12))

    # Use content list to build a doc
    doc.build(content_list)

    # Set seeker to the beginning of the doc and return the buffer
    buffer.seek(0)
    return buffer

def create_doc(beginning_month, ending_month, assessments, social_media_report):
    # Get current report (combines template + Ollama)
    current_report = add_raw_output_to_report_content(assessments, social_media_report)

    # Replace all placeholders
    replace_placeholders(current_report, beginning_month, ending_month)

    # Set up document
    document = Document()

    section = document.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    def render_run(run, block):
        run.text = block.text
        run.bold = block.bold
        run.underline = block.underline
        run.font.size = Pt(block.font_size)
        run.font.color.rgb = block.get_rgb_color()
        run.font.name = "Montserrat"
        r = run._element
        r.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')  # fallback if Montserrat is not available

    def add_paragraph_from_blocks(blocks, style=None, is_bullet=False, is_indent=False):
        para = document.add_paragraph(style=style)
        if is_bullet:
            para.style = 'List Bullet 2' if is_indent else 'List Bullet'

        para.paragraph_format.line_spacing = Pt(12)
        para.paragraph_format.space_after = Pt(2)
        para.paragraph_format.space_before = Pt(0)

        first_block = blocks[0]
        if first_block.alignment == Alignment.CENTER:
            para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        else:
            para.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

        for i, block in enumerate(blocks):
            run = para.add_run()
            render_run(run, block)
            if block.new_line and i < len(blocks) - 1:
                run.add_break(WD_BREAK.LINE)

    current_line = []
    indent_line = False
    for item in current_report:
        if isinstance(item, list):
            bullet_item = []
            for block in item:
                bullet_item.append(block)
                if block.indent:
                    indent_line = True
                if block.new_line or block.new_paragraph:
                    if bullet_item:
                        add_paragraph_from_blocks(bullet_item, is_bullet=True, is_indent=indent_line)
                        bullet_item = []
                        indent_line = False
        else:
            current_line.append(item)
            if item.new_line or item.new_paragraph:
                add_paragraph_from_blocks(current_line)
                current_line = []
    if current_line:
        add_paragraph_from_blocks(current_line)

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer