import streamlit as st

def load_api_key(api_provider, filename="api_keys.json"):
    import json
    try:
        with open(filename, 'r') as f:
            api_keys = json.load(f)
        return api_keys.get(api_provider)
    except FileNotFoundError:
        return None
        
def api_key_input(api_provider):
    # API Key input

    if api_provider != "Ollama":
        api_key = st.sidebar.text_input("Enter API Key", type="password", value=load_api_key(api_provider))
    else:
        api_key = None
    return api_key

def download_button(messages):
    # Download button
    if st.sidebar.button("Download Updated CV") and len(messages) > 0:
        from data_handling import create_docx
        docx_file = create_docx(messages[-1]["content"])
        with open(docx_file, "rb") as f:
            st.sidebar.download_button(
                label="Confirm",
                data=f,
                file_name= docx_file,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    if st.sidebar.button("Download Cover Letter") and len(messages) > 0:
        from data_handling import create_docx
        docx_file = create_docx(messages[-1]["content"])
        with open(docx_file, "rb") as f:
            st.sidebar.download_button(
                label="Confirm",
                data=f,
                file_name="Cover Letter",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

def chat_buttons():
    # Add save and load chat buttons in the sidebar
    col1, col2, col3 = st.sidebar.columns(3)

    button1 = col1.button('Save Chat')
    button2 = col2.button('Load Chat')
    button3 = col3.button('Clear Chat')
    return button1, button2, button3


def upload_master_cv():
    uploaded_file = st.sidebar.file_uploader("Upload your CV (PDF or DOCX)", type=["pdf", "docx"])
    return uploaded_file

def show_details_toggle():
    """Adds a toggle button to the sidebar to show/hide AI and API provider details."""
    return st.sidebar.toggle("Show AI and API Provider Details", value=False)

def switch_mode():
    return st.sidebar.button("Switch Mode")
