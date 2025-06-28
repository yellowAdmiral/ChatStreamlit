import streamlit as st
import requests

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
