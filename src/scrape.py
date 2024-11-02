import requests
from bs4 import BeautifulSoup
import json
import os
import sys
import time
from requests.exceptions import HTTPError, RequestException
from utils import clean_text

# Ensure config and utils are accessible from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import SELECTORS, BASE_URL

# Constants
LOG_FILE = '../logs/scrape_log.txt'
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Function to fetch a specific section based on selectors
def fetch_section(url, selectors, max_retries=MAX_RETRIES):
    """
    Fetches and returns the text content of a specific section on a webpage,
    identified by a list of selectors. Handles retries and logs errors.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Ensure selectors is a list; if it's a single dict, wrap it in a list
            if isinstance(selectors, dict):
                selectors = [selectors]

            # Try each selector until a match is found
            for selector in selectors:
                filter_args = {key: selector[key] for key in ['id', 'class', 'href'] if key in selector}
                section = soup.find(selector.get('tag'), filter_args)

                if section:
                    return clean_text(section.get_text(strip=True))

            # If no selector matched, log and return None
            log_error(f"No matching section found for selectors: {selectors} on {url}")
            return None

        except HTTPError as e:
            log_error(f"HTTP error while fetching {url}: {e}")
        except RequestException as e:
            log_error(f"Request error while fetching {url}: {e}")
        except Exception as e:
            log_error(f"Unexpected error while fetching {url} with selectors {selectors}: {e}")

        time.sleep(RETRY_DELAY)  # Wait before retrying

    log_error(f"Failed to fetch {url} after {max_retries} attempts")
    return None


def log_error(message):
    """Appends an error message to the log file."""
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


# Main function to fetch client profile data
def scrape_client_profile(base_url_dict, filename='/Users/prakharpandey/Desktop/ComputerScience_/scrap/data/client_profiles.json'):
    """
    Scrapes the client profiles based on provided URLs and selectors,
    saves the output to a JSON file, and handles appending if the file already exists.
    """
    client_profiles = []

    for client, url in base_url_dict.items():
        client_selectors = SELECTORS.get(client, {})

        # Fetch sections based on selectors if they exist
        about_us_content = fetch_section(url, client_selectors.get('about_us', [{}])[0])  # Use default empty selector if missing
        services_content = fetch_section(url, client_selectors.get('services', [{}])[0])
        media_content = fetch_section(url, client_selectors.get('media', [{}])[0])

        # Add fetched data to the client profile
        client_profile = {
            "client": client,
            "about_us": about_us_content,
            "services_offered": services_content,
            "media": media_content,
        }
        client_profiles.append(client_profile)

    # Save all client profiles as JSON
    save_json(filename, client_profiles)


def save_json(filename, data):
    """Saves or appends JSON data to a specified file."""
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    # Check if the file exists and append or create a new one
    if os.path.exists(filename):
        with open(filename, 'r+') as file:
            existing_data = json.load(file)
            existing_data.extend(data)
            file.seek(0)
            json.dump(existing_data, file, indent=4)
    else:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

    print("Data saved successfully.")


# Example usage
if __name__ == "__main__":
    scrape_client_profile(BASE_URL)
