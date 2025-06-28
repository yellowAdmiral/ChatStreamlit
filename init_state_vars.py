import streamlit as st

def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "file_uploaded" not in st.session_state:
        st.session_state["file_uploaded"] = False

    if "job_description" not in st.session_state:
        st.session_state["job_description"] = None

    if "company_name" not in st.session_state:
        st.session_state["company_name"] = ""

    if "user_name" not in st.session_state:
        st.session_state["user_name"] = None

    if "master_cv_content" not in st.session_state:
        st.session_state["master_cv_content"] = None

    if "modified_cv" not in st.session_state:
        st.session_state["modified_cv"] = None

    if "updated_CV_obj" not in st.session_state:
        st.session_state["updated_CV_obj"]= None