import requests
import streamlit as st
import openai
import json
from datatypes.CV_obj import CV


# Function to get response from LLM
import os
from dotenv import load_dotenv

load_dotenv()


def get_model_response(prompt, model, api_provider, api_key, type):
    if type == "CV":
        prompt_prefix = "Based on this job description, identify keywords, skills and experience requirements" \
        "and tailor the master CV. Select a subset of relevant projects from the master CV with a concise profile." \
        "The CV should be of the following format:" \
        "1. Personal Profile must be 80 words or under." \
        "2. Each Project should have atmost 4 points in logical order." \
        "3. Each Job role must contain 3-4 points describing the roles and responsibilities taken in that job." \
        "4. DO NOT ASSUME ADDITIONAL SKILLS OR EXPERIENCES NOT IMPLIED IN THE MASTER CV, the CV is the only ground truth for the user's experience." \
        "5. Keep the Education segment the same." \
        "6. Keep all the job titles and dates, refine the content if needed based on the description." \
        "7. Use bulleted lists for all the descriptors like Experience and Projects."\
        "Only provide the updated CV with proper formatting and spacing as the final output " \
        "DO NOT PRODUCE ADDITIONAL TEXT BEYOND THE UPDATED CV."
    elif type == "CL":
        prompt_prefix = "Based on this job description, identify keywords, skills and experience requirements" \
        "write a cover letter using the master CV provided" \
        "Ensure the output only the cover letter and nothing else." \
        "Use the name and contact details from the CV and job description" \
        "DO NOT ASSUME ADDITIONAL SKILLS OR EXPERIENCES NOT IMPLIED IN THE MASTER CV"

    master_cv_content = st.session_state.get("master_cv_content")
    if not master_cv_content:
        st.error("Master CV content not found in session state. Please upload your CV.")
        return None

    master_cv_data = "Master CV:" + master_cv_content
    final_prompt = prompt_prefix + prompt + master_cv_data
    if api_provider == "Ollama":
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": final_prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to Ollama: {str(e)}")
            return None
    elif api_provider == "OpenAI":
        openai.api_key = api_key
        try:
            response = openai.Completion.create(
                engine=model,
                prompt=final_prompt,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.7,
            )
            return response.choices[0].text.strip()
        except Exception as e:
            st.error(f"Error connecting to OpenAI: {str(e)}")
            return None
    elif api_provider == "Gemini":
        from google import genai
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            st.error("Gemini API key not found in environment variables.")
            return None
        client = genai.Client(api_key=gemini_api_key)

        if type == "CV":
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=final_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": CV,
                },
            )
            st.session_state["updated_CV_obj"] = response.parsed
            markdown_cv = cv_to_markdown(response.parsed)
            return markdown_cv
        else:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=final_prompt,
            )
            return response.text
    else:
        st.error("API Provider not implemented yet.")
        return None

def cv_to_markdown(cv_data: CV) -> str:
    """Converts a CV object to a Markdown formatted string."""
    st.session_state['user_name'] = cv_data.full_name
    markdown_output = f"# **{cv_data.full_name}**\n\n"

    markdown_output += f"**LinkedIn:** {cv_data.linkedin}\n"
    if cv_data.github:
        markdown_output += f"**GitHub:** {cv_data.github}\n\n"
    else:
        markdown_output += "\n"

    markdown_output += f"**Personal Profile**\n{cv_data.personal_profile}\n\n"

    markdown_output += "**Skills**\n"
    for skill_category in cv_data.skills:
        markdown_output += f"- **{skill_category.skill_subcategory}**"
        for skill in skill_category.skill_list:
            markdown_output += f" {skill},"
        markdown_output += "\n\n"

    markdown_output += "**Experience**\n\n"
    for job in cv_data.experience:
        markdown_output += f"**{job.company_name} ({job.date_from} - {job.date_to})**\n"
        for responsibility in job.responsibilities:
            markdown_output += f"- {responsibility}\n"
        markdown_output += "\n"

    markdown_output += "**Education**\n\n"
    for education in cv_data.education:
        markdown_output += f"**{education.degree}, {education.university}, {education.grade} ({education.date_from} - {education.date_to})**\n\n"

    markdown_output += "**Projects**\n\n"
    for project in cv_data.projects:
        markdown_output += f"**{project.project_title}**\n"
        for description_point in project.description:
            markdown_output += f"- {description_point}\n"
        markdown_output += "\n"

    return markdown_output
