# Chat with Ollama using Streamlit

A simple chat interface built with Streamlit that allows you to interact with your local Ollama models and tailor your CV based on job descriptions, including parsing job descriptions from URLs.

## Prerequisites

1. Install [Ollama](https://ollama.ai/) on your system
2. Python 3.8 or higher
3. pip (Python package installer)

## Setup

1. Clone this repository:
```bash
git clone <your-repo-url>
cd ChatStreamlit
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Start Ollama and pull a model:
```bash
# Start Ollama (if not already running)
ollama serve

# In a new terminal, pull a model (e.g., llama2)
ollama pull llama2
```

## Running the Application

1. Make sure Ollama is running in the background
2. Start the Streamlit app:
```bash
streamlit run app.py
```

3. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

## Features

- Chat interface with message history
- Model selection (llama2, mistral, codellama, neural-chat)
- Clear chat history
- Error handling for Ollama connection issues
- **CV Tailoring:** Tailor your CV based on provided job descriptions.
- **Web Parsing:** Automatically parse job descriptions from URLs (currently supports some LinkedIn formats).
- **Master CV Upload:** Upload your master CV for tailoring.

## Notes

- The application connects to Ollama at `http://localhost:11434`
- Make sure you have enough system resources to run your chosen model
- The chat history is maintained during the session but will be cleared when you refresh the page
- Web parsing capabilities are experimental and may not work for all websites.
