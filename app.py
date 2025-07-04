import streamlit as st
import os
# Configure the page
st.set_page_config(
    page_title="Get CV assistance",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

from ui import api_key_input, download_button, chat_buttons, upload_master_cv, show_details_toggle, switch_mode
from data_handling import save_chat_history, load_chat_history, read_file
from llm_interaction import get_model_response
from utils import generate_chat_title
from CV_scorer.simple_scorer import get_similarity_score, get_similarity_score_locally
from init_state_vars import init_state
import web_parser # Import web_parser

# Download the spaCy model if it's not already present

regenerate_cv_button = None
check_fit_score_button = None
#Create Master CV directory
if not os.path.exists("MasterCV"):
    os.mkdir("MasterCV")
# Title and description
st.title("💬 CV Tailoring Assistant")
st.markdown("""
Paste the Job descripion or Linkedin link (starting with https://...) and send it to tailor your current CV.
""")

# Initialize session state for chat history
init_state()

upload_message = st.sidebar.empty()

# Show/hide AI and API provider details based on toggle
show_details = show_details_toggle()



api_provider = "Gemini"
model = 'gemini-2.5-flash-preview-05-20'
api_key = None



if show_details:
    # UI setup
    api_provider = st.sidebar.selectbox(
        "Select API Provider",
        [ "Gemini", "Ollama", "OpenAI","Claude"],
        index=0
    )

    # Model selection
    if api_provider == "Ollama":
        model = st.sidebar.selectbox(
            "Select Model",
            ["llama3.2:1b", "deepseek-r1:1.5b"],
            index=0
        )
    elif api_provider == "Gemini":
        model = st.sidebar.selectbox(
            "Select Model",
            ['gemini-2.5-flash-preview-05-20','gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-1.5-flash'],
            index=0
        )
    else:
        model = None
    api_key = api_key_input(api_provider)

# else:
#     api_provider = "Ollama" # Default to Ollama if details are hidden
#     model = "llama3.2:1b" # Default model for Ollama
#     api_key = None # No API key needed for Ollama

download_button(st.session_state.messages)
button1, button2, button3 = chat_buttons()

# Get chat history files
chat_files = [f for f in os.listdir("chat history") if f.endswith(".json")]
chat_titles = [f[:-5] for f in chat_files]

# Chat selection
selected_chat = st.sidebar.selectbox(
    "Select Chat",
    chat_titles,
    index=0
)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if "uploader_visible" not in st.session_state:
    st.session_state["uploader_visible"] = True
def show_upload(state:bool):
    st.session_state["uploader_visible"] = state
    

# Chat input and buttons
if st.session_state["job_description"] is None:
    cols = st.columns([0.8, 0.2]) # Adjust column ratios as needed

    with cols[0]:
        prompt = st.chat_input("Enter the Job description or link")

    with cols[1]:
        generate_cover_letter_button = st.button("Generate Cover Letter")
else:
    cols = st.columns([0.6, 0.2, 0.2]) # Adjust column ratios as needed
    with cols[0]:
        generate_cover_letter_button = st.button("Generate Cover Letter")
    with cols[1]:
        regenerate_cv_button = st.button("Regenerate CV")
    with cols[2]:
        check_fit_score_button = st.button("Check Fit Score")
    prompt = None # Set prompt to None when input is hidden

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state["job_description"] = prompt
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if the prompt is a URL
    if prompt.startswith('http://') or prompt.startswith('https://'):
        job_info = web_parser.parse_job_description(prompt)
        if job_info is not None:
            st.session_state["job_description"] =  job_info['job_description']
            st.session_state["company_name"] = job_info['company']
            st.session_state.messages.append({"role": "user", "content": f"After scraping the link we got:\n{st.session_state['job_description']}"})
            with st.chat_message("user"):
                st.markdown(f"After scraping the link we got: \n\n Job Posted by: {st.session_state['company_name']} \n\n Job Description: {st.session_state['job_description']}")
            # st.write("Job description extracted from URL (TODO: Implement web_parser fully)")
        else:
            st.warning("The link could not be scraped. Some websites block scrapers so you may try manually copying the job description.")
            st.session_state["job_description"] = None
    else:   
        st.session_state["job_description"] = prompt

    # Get and display assistant response
    if st.session_state["job_description"] is not None:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_model_response(st.session_state["job_description"], model, api_provider, api_key, "CV")
                if response:
                    st.markdown(response)
                    st.session_state["modified_cv"] = response
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Failed to get response from Ollama. Please make sure Ollama is running.")
    st.rerun()

if generate_cover_letter_button:
    # TODO: Implement cover letter generation logic here
    if not st.session_state["job_description"]:
        st.write("Please send a job description first")
    else:    
        st.session_state.messages.append({"role": "user", "content": "Generate Cover Letter"})
        with st.chat_message("user"):
            st.markdown("Generate Cover Letter")
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_model_response(st.session_state["job_description"], model, api_provider, api_key, "CL")
                if response and response.strip():
                    st.markdown(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Failed to get response from Ollama. Please make sure Ollama is running.")
    st.rerun()

if regenerate_cv_button:
    # TODO: Implement regenerate CV logic here
    if not st.session_state["job_description"]:
        st.write("Please send a job description first")
    else:
        st.session_state.messages.append({"role": "user", "content": "Regenerate CV"})
        with st.chat_message("user"):
            st.markdown("Regenerate CV")
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Assuming regenerate CV uses the same logic as initial CV generation
                response = get_model_response(st.session_state["job_description"], model, api_provider, api_key, "CV")
                if response:
                    st.markdown(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Failed to get response from Model.")
    st.rerun()

if check_fit_score_button:
    if not st.session_state["job_description"] or not st.session_state.messages:
        st.write("Please generate a CV first.")
    else:
        # Assuming the last assistant message is the generated CV
        generated_cv_content = st.session_state.messages[-1]["content"]
        
        fit_score, matched_keywords, missing_keywords = get_similarity_score_locally(generated_cv_content, st.session_state["job_description"])
        st.markdown(f"## ✅ Fit Score: `{fit_score * 100:.1f}%`")
        st.progress(fit_score)
        

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔑 Matching Keywords")
            if matched_keywords:
                st.success(", ".join(matched_keywords))
            else:
                st.warning("No overlapping keywords found.")

        with col2:
            st.markdown("### ❌ Missing Keywords (Consider adding)")
            if missing_keywords:
                st.info(", ".join(missing_keywords))
            else:
                st.success("Great! All important keywords are covered.")



if button1:
    save_chat_history(st.session_state.messages, model)
if button2:
    st.session_state.messages = load_chat_history(f"{selected_chat}.json")

# Add a clear chat button in the sidebar
if button3:
    st.session_state.messages = []
    st.session_state["job_description"] = None
    st.rerun()

st.sidebar.button("Clear Master CV", on_click=show_upload, args=[True])

# cols= st.sidebar.columns((2,1,1))
# cols[0].write("Clear Master CV?")
# cols[1].button("yes", use_container_width=True, on_click=show_upload, args=[True])

if st.session_state["uploader_visible"] and not st.session_state["file_uploaded"]:
    # with st.chat_message("system"):
    uploaded_file = upload_master_cv()

    if uploaded_file is not None:
        # Define the full path where the file will be saved
        save_dir = "MasterCV"
        import os
        save_path = os.path.join(save_dir, uploaded_file.name)

        # Save the uploaded file
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success(f"File saved to {save_path}")
        master_cv_list = [f for f in os.listdir("MasterCV") if (f.endswith(".pdf") or f.endswith(".docx"))]
        st.sidebar.success(f"File saved to {save_path}")
        st.session_state["master_cv_content"] = read_file(save_path)
        st.session_state["file_uploaded"] = True
        st.session_state["uploader_visible"] = False
        st.rerun()
st.caption("Powered by Sentence-BERT, spaCy, and Streamlit")
