import requests
from bs4 import BeautifulSoup
import csv
import re
import time
from urllib.parse import urljoin, urlparse
from rich.pretty import pprint
import unicodedata
import os


def clean_text(text):
    """Clean text by removing unwanted Unicode characters and normalizing whitespace"""
    if not text:
        return text
    
    # Replace non-breaking spaces and other problematic Unicode chars with regular spaces
    text = text.replace('\xa0', ' ')  # Non-breaking space
    text = text.replace('\u00a0', ' ')  # Another form of non-breaking space
    text = text.replace('\u2000', ' ')  # En quad
    text = text.replace('\u2001', ' ')  # Em quad
    text = text.replace('\u2002', ' ')  # En space
    text = text.replace('\u2003', ' ')  # Em space
    text = text.replace('\u2009', ' ')  # Thin space
    text = text.replace('\u200a', ' ')  # Hair space
    
    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def clean_phone_number(phone):
    """Clean and format phone number to international standard"""
    if not phone:
        return phone
    
    # First clean the text
    phone = clean_text(phone)
    
    # Only clean phone numbers that start with + (international format)
    if phone.startswith('+'):
        # Simple approach: remove all spaces from international numbers
        phone = phone.replace(' ', '')
    
    return phone


# Get Google Maps API key from environment variable
API_KEY = os.getenv('API_KEY')


def get_coordinates(name, address):
    """Get latitude and longitude from address using Google Maps or Nominatim fallback"""
    # Try Google Maps first if API key is available
    if API_KEY:
        try:
            lat, lng = get_coordinates_google(address, API_KEY)
            if lat and lng:
                return lat, lng
        except Exception as e:
            print(f"Google Maps API failed, falling back to Nominatim: {e}")
    
    # Fall back to Nominatim (OpenStreetMap)
    try:
        # Using Nominatim (free, no API key needed)
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': name + " " + address,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'ChapelScraper/1.0 (your-email@example.com)'
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        
        return None, None
    except Exception as e:
        print(f"Error geocoding address '{address}': {e}")
        return None, None


# Alternative using Google Maps API (requires API key)
def get_coordinates_google(address, api_key):
    """Get latitude and longitude using Google Maps Geocoding API"""
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        
        return None, None
    except Exception as e:
        print(f"Error geocoding address '{address}': {e}")
        return None, None



def scrape_chapels_from_url(url):
    """Scrape chapel data from a single URL"""
    try:
        print(f"Scraping chapels from: {url}")
        
        r = requests.get(url, impersonate="chrome110")
        print(f"Status code: {r.status_code}")
        
        if r.status_code != 200:
            print(f"Failed to fetch {url}: {r.status_code}")
            return []
        
        soup = BeautifulSoup(r.content, "html.parser")
        
        # Find all chapel items
        chapels = []
        chapels_html = soup.find_all("article", class_="spotlight-row")
        
        print(f"Found {len(chapels_html)} chapels on {url}")
        
        for chapel_html in chapels_html:
            # Extract name
            name_elem = chapel_html.find("h2", class_="spotlight-row__title")
            name = clean_text(name_elem.text.strip()) if name_elem else ""
            
            # Extract full address (all components combined)
            address_elem = chapel_html.find("p", class_="address")
            if address_elem:
                address_parts = []
                
                # Get address line 1
                addr_line1 = address_elem.find("span", class_="address-line1")
                if addr_line1:
                    address_parts.append(clean_text(addr_line1.text.strip()))
                
                # Get address line 2
                addr_line2 = address_elem.find("span", class_="address-line2")
                if addr_line2:
                    address_parts.append(clean_text(addr_line2.text.strip()))
                
                # Get postal code
                postal_code = address_elem.find("span", class_="postal-code")
                if postal_code:
                    address_parts.append(clean_text(postal_code.text.strip()))
                
                # Get locality (city)
                locality = address_elem.find("span", class_="locality")
                if locality:
                    address_parts.append(clean_text(locality.text.strip()))
                
                # Get administrative area (state)
                admin_area = address_elem.find("span", class_="administrative-area")
                if admin_area:
                    address_parts.append(clean_text(admin_area.text.strip()))
                
                # Get country
                country = address_elem.find("span", class_="country")
                if country:
                    address_parts.append(clean_text(country.text.strip()))
                
                address = ", ".join(address_parts)
            else:
                address = ""
            
            # Extract phone
            phone_elem = chapel_html.find("span", class_="spotlight-row__item-content")
            phone = clean_phone_number(phone_elem.text.strip()) if phone_elem else ""
            
            # Extract website
            website_elem = chapel_html.find("a", class_="spotlight-row__link")
            website = website_elem.get("href") if website_elem else ""
            
            # Extract schedule/comments
            schedule_elem = chapel_html.find("span", class_="spotlight-row__text--small")
            comments = clean_text(schedule_elem.text.strip()) if schedule_elem else ""
            
            # Get coordinates
            lat, lng = get_coordinates(name, address)
            
            chapel_data = {
                "name": name,
                "address": address,
                "phone": phone,
                "website": website,
                "comments": comments,
                "latitude": lat,
                "longitude": lng
            }
            
            chapels.append(chapel_data)
            print(f"Added: {name}")
            
            # Add delay to be respectful to geocoding service
            time.sleep(1)
        
        return chapels
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []


CHAPEL_LINKS = [
    "https://centroamerica.fsspx.org/es/capillas-1",
    "https://fsspx-sudamerica.org/es/capillas",
    "https://fsspx.mx/es/capillas-2",
]

from curl_cffi import requests

# Main scraping loop
all_chapels = []

for url in CHAPEL_LINKS:
    chapels_from_url = scrape_chapels_from_url(url)
    all_chapels.extend(chapels_from_url)
    print(f"Total chapels so far: {len(all_chapels)}")
    
    # Add delay between different sites
    time.sleep(2)

print(f"\nTotal chapels scraped: {len(all_chapels)}")

# Save to JSON file
with open("chapels.json", "w", encoding='utf-8') as f:
    import json
    json.dump(all_chapels, f, indent=2, ensure_ascii=False)

print("Chapels saved to chapels.json")