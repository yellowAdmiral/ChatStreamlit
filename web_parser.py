import requests
from bs4 import BeautifulSoup

def parse_job_description(url):
    """
    Parses a website for job description and company name.

    Args:
        url (str): The URL of the job posting.

    Returns:
        dict: A dictionary containing 'company' and 'job_description',
              or None if parsing fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- LinkedIn Parsing Logic ---
        # Attempting to parse based on common LinkedIn job page structures.
        # Note: LinkedIn's structure can change, and this might not work for all pages.

        company_name = "Unknown Company" # Default value
        job_description = "Job description not found." # Default value

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

        return {
            "company": company_name,
            "job_description": job_description
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
    except Exception as e:
        print(f"An error occurred during parsing: {e}")
        return None

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
