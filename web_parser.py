from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time # Import time for potential waits
from google import genai
from pydantic import BaseModel
import os

class JobInfo(BaseModel):
    company_name: str
    job_description: str

def parse_job_description(url):
    """
    Parses a website for job description and company name using Selenium and BeautifulSoup.

    Args:
        url (str): The URL of the job posting.

    Returns:
        dict: A dictionary containing 'company' and 'job_description',
              or None if parsing fails.
    """
    driver = None # Initialize driver to None
    page_source = None # Initialize page_source to None
    try:
        if "linkedin.com" in url:
            # --- LinkedIn Parsing Logic (without Selenium) ---
            import requests
            response = requests.get(url)
            response.raise_for_status() # Raise an exception for bad status codes
            page_source = response.text
            # --- End LinkedIn Parsing Logic ---
        else:
            # --- General Website Parsing Logic (with Selenium) ---
            # Set up Selenium WebDriver (ensure you have the appropriate driver installed and in your PATH)
            # For Chrome: webdriver.Chrome()
            # For Firefox: webdriver.Firefox()
            # You might need to add options for headless browsing etc.
            driver = webdriver.Chrome() 
            
            driver.get(url)

            # Optional: Add a wait here if the page content is loaded dynamically
            # time.sleep(5) # Example: wait for 5 seconds

            # Get the page source after Selenium has loaded the page
            page_source = driver.page_source
            # --- End General Website Parsing Logic ---

        if not page_source:
             print(f"Failed to get page source for {url}")
             return None

        soup = BeautifulSoup(page_source, 'html.parser')

        company_name = "Unknown Company" # Default value
        job_description = "Job description not found." # Default value

        if "linkedin.com" in url:
            # --- LinkedIn Parsing Logic ---
            # Attempting to parse based on common LinkedIn job page structures.
            # Note: LinkedIn's structure can change, and this might not work for all pages.

            try:
                # Attempt to find the company name
                # Common selectors for company name on LinkedIn job pages
                company_element = soup.select_one('a[data-tracking-control-name="public_jobs_topcard_company_name"]')
                if not company_element:
                     company_element = soup.select_one('.topcard__flavor-row div a') # Another common selector

                if company_element:
                    company_name = company_element.get_text(strip=True)

                # Attempt to find the job description
                # Common selectors for job description on LinkedIn job pages
                description_element = soup.select_one('.description__text')
                if not description_element:
                    description_element = soup.select_one('.jobs-description__content') # Another common selector

                if description_element:
                    # Extract text and clean up potential extra whitespace/newlines
                    job_description = description_element.get_text(separator='\n', strip=True)

            except Exception as e:
                print(f"Error during LinkedIn parsing attempt: {e}")
                # Keep default values if parsing fails

            # --- End LinkedIn Parsing Logic ---
        else:
            # --- General Website Parsing Logic ---
            # Extract all text content from the body
            body_element = soup.find('body')
            if body_element:
                job_description = body_element.get_text(separator='\n', strip=True)
            print("Job Description:", job_description)
            # --- End General Website Parsing Logic ---

        # Call Gemini to extract structured data
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("GEMINI_API_KEY environment variable not set.")
                # Fall back to original parsing if API key is not available
                return {
                    "company": company_name,
                    "job_description": job_description
                }
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash", # Or another suitable model
                contents=f"Extract the company name and job description from the following text and return it as a JSON object with keys 'company_name' and 'job_description':\n\n{job_description}",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": JobInfo,
                },
            )
            # Use the parsed object
            extracted_data: JobInfo = response.parsed
            print("Successfully extracted data using Gemini:")
            print(f"Company Name: {extracted_data.company_name}")
            print(f"Job Description: {extracted_data.job_description}")

            # Return the extracted data in the desired dictionary format
            return {
                "company": extracted_data.company_name,
                "job_description": extracted_data.job_description
            }

        except Exception as e:
            print(f"An error occurred during Gemini API call or parsing: {e}")
            # If Gemini call fails, fall back to the original parsed data
            return {
                "company": company_name,
                "job_description": job_description
            }

    except Exception as e:
        print(f"An error occurred during parsing: {e}")
        return None
    finally:
        if driver:
            driver.quit() # Ensure the browser is closed even if an error occurs

if __name__ == '__main__':
    # Example Usage (replace with a real job posting URL for testing)
    test_url = "https://www.linkedin.com/jobs/view/4249975436" # Replace with a real URL
    job_data = parse_job_description(test_url)

    if job_data:
        print("Successfully parsed job data:")
        print(f"Company: {job_data['company']}")
        print(f"Job Description: {job_data['job_description']}")
    else:
        print("Failed to parse job data.")
