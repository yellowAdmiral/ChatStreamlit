import streamlit as st
import requests
import spacy
from sentence_transformers import SentenceTransformer, util



# Custom irrelevant terms to ignore
irrelevant_keywords = set([
    'experience', 'work', 'skills', 'role', 'team', 'great', 'good', 'ability',
    'strong', 'want', 'you', 'your', 'their', 'we', 'us', 'our', 'can', 'will',
    'new', 'build', 'across', 'help', 'enable', 'about', 'get', 'give', 'need',
    'have', 'has', 'make', 'take', 'who', 'what', 'where', 'when', 'how',
    'improve', 'develop', 'create', 'workplace', 'benefit', 'company', 'teams',
    'employees', 'opportunity', 'opportunities', 'fit', 'like'
])

def extract_relevant_keywords(text: str) -> set:
    doc = nlp(text)
    keywords = set()
    for token in doc:
        if token.pos_ in {"NOUN", "PROPN"} and not token.is_stop:
            word = token.text.lower()
            if len(word) > 2 and word not in irrelevant_keywords:
                keywords.add(word)
    return keywords

    
# Load models
@st.cache_resource
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.error("SpaCy model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm'")
        return None

@st.cache_resource
def load_sentence_transformer_model():
    try:
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        st.error(f"Error loading SentenceTransformer model: {e}")
        return None

nlp = load_spacy_model()
model = load_sentence_transformer_model()

# Helper functions
def get_similarity_score(resume: str, jd: str) -> tuple[float, list, list]:
    API_URL = "https://pranup-cv_scorer_api_v1.hf.space/analyze"
    headers = {"Content-Type": "application/json"}
    payload = {
        "cv": resume,
        "job_description": jd
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        
        fit_score = result.get("fit_score")
        keyword_comparison = result.get("keyword_comparison", {})
        matched_keywords = keyword_comparison.get("matched_keywords", [])
        missing_keywords = keyword_comparison.get("missing_keywords", [])

        if fit_score is not None:
            return round(fit_score, 2), matched_keywords, missing_keywords
        else:
            st.error("API response did not contain 'fit_score'.")
            return 0.0, [], []
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling API: {e}")
        return 0.0, [], []

def get_similarity_score_locally(resume: str, jd: str) -> tuple[float, list, list]:
    if nlp is None or model is None:
        st.error("Local models not loaded. Cannot perform local similarity scoring.")
        return 0.0, [], []
    #Similarity Score
    embeddings = model.encode([resume, jd])
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    resume_kw = extract_relevant_keywords(resume)
    #Keyword Matching
    jd_kw = extract_relevant_keywords(jd)
    matched = sorted(resume_kw & jd_kw)
    missing = sorted(jd_kw - resume_kw)
    return round(score, 2), matched, missing
