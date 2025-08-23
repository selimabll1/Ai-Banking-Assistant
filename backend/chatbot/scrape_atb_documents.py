from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.atb.tn"

# List of URLs to scrape
credit_urls = [
       f"{BASE_URL}/produits/credit-sakan-presentation.php",
    f"{BASE_URL}/produits/credit-mounassib-presentation.php",
    f"{BASE_URL}/produits/credit-tahawel-presentation.php",
    f"{BASE_URL}/produits/credit-sayara-presentation.php",
    f"{BASE_URL}/produits/credit-Renov-presentation.php",
    f"{BASE_URL}/produits/credit-start-presentation.php",
    f"{BASE_URL}/produits/credit-tahawel-presentation.php",
    f"{BASE_URL}/produits/credit-Bien-etre-presentation.php",
    f"{BASE_URL}/produits/services-transfert-presentation.php",
    f"{BASE_URL}/produits/services-change-presentation.php",
    f"{BASE_URL}/produits/services-gestion-presentation.php",
    f"{BASE_URL}/produits/placement-depots-presentation.php",
    f"{BASE_URL}/produits/placement-valeur-presentation.php",
    f"{BASE_URL}/produits/placement-sicav-presentation.php",
    f"{BASE_URL}/produits/placement-autre-presentation.php",
    f"{BASE_URL}/produits/epargne-elkhir-presentation.php",
    f"{BASE_URL}/produits/epargne-conv-presentation.php",
    f"{BASE_URL}/produits/epargne-invest-presentation.php",
    f"{BASE_URL}/produits/compte-cheques-presentation.php",
    f"{BASE_URL}/produits/compte-cheques-conv-tre-presentation.php",
    f"{BASE_URL}/produits/compte-cheques-spec-conv-devis-presentation.php",
    f"{BASE_URL}/produits/compte-cheques-prof-conv-devis-presentation.php",
    f"{BASE_URL}/produits/compte-cheques-conv-presentation.php",
    f"{BASE_URL}/produits/compte-cheques-interieur-non-resident-presentation.php",
    f"{BASE_URL}/produits/services-banque-presentation.php",
    f"{BASE_URL}/produits/services-mobilink-presentation.php",
    f"{BASE_URL}/produits/services-ATBPAY-presentation.php"
    # Add more URLs
]

# Function to use Selenium to get page content
def extract_credit_info_selenium(credit_url):
    try:
        # Initialize the Chrome WebDriver using the Service object
        options = Options()
        options.headless = True  # Run in headless mode (no GUI)

        # Create Service object and specify the path to chromedriver
        service = Service(ChromeDriverManager().install())  # Automatically download the chromedriver

        driver = webdriver.Chrome(service=service, options=options)
        driver.get(credit_url)
        
        # Wait for content to load
        time.sleep(3)  # Increase sleep time if content loads slowly
        
        # Get the page content after loading
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract title from headers (h1, h2, h3)
        title = ""
        for tag in ['h1', 'h2', 'h3']:
            title_tag = soup.find(tag)
            if title_tag:
                title = title_tag.text.strip()
                break  # Stop once the first title is found
        
        # Extract all paragraphs or specific content sections
        content = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text:
                content.append(text)

        # Save content to a file or print it
        if content:
            save_content_to_file(title, "\n".join(content))
        else:
            print(f"\n=== {title} ===\nNo detailed content found.")

        driver.quit()

    except Exception as e:
        print(f"[!] Error extracting content from {credit_url}: {e}")
        time.sleep(2)

def save_content_to_file(title, content):
    output_path = 'scraped_content_selenium.txt'
    with open(output_path, 'a', encoding='utf-8') as f:
        f.write(f"=== {title} ===\n{content}\n\n")
    print(f"Content saved to {output_path}")

def scrape_credit_pages_selenium():
    for credit_url in credit_urls:
        print(f"[*] Scraping content from {credit_url}...")
        extract_credit_info_selenium(credit_url)
        time.sleep(1)

if __name__ == "__main__":
    scrape_credit_pages_selenium()
