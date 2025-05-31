import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import io



def crawl_wikipedia(url):
    print(f"Using Wikipedia crawler: {url}")
    # Send an HTTP GET request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching the page: Status code {response.status_code}")
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locate the main content area. Wikipedia articles are contained in the div with id "mw-content-text"
    content_div = soup.find('div', id='mw-content-text')
    if content_div is None:
        raise Exception("Couldn't find the main content on the page.")
    
    # Optionally, you can remove unwanted tags like tables, edit links, or reference markers.
    # Here we decompose some common unwanted elements.
    for tag in content_div.find_all(['table', 'sup']): # ['table', 'sup', 'span', 'div']
        tag.decompose()
    
    # Extract all paragraphs within the main content and join them into one coherent text
    paragraphs = content_div.find_all('p')
    text = "\n".join([para.get_text().strip() for para in paragraphs if para.get_text().strip()])
    print("Crawl done")
    return text.strip()

# we really only want the summaries (unless its one of those short wikipedia pages)
def crawl_wikipedia_summary(url):
    print(f"Using Wikipedia summary crawler: {url}")
    # Send an HTTP GET request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching the page: Status code {response.status_code}")
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locate the main content area. Wikipedia articles are contained in the div with id "mw-content-text"
    content_div = soup.find('div', id='mw-content-text')
    if content_div is None:
        raise Exception("Couldn't find the main content on the page.")
    
    # Remove unwanted tags (e.g., tables, sup tags) before extracting paragraphs
    for tag in content_div.find_all(['table', 'sup']):
        tag.decompose()
    
    # Collect only the opening summary paragraphs: iterate through <p> and <h2>/<h3> in document order
    summary_paragraphs = []
    for element in content_div.find_all(['p', 'h2', 'h3'], recursive=True):
        # If we hit a <h2> or <h3>, that signals the end of the lead (opening summary)
        if element.name in ('h2', 'h3'):
            break
        # Otherwise, if it's a <p> with non-empty text, add it to the summary
        text = element.get_text().strip()
        if element.name == 'p' and text:
            summary_paragraphs.append(text)
    
    summary_text = "\n\n".join(summary_paragraphs).strip()
    print("Summary crawl done")
    return summary_text

def generic_scrape(url):
    print(f"Using generic crawler: {url}")
    # Send an HTTP GET request to the URL.
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching the page: Status code {response.status_code}")
    
    # Parse the HTML content.
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove unwanted elements that likely do not contribute to the main text.
    for tag in soup.find_all(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
        tag.decompose()
    
    # Try to locate the main content container.
    container = soup.find('main')
    if container is None:
        container = soup.find('body')
    if container is None:
        container = soup  # Fallback: use the entire document
    
    # Extract all text with a newline as a separator.
    raw_text = container.get_text(separator="\n")
    
    # Clean up the text: remove extra spaces and blank lines.
    lines = [line.strip() for line in raw_text.splitlines()]
    text = "\n".join([line for line in lines if line])
    
    print("Crawl done")
    return text

def crawl_link(url):
    crawl_result = ""
    if "wikipedia.org" in url:
        crawl_result = crawl_wikipedia_summary(url)
        if (len(crawl_result) < 3000):
            crawl_result = crawl_wikipedia(url)
            if len(crawl_result) > 10000:
                crawl_result = crawl_result[:10000]
    else:
        crawl_result = generic_scrape(url)
    return crawl_result

if __name__ == '__main__':
    # url = "https://baike.baidu.com/item/%E7%8E%8B%E9%8F%8A/4184443"
    url = "https://zh.wikipedia.org/wiki/%E7%8E%8B%E9%8F%8A"
    # url = "https://en.wikipedia.org/wiki/Otto_von_Bismarck"
    # url = "https://www.britannica.com/biography/Isaac-Newton"
    # url = "https://www.bbc.co.uk/teach/articles/zh8792p"

    # url = "https://en.wikipedia.org/wiki/Sir_William_Molesworth,_8th_Baronet"
    # url = "https://en.wikipedia.org/wiki/Edwin_Freiherr_von_Manteuffel"

    try:
        text_data = crawl_link(url)
        print("\n--- Extracted Article Text ---\n")
        print(text_data)
    except Exception as e:
        print(f"An error occurred: {e}")
