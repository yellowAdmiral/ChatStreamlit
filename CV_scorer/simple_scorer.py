import streamlit as st
from sentence_transformers import SentenceTransformer, util
import spacy


# Load models once
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def load_nlp():
    return spacy.load("en_core_web_sm")

model = load_model()
nlp = load_nlp()

# Custom irrelevant terms to ignore
irrelevant_keywords = set([
    'experience', 'work', 'skills', 'role', 'team', 'great', 'good', 'ability',
    'strong', 'want', 'you', 'your', 'their', 'we', 'us', 'our', 'can', 'will',
    'new', 'build', 'across', 'help', 'enable', 'about', 'get', 'give', 'need',
    'have', 'has', 'make', 'take', 'who', 'what', 'where', 'when', 'how',
    'improve', 'develop', 'create', 'workplace', 'benefit', 'company', 'teams',
    'employees', 'opportunity', 'opportunities', 'fit', 'like'
])

# Helper functions
def get_similarity_score(resume: str, jd: str) -> float:
    embeddings = model.encode([resume, jd])
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    return round(score, 2)

def extract_relevant_keywords(text: str) -> set:
    doc = nlp(text)
    keywords = set()
    for token in doc:
        if token.pos_ in {"NOUN", "PROPN"} and not token.is_stop:
            word = token.text.lower()
            if len(word) > 2 and word not in irrelevant_keywords:
                keywords.add(word)
    return keywords

def get_keyword_overlap(resume_text: str, jd_text: str):
    resume_kw = extract_relevant_keywords(resume_text)
    jd_kw = extract_relevant_keywords(jd_text)
    matched = sorted(resume_kw & jd_kw)
    missing = sorted(jd_kw - resume_kw)
    return matched, missing
