import streamlit as st
import os
from ui import api_key_input, download_button, chat_buttons, upload_master_cv, show_details_toggle, switch_mode
from data_handling import save_chat_history, load_chat_history, read_file
from llm_interaction import get_ollama_response
from utils import generate_chat_title
import web_parser # Import web_parser

# Configure the page
st.set_page_config(
    page_title="Chat with Ollama",
    page_icon="🤖",
    layout="centered"
)

# Title and description
st.title("💬 CV Tailoring Assistant")
st.markdown("""
Paste the Job descripion or Linkedin link (starting with https://...) and send it to tailor your current CV.
""")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#Initialize Master CV
if "file_uploaded" not in st.session_state:
    st.session_state["file_uploaded"] = False

if "job_description" not in st.session_state:
    st.session_state["job_description"] = None
master_cv_list = [f for f in os.listdir("MasterCV") if (f.endswith(".pdf") or f.endswith(".docx"))]

upload_message = st.sidebar.empty()
# if switch_mode():
#     st.write("Mode Switched")
if len(master_cv_list)>0:
    print(master_cv_list)
    master_cv = read_file("masterCV/"+master_cv_list[0])
    upload_message.markdown("MasterCV registered")
else:
    upload_message.markdown("""
Please Upload a Master CV beore starting.
""")

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
    st.session_state["uploader_visible"] = False
def show_upload(state:bool):
    st.session_state["uploader_visible"] = state
    

# Chat input and buttons
cols = st.columns([0.8, 0.2]) # Adjust column ratios as needed

with cols[0]:
    prompt = st.chat_input("What's on your mind?")

with cols[1]:
    generate_cover_letter_button = st.button("Generate Cover Letter")

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
        st.session_state["job_description"] =  job_info['job_description']# TODO: Implement web_parser to get job description
        st.session_state.messages.append({"role": "user", "content": f"After scraping the link we got:\n{st.session_state['job_description']}"})
        with st.chat_message("user"):
            st.markdown(f"After scraping the link we got:\n{st.session_state['job_description']}")
        # st.write("Job description extracted from URL (TODO: Implement web_parser fully)")
    else:
        st.session_state["job_description"] = prompt

    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_ollama_response(st.session_state["job_description"], model, api_provider, api_key, "CV")
            if response and response.strip():
                st.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.error("Failed to get response from Ollama. Please make sure Ollama is running.")

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
                response = get_ollama_response(st.session_state["job_description"], model, api_provider, api_key, "CL")
                if response and response.strip():
                    st.markdown(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Failed to get response from Ollama. Please make sure Ollama is running.")

    # st.write("Generate Cover Letter button clicked!") # Placeholder

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
        save_dir = "masterCV"
        import os
        save_path = os.path.join(save_dir, uploaded_file.name)

        # Save the uploaded file
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success(f"File saved to {save_path}")
        master_cv_list = [f for f in os.listdir("MasterCV") if (f.endswith(".pdf") or f.endswith(".docx"))]
        st.session_state["file_uploaded"] = True
        if st.session_state["file_uploaded"]:
            # print("here")
            st.rerun()
            # st.session_state["file_uploaded"] = False
            st.session_state["uploader_visible"] = False
