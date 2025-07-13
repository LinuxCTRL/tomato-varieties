#!/usr/bin/env python3
"""
Test script to analyze the HTML structure of tomato variety pages
and improve data extraction
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def test_variety_page(url):
    """Test extraction from a specific variety page"""
    
    print(f"🔍 Testing variety page: {url}")
    print("=" * 80)
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get the raw text to see the structure
        raw_text = soup.get_text()
        print("📄 Raw text sample:")
        print(raw_text[:500])
        print("\n" + "=" * 80)
        
        # Look for the specific pattern in the text
        characteristics = {}
        
        # The data appears to be in plain text format like:
        # Tomato Type: Heirloom
        # Breed: Open Pollinated
        # etc.
        
        # Extract structured data using regex patterns
        patterns = {
            'tomato_type': r'Tomato Type:\s*([^\n\r]+)',
            'breed': r'Breed:\s*([^\n\r]+)',
            'origin': r'Origin:\s*([^\n\r]+)',
            'season': r'Season:\s*([^\n\r]+)',
            'leaf_type': r'Leaf Type:\s*([^\n\r]+)',
            'plant_type': r'Plant Type:\s*([^\n\r]+)',
            'plant_height': r'Plant Height:\s*([^\n\r]+)',
            'fruit_size': r'Fruit Size:\s*([^\n\r]+)',
            'fruit_shape': r'Fruit Shape:\s*([^\n\r]+)',
            'skin_color': r'Skin Color:\s*([^\n\r]+)',
            'flesh_color': r'Flesh Color:\s*([^\n\r]+)',
            'taste': r'Taste:\s*([^\n\r]+)',
            'comments': r'Comments:\s*([^\n\r]+)',
            'days_to_maturity': r'Days to Maturity:\s*([^\n\r]+)',
        }
        
        print("🔍 Extracted characteristics:")
        for key, pattern in patterns.items():
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                characteristics[key] = value
                print(f"   {key}: {value}")
        
        if not characteristics:
            print("❌ No characteristics found with regex patterns")
            print("\n🔍 Let's look for the data in different ways...")
            
            # Try to find specific text patterns
            lines = raw_text.split('\n')
            for i, line in enumerate(lines):
                if 'Tomato Type:' in line or 'Breed:' in line or 'Origin:' in line:
                    print(f"Line {i}: {line.strip()}")
                    # Print surrounding lines for context
                    for j in range(max(0, i-2), min(len(lines), i+10)):
                        if j != i:
                            print(f"     {j}: {lines[j].strip()}")
                    break
        
        return characteristics
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def improved_scrape_variety_details(variety_url, variety_name):
    """Improved version of the scrape function"""
    
    try:
        response = requests.get(variety_url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract all available information
        variety_details = {
            'name': variety_name,
            'url': variety_url,
            'description': '',
            'characteristics': {},
            'growing_info': {},
            'images': [],
            'raw_text': ''
        }

        # Get page title
        if soup.title:
            variety_details['page_title'] = soup.title.get_text(strip=True)

        # Extract text content
        raw_text = soup.get_text(separator=' ', strip=True)
        variety_details['raw_text'] = raw_text

        # Improved extraction using regex patterns for the specific format
        patterns = {
            'tomato_type': r'Tomato Type:\s*([^\n\r]+)',
            'breed': r'Breed:\s*([^\n\r]+)', 
            'origin': r'Origin:\s*([^\n\r]+)',
            'season': r'Season:\s*([^\n\r]+)',
            'leaf_type': r'Leaf Type:\s*([^\n\r]+)',
            'plant_type': r'Plant Type:\s*([^\n\r]+)',
            'plant_height': r'Plant Height:\s*([^\n\r]+)',
            'fruit_size': r'Fruit Size:\s*([^\n\r]+)',
            'fruit_shape': r'Fruit Shape:\s*([^\n\r]+)',
            'skin_color': r'Skin Color:\s*([^\n\r]+)',
            'flesh_color': r'Flesh Color:\s*([^\n\r]+)',
            'taste': r'Taste:\s*([^\n\r]+)',
            'comments': r'Comments:\s*([^\n\r]+)',
            'days_to_maturity': r'Days to Maturity:\s*([^\n\r]+)',
        }
        
        # Extract characteristics using regex
        for key, pattern in patterns.items():
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Clean up the value (remove extra whitespace, trailing periods, etc.)
                value = re.sub(r'\s+', ' ', value).strip()
                variety_details['characteristics'][key] = value

        # Extract images
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src and not src.startswith('data:'):
                full_img_url = urljoin(variety_url, str(src))
                variety_details['images'].append({
                    'url': full_img_url,
                    'alt': alt
                })

        # Extract description from paragraphs or specific content areas
        paragraphs = soup.find_all('p')
        if paragraphs:
            variety_details['description'] = ' '.join([p.get_text(strip=True) for p in paragraphs[:2]])

        return variety_details

    except Exception as e:
        print(f"❌ Error scraping {variety_url}: {e}")
        return None

if __name__ == "__main__":
    # Test with the specific URL you mentioned
    test_url = "https://njaes.rutgers.edu/tomato-varieties/variety.php?A+Grappoli+D%27Inverno"
    
    print("🍅 Testing Improved Variety Data Extraction")
    print("=" * 80)
    
    # Test the extraction
    characteristics = test_variety_page(test_url)
    
    print(f"\n🧪 Testing improved extraction function...")
    improved_data = improved_scrape_variety_details(test_url, "A Grappoli D'Inverno")
    
    if improved_data:
        print(f"\n✅ Improved extraction results:")
        print(f"   Name: {improved_data['name']}")
        print(f"   Characteristics found: {len(improved_data['characteristics'])}")
        for key, value in improved_data['characteristics'].items():
            print(f"      {key}: {value}")
        print(f"   Images found: {len(improved_data['images'])}")
        print(f"   Description: {improved_data['description'][:100]}...")
    else:
        print("❌ Improved extraction failed")