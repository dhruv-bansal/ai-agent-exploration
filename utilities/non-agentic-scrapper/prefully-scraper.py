import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import logging
from urllib.parse import quote

# Cache dictionary to store responses
response_cache = {}

def configure_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger('urllib3').setLevel(logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.DEBUG)


def load_env_variables():
    load_dotenv()
    return {
        'company': os.getenv('COMPANY_NAME'),
        'position': os.getenv('POSITION'),
        'tag': os.getenv('TAG')
    }

def get_response(url):
    if url in response_cache:
        logging.info(f"Using cached response for {url}")
        return response_cache[url]
    else:
        response = requests.get(url)
        response_cache[url] = response
        return response


def get_page_url(company, position, tag, page=None):
    base_url = "https://prepfully.com/interview-questions/"
    company = quote(company)
    position = quote(position)
    tag = quote(tag)
    if page:
        search_url = f"{base_url}{company}/{position}?page={page}&type={tag}"
    else:
        search_url = f"{base_url}{company}/{position}?type={tag}"

    logging.info(f"Scraping page {search_url}")
    return search_url

def extract_questions_from_page(url):
    # Send request to the page
    response = get_response(url)
    # add log to print all the response html
    logging.debug(f"Response HTML: {response.text}")
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find questions based on the class 'text-lg'
    questions = []
    question_elements = soup.find_all('div', class_='mb-1 line-clamp-2 text-lg font-medium')

    for question in question_elements:
        text = question.get_text(strip=True)
        if text:
            questions.append(text)

    return questions




def scrape_questions(company, position, tag):

    page = 1
    all_questions = []

    while True:
        url = get_page_url(company, position, tag, page)
        print(f"Scraping page {page}: {url}")
        questions = extract_questions_from_page(url)

        if not questions:  # If no questions are found, stop
            break

        all_questions.extend(questions)
        page += 1

    # Output to a text file
    with open(f"{company}_{position}_{tag}_questions.txt", "w") as f:
        for question in all_questions:
            f.write(question + "\n")

    print(f"Scraping completed. {len(all_questions)} questions saved to {company}_{position}_{tag}_questions.txt")


if __name__ == "__main__":
    configure_logging()
    env_vars = load_env_variables()

    scrape_questions(env_vars['company'], env_vars['position'], env_vars['tag'])

