"""
Author: Yahya Khawaja
Date: 2024-10-16
Description: Recursively scrapes properties in Lahore from zameen.com and extracts useful property information for research purposes. Use hyper-parameters to adjust scraping duration.
Version: 1.0
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import csv
import json
import random
import concurrent.futures

# Hyperparameters
BASE_URL = "https://www.zameen.com/Homes/Lahore-1-{}.html"
DELAY = 0 ## Delay between requests (for ethical purposes and to avoid DOS)
ID = 0 ## Unique id for each property
MAX_PAGES = 1000 ## Total Number of pages on Zameen(each page has approx 20 properties)
NUM_PAGES_TO_SCRAPE = 500 ## Randomly select 500 out of 1000 total pages

## Seed for reproducibility
SEED = 41
random.seed(SEED)

def extract_properties(soup):
    global ID
    property_info = {}

    price = soup.find('span', {'aria-label': 'Price'})
    type_ = soup.find('span', {'aria-label': 'Type'})
    # initial_amount = soup.find('span', {'aria-label': 'advance'})
    # monthly_installments = soup.find('span', {'aria-label': 'Monthly installment'})
    # remaining_installments = soup.find('span', {'aria-label': 'Remaining installments'})
    location = soup.find('span', {'aria-label': 'Location'})
    location_precise = soup.find('div', {'aria-label': 'Property header'})
    baths = soup.find('span', {'aria-label': 'Baths'})
    area = soup.find('span', {'aria-label': 'Area'})
    purpose = soup.find('span', {'aria-label': 'Purpose'})
    beds = soup.find('span', {'aria-label': 'Beds'})
    creation_date = soup.find('span', {'aria-label': 'Creation date'})
    description = soup.find('div', {'aria-label': 'Property description'})

    script = soup.find('script', string=re.compile('window\\[\'dataLayer\'\\]')) ## Regex to find appropriate text block in javascript

    # amenities = soup.find('div', class_='_51519f00')
    # more_amenities = soup.find('div', class_='_3efd3392')

    property_info['home_id'] = ID
    ID += 1
    property_info['price'] = price.get_text(strip=True) if price else 'N/A'
    property_info['type'] = type_.get_text(strip=True) if type_ else 'N/A'
    # property_info['intial_amount'] = initial_amount.get_text(strip=True) if initial_amount else 'N/A'
    # property_info['monthly_installments'] = monthly_installments.get_text(strip=True) if monthly_installments else 'N/A'
    # property_info['remaining_installments'] = remaining_installments.get_text(strip=True) if remaining_installments else 'N/A'
    property_info['location'] = location.get_text(strip=True) if location else 'N/A'
    property_info['location_precise'] = location_precise.get_text(strip=True) if location_precise else 'N/A'    
    property_info['baths'] = baths.get_text(strip=True) if baths else 'N/A'
    property_info['area'] = area.get_text(strip=True) if area else 'N/A'
    property_info['purpose'] = purpose.get_text(strip=True) if purpose else 'N/A'
    property_info['beds'] = beds.get_text(strip=True) if beds else 'N/A'
    property_info['creation_date'] = creation_date.get_text(strip=True) if creation_date else 'N/A'

    if script:
        script_content = script.string
        json_text = re.search(r'window\[\'dataLayer\'\]\s*=\s*window\[\'dataLayer\'\]\s*\|\|\s*\[\];\s*window\[\'dataLayer\'\]\.push\((\{.*\})\);', script_content)

        if json_text:
            json_data = json_text.group(1)
        
            data_layer = json.loads(json_data)
            # This was a pain in the ass to find
            property_info['latitude'] = data_layer.get('latitude') if data_layer.get('latitude') else 'N/A'
            property_info['longitude'] = data_layer.get('longitude') if data_layer.get('longitude') else 'N/A'


    property_info['description'] = description.get_text(strip=True) if description else 'N/A'

    # print(property_info)
    return property_info


def fetch_property_links(soup):
    property_links = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if re.search(r'^/Property/', href):
            full_link = 'https://www.zameen.com' + href
            property_links.append(full_link)
    
    return property_links

def fetch_property_details(link, visited):
    """Fetches and extracts property details for a given link."""
    if link not in visited:
        visited.add(link)
        
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.content, 'lxml')
            property_info = extract_properties(soup)
            return property_info
        except Exception as e:
            print(f"Error fetching {link}: {e}")
            return None  # Handle errors gracefully
    return None  # If the link was already visited


def crawl_properties(url, visited=set(), scraped_properties=[]):
    time.sleep(DELAY)
    try:
        response = requests.get(url)
    except:
        return None

    soup = BeautifulSoup(response.content, 'lxml')
    links = fetch_property_links(soup)

    ## Multi-Threading to boost speed, got a 5x speed boost (very unethical)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_property_details, link, visited): link for link in links}

        for future in concurrent.futures.as_completed(futures):
            property_info = future.result()
            if property_info:
                scraped_properties.append(property_info)

    return scraped_properties

def save_to_csv(properties, filename='properties.csv'):
    keys = properties[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(properties)
    print(f"Data saved to {filename}")

def save_to_json(properties, filename='properties.json'):
    with open(filename, 'w', encoding='utf-8') as output_file:
        json.dump(properties, output_file, ensure_ascii=False, indent=4)
    print(f"Data saved to properties.json")

if __name__ == '__main__':
    all_properties = []
    visited=set()

    ## Random Sampling to avoid popularity bias, pick 200 out of 1000 pages, each page contains 20 pages
    ## Cluster Sampling
    start = time.time()
    random_pages = set(random.sample(range(1, MAX_PAGES + 1), NUM_PAGES_TO_SCRAPE))
    for page_num in random_pages:
        url = BASE_URL.format(page_num)
        print(f"Scraping page: {url}")
        all_properties = crawl_properties(url, visited=visited, scraped_properties=all_properties)
    end = time.time()
    
    elapsed_time = end-start
    hours = elapsed_time // 3600
    minutes = (elapsed_time % 3600) // 60
    seconds = elapsed_time % 60

    print(f"\n\nElapsed time: {int(hours)} hours, {int(minutes)} minutes, and {seconds:.2f} seconds")

    save_to_json(all_properties)
    save_to_csv(all_properties)