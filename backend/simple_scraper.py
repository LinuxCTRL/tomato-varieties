#!/usr/bin/env python3
"""
Simple Tomato Varieties Scraper using built-in libraries
"""

import urllib.request
import urllib.parse
import json
import re
import time

def fetch_page(url):
    """Fetch webpage content using urllib"""
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_basic_info(html_content):
    """Extract basic information from HTML using regex patterns"""
    varieties = []
    
    # Look for table rows that might contain variety information
    table_pattern = r'<tr[^>]*>(.*?)</tr>'
    table_matches = re.findall(table_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    print(f"Found {len(table_matches)} table rows")
    
    # Look for links that might be varieties
    link_pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>'
    link_matches = re.findall(link_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    print(f"Found {len(link_matches)} links")
    
    # Filter links that might be tomato varieties
    variety_links = []
    for href, text in link_matches:
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        if clean_text and len(clean_text) > 2:
            # Skip navigation links
            skip_terms = ['home', 'contact', 'about', 'search', 'menu', 'rutgers', 'njaes']
            if not any(term in clean_text.lower() for term in skip_terms):
                variety_links.append({
                    'name': clean_text,
                    'url': href
                })
    
    return variety_links[:50]  # Return first 50 for analysis

def analyze_page_structure(html_content):
    """Analyze the HTML structure to understand the data layout"""
    analysis = {
        'total_length': len(html_content),
        'has_tables': '<table' in html_content.lower(),
        'table_count': len(re.findall(r'<table', html_content, re.IGNORECASE)),
        'has_lists': '<ul' in html_content.lower() or '<ol' in html_content.lower(),
        'list_count': len(re.findall(r'<[uo]l', html_content, re.IGNORECASE)),
        'div_count': len(re.findall(r'<div', html_content, re.IGNORECASE)),
    }
    
    # Look for potential variety-related keywords
    keywords = ['variety', 'tomato', 'days', 'fruit', 'plant', 'disease', 'resistance']
    keyword_counts = {}
    for keyword in keywords:
        keyword_counts[keyword] = len(re.findall(keyword, html_content, re.IGNORECASE))
    
    analysis['keyword_counts'] = keyword_counts
    
    return analysis

def main():
    url = "https://njaes.rutgers.edu/tomato-varieties/"
    print(f"Fetching: {url}")
    
    html_content = fetch_page(url)
    
    if not html_content:
        print("Failed to fetch the webpage")
        return
    
    print(f"Successfully fetched {len(html_content)} characters")
    
    # Analyze page structure
    analysis = analyze_page_structure(html_content)
    print("\n=== PAGE ANALYSIS ===")
    for key, value in analysis.items():
        print(f"{key}: {value}")
    
    # Extract potential variety information
    varieties = extract_basic_info(html_content)
    
    print(f"\n=== EXTRACTED VARIETIES ===")
    print(f"Found {len(varieties)} potential varieties:")
    
    for i, variety in enumerate(varieties[:10], 1):
        print(f"{i}. {variety['name']} -> {variety['url']}")
    
    # Save results
    result = {
        'analysis': analysis,
        'varieties': varieties,
        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'source_url': url,
        'total_found': len(varieties)
    }
    
    with open('tomato_analysis.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nResults saved to tomato_analysis.json")
    
    # Save a sample of the HTML for manual inspection
    with open('sample_html.txt', 'w') as f:
        f.write(html_content[:5000])  # First 5000 characters
    
    print("Sample HTML saved to sample_html.txt")

if __name__ == "__main__":
    main()