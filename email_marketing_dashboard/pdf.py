import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from data_loader import load_data
from data_loader import load_data, get_email_funnel_data, get_performance_vs_previous

def create_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont('Helvetica-bold', 16)
    c.drawString(50, height - 50, "September 2024 MCCS Marketing Analytics Assessment")
