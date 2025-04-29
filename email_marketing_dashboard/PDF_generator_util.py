import streamlit as st                   # 引入 Streamlit，用于构建 Web 应用
from reportlab.pdfgen import canvas      # 引入 reportlab 的 canvas，用于生成 PDF 文件
from io import BytesIO                   # 引入 BytesIO，用于在内存中临时存储文件（类似文件对象）
import base64                            # 引入 base64，用于将二进制文件转换为 Base64 编码
import textwrap

def generate_pdf(text: str) -> BytesIO:  # 定义生成 PDF 的函数，接收文本参数并返回 PDF 缓冲区
    buffer = BytesIO()
    c = canvas.Canvas(buffer)

    wrapped_lines = []
    for line in text.split('\n'):
        wrapped_lines.extend(textwrap.wrap(line, width=80))  # 每行最多 80 个字符

    y = 750
    for line in wrapped_lines:
        if y < 50:  # 留出底部边距
            c.showPage()  # 创建新页面
            y = 750  # 重置 y 坐标为新页起始高度
        c.drawString(100, y, line)
        y -= 20  # 每行行距为 20 像素

    c.save()
    buffer.seek(0)
    return buffer

def show_pdf(file_buffer: BytesIO):      # 定义预览 PDF 的函数
    # base64_pdf = base64.b64encode(file_buffer.read()).decode('utf-8')  # 将 PDF 内容编码为 base64 字符串
    # pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'  # 构造用于预览的 iframe 标签
    # st.markdown(pdf_display, unsafe_allow_html=True)  # 使用 markdown 渲染 HTML 内容，打开允许 HTML 标志
    base64_pdf = base64.b64encode(file_buffer.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
