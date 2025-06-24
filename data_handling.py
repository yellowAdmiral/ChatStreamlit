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
try:
    master_cv_list = [f for f in os.listdir("MasterCV") if (f.endswith(".pdf") or f.endswith(".docx"))]
except:
    master_cv_list = []

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

def create_docx(text):
    # Create a new document
    document = Document()
    text = text.replace("```", "").replace("markdown","")
    document.add_paragraph(text)
    filename = st.session_state['user_name'] + "_" + st.session_state['company_name']
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
