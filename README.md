# CS 334 Group Project

This repository is dedicated to our CS 334 Group Project.

### Authors:
- Yahya Khawaja
- Abdullah Sohail
- Sujo Punar
- Bushra Zubair
- Syed Shaheer

## Scraper.py

### Features
- **Scrapes property details from zameen.com**
- **Extracts various information such as:**
  - Price
  - Type (e.g., residential, commercial)
  - Location
  - Area
  - Number of beds and baths
  - Creation date
  - Description
  - Latitude and longitude
- **Allows configuration of scraping parameters** (e.g., number of pages to scrape)
- **Saves the scraped data in CSV and JSON formats**

### Requirements
- Python 3.x
- `requests`
- `BeautifulSoup4`
- `lxml`
- `concurrent.futures`

### Hyperparameters
- **BASE_URL**: Base URL template for scraping property listings.
- **DELAY**: Delay between requests (set for ethical scraping to avoid overwhelming the server).
- **MAX_PAGES**: Total number of pages available on the website (default is set to 1000).
- **NUM_PAGES_TO_SCRAPE**: Number of pages to scrape (randomly selected from the total pages).

### Ethical Considerations
The scraper includes a delay between requests to minimize the risk of overwhelming the server. It is important to scrape responsibly and avoid any actions that may be interpreted as a Denial-of-Service (DOS) attack.
