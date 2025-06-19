import requests
import streamlit as st
import json

def generate_chat_title(history, model):
    prompt = "Please generate a short title (max 5 words) for the following chat history, do not provide any extra text other than the title:\\n"
    for message in history:
        prompt += f"{message['role']}: {message['content']}\\n"
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"].split('</think>')[-1].strip().replace("\"", "")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to Ollama: {str(e)}")
        return "Untitled Chat"
