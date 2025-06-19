import streamlit as st
import json
from docx import Document
import fitz  # PyMuPDF
import os
from utils import generate_chat_title
import markdown
from docx.shared import Inches
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

master_cv_list = [f for f in os.listdir("MasterCV") if (f.endswith(".pdf") or f.endswith(".docx"))]

save_dir = "masterCV"
os.makedirs(save_dir, exist_ok=True)

def read_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def read_docx(file_path):
    doc = Document(file_path)
    return "\\n".join(para.text for para in doc.paragraphs)

def save_chat_history(history, model):
    title = generate_chat_title(history, model)
    filename = f"chat history/{title}.json"
    chat_data = {
        "title": title,
        "history": history
    }
    with open(filename, 'w') as f:
        json.dump(chat_data, f)

def load_chat_history(filename):
    try:
        with open(filename, 'r') as f:
            chat_data = json.load(f)
        return chat_data["history"]
    except FileNotFoundError:
        return []

def create_docx(text, filename="updated_cv.docx"):
    # Create a new document
    document = Document()
    
    # Add a style for normal paragraphs
    # normal_style = document.styles.add_style('NormalParagraph', WD_STYLE_TYPE.PARAGRAPH)
    # normal_style.paragraph_format.space_after = Pt(6)
    # normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    # Add a style for Markdown headings
    # h1_style = document.styles.add_style('Heading1', WD_STYLE_TYPE.PARAGRAPH)
    # h1_style.paragraph_format.space_before = Pt(12)
    # h1_style.paragraph_format.space_after = Pt(6)
    # h1_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # h1_style.font.bold = True
    # h1_style.font.size = Pt(16)
    
    # h2_style = document.styles.add_style('Heading2', WD_STYLE_TYPE.PARAGRAPH)
    # h2_style.paragraph_format.space_before = Pt(12)
    # h2_style.paragraph_format.space_after = Pt(6)
    # h2_style.font.bold = True
    # h2_style.font.size = Pt(14)
    
    # h3_style = document.styles.add_style('Heading3', WD_STYLE_TYPE.PARAGRAPH)
    # h3_style.paragraph_format.space_before = Pt(12)
    # h3_style.paragraph_format.space_after = Pt(6)
    # h3_style.font.bold = True
    # h3_style.font.size = Pt(12)

    text = text.replace("```", "").replace("markdown","")
    document.add_paragraph(text)
    # # Convert markdown to HTML
    # html = markdown.markdown(text)
    
    # # Parse the HTML and add elements to the document
    # for element in html.split("<p>"):
    #     element = element.strip("</p>")
    #     if not element:
    #         continue

    #     if element.startswith("strong>"):
    #         element = element.strip("</p>").strip("strong>").replace("</strong>", "")
    #         p = document.add_paragraph(element, style='Heading4')
    #     elif element.startswith("<h2>"):
    #         p = document.add_paragraph(element[4:-5], style='Heading2')
    #     elif element.startswith("<h3>"):
    #         p = document.add_paragraph(element[4:-5], style='Heading3')
    #     elif element.startswith("<h4>"):
    #         p = document.add_paragraph(element[4:-5], style='NormalParagraph')
    #     elif element.startswith("<h5>"):
    #         p = document.add_paragraph(element[4:-5], style='NormalParagraph')
    #     elif element.startswith("<h6>"):
    #         p = document.add_paragraph(element[4:-5], style='NormalParagraph')
    #     else:
    #         p = document.add_paragraph(element, style='NormalParagraph')

    # Save the document
    document.save(filename)
    return filename

def read_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".docx":
        return read_docx(file_path)
    elif ext == ".pdf":
        return read_pdf(file_path)
    else:
        raise ValueError("Unsupported file type")
