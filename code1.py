from googlesearch import search
import requests
from bs4 import BeautifulSoup
import re
import csv
import time
from fake_useragent import UserAgent

# Configuration
COUNTRIES = {
    "USA": "site:.us",
    "UK": "site:.co.uk",
    "Australia": "site:.com.au"
}
CSV_FILE = "tier1_clothing_dealers.csv"
CSV_HEADERS = ["Business Name", "Email", "Phone", "Website", "Country"]
REQUIRED_TOTAL = 50

ua = UserAgent()

def extract_contact_info(url, country_name):
    try:
        headers = {'User-Agent': ua.random}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text()

        email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        if not email:
            return None  # Email is mandatory

        phone = re.search(r'(?:(?:\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{6,10})', text)
        business_name = ""

        for tag in soup.find_all(['h1', 'h2', 'title']):
            if tag.text.strip() and any(word in tag.text.lower() for word in ["garment", "clothing", "fashion", "wear", "textile", "manufacturer", "company"]):
                business_name = tag.text.strip()
                break

        if not business_name:
            business_name = soup.title.string.strip() if soup.title else "N/A"

        return {
            "Business Name": business_name,
            "Email": email.group(0),
            "Phone": phone.group(0) if phone else "",
            "Website": url,
            "Country": country_name
        }

    except Exception:
        return None

def search_and_scrape():
    collected = []
    print(f"🔍 Starting scraping for Tier 1 countries...")

    for country, domain in COUNTRIES.items():
        query = f"clothing dealers manufacturers {country} {domain}"
        print(f"\n🌐 Searching: {query}")
        urls = search(query, num_results=30)
        
        for url in urls:
            if any(skip in url for skip in ["facebook", "youtube", "linkedin", "microsoft", "wiki"]):
                continue
            info = extract_contact_info(url, country)
            if info:
                print(f"✅ {info['Business Name']} | {info['Email']}")
                collected.append(info)
            if len(collected) >= REQUIRED_TOTAL:
                return collected
            time.sleep(1)  # polite delay

    return collected

def save_to_csv(data):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(data)

# Run
start = time.time()
results = search_and_scrape()
save_to_csv(results)

print(f"\n✅ {len(results)} genuine dealers saved in '{CSV_FILE}'")
print(f"⏱️ Done in {round(time.time() - start, 2)} seconds.")
