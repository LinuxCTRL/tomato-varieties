#!/usr/bin/env python3
"""
Multithreaded Tomato Varieties Scraper
Scrapes tomato variety data from Rutgers NJAES website using concurrent threads
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import sys

# Thread-safe printing
print_lock = threading.Lock()

def thread_safe_print(*args, **kwargs):
    """Thread-safe print function"""
    with print_lock:
        print(*args, **kwargs)

def get_tomato_variety_links(base_url):
    """Get all tomato variety names and their individual page links"""

    thread_safe_print(f"Fetching tomato variety links from: {base_url}")

    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        thread_safe_print("Main page fetched successfully!")

        # Look specifically for tomato variety links
        variety_links = []

        # First, try to find the main content area
        main_content = soup.find('main') or soup.find('div', class_='content') or soup.find('div', id='content') or soup.body

        # Look for specific patterns that indicate tomato varieties
        # Check for lists, tables, or specific containers that might hold variety links
        variety_containers = []

        # Look for common patterns in variety listing pages
        for container in main_content.find_all(['ul', 'ol', 'div', 'table', 'section']):
            container_text = container.get_text().lower()
            # If container mentions varieties, tomatoes, or has multiple links, it might contain varieties
            if ('varieties' in container_text or 'tomato' in container_text or
                len(container.find_all('a', href=True)) > 3):
                variety_containers.append(container)

        # If no specific containers found, use the main content
        if not variety_containers:
            variety_containers = [main_content]

        # Extract links from variety containers
        for container in variety_containers:
            links = container.find_all('a', href=True)

            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                # Very strict filtering for actual tomato variety names
                skip_terms = [
                    'home', 'contact', 'about', 'search', 'menu', 'login', 'register',
                    'privacy', 'terms', 'sitemap', 'rss', 'feed', 'mailto:', 'tel:',
                    'javascript:', '#', 'pdf', '.pdf', 'universitywide', 'new brunswick',
                    'school of', 'experiment station', 'rutgers', 'njaes', 'extension',
                    'faculty', 'staff', 'directory', 'programs', 'research', 'news',
                    'events', 'calendar', 'publications', 'resources', 'links', 'sebs',
                    'agricultural', 'biological sciences', 'environmental', 'new jersey'
                ]

                # Check if this looks like a tomato variety
                if (text and
                    3 <= len(text) <= 50 and  # Reasonable length for variety names
                    not any(skip in text.lower() for skip in skip_terms) and
                    not any(skip in str(href).lower() for skip in skip_terms) and
                    isinstance(href, str) and
                    not href.startswith(('mailto:', 'tel:', 'javascript:', '#')) and
                    not href.endswith(('.jpg', '.png', '.gif', '.pdf', '.doc', '.docx'))):

                    full_url = urljoin(base_url, href)

                    # Additional checks: must be a different page and contain tomato/varieties in URL
                    if (full_url != base_url and
                        full_url not in [v['url'] for v in variety_links] and
                        ('tomato' in full_url.lower() or 'varieties' in full_url.lower() or
                         full_url.startswith(base_url))):  # Or be a subpage of the base URL

                        variety_links.append({
                            'name': text,
                            'url': full_url,
                            'slug': re.sub(r'[^a-zA-Z0-9\-_]', '-', text.lower()).strip('-')
                        })

        # If still no varieties found, try a more targeted approach
        if not variety_links:
            thread_safe_print("No varieties found with container approach. Trying direct search...")

            # Look for links that might be in a specific format
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                # Look for links that contain variety-like patterns
                if (text and
                    re.match(r'^[A-Za-z][A-Za-z0-9\s\-\'\.]+$', text) and  # Alphanumeric with spaces, hyphens, apostrophes
                    3 <= len(text) <= 40 and
                    not any(word in text.lower() for word in ['university', 'rutgers', 'new jersey', 'school', 'extension']) and
                    href and 'varieties' in href.lower()):

                    full_url = urljoin(base_url, href)
                    if full_url not in [v['url'] for v in variety_links]:
                        variety_links.append({
                            'name': text,
                            'url': full_url,
                            'slug': re.sub(r'[^a-zA-Z0-9\-_]', '-', text.lower()).strip('-')
                        })

        thread_safe_print(f"Found {len(variety_links)} potential tomato variety links")

        # Debug: print first few links to see what we're getting
        if variety_links:
            thread_safe_print("Sample links found:")
            for i, variety in enumerate(variety_links[:10]):
                thread_safe_print(f"  {i+1}. '{variety['name']}' -> {variety['url']}")
        else:
            thread_safe_print("No variety links found. The page structure might be different than expected.")
            thread_safe_print("You may need to manually inspect the website structure.")
        return variety_links

    except requests.RequestException as e:
        thread_safe_print(f"Error fetching the webpage: {e}")
        return []
    except Exception as e:
        thread_safe_print(f"Error parsing the webpage: {e}")
        return []

def scrape_variety_details(variety_url, variety_name, thread_id=None):
    """Scrape detailed information from an individual tomato variety page"""

    thread_prefix = f"[Thread {thread_id}] " if thread_id else ""
    thread_safe_print(f"{thread_prefix}Scraping details for: {variety_name}")

    try:
        response = requests.get(variety_url, timeout=15)  # Increased timeout for concurrent requests
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

        # Extract main content
        content_selectors = [
            'main', '.main-content', '#main-content', '.content',
            '#content', 'article', '.article', '.post-content'
        ]

        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            main_content = soup.body or soup

        # Extract text content
        variety_details['raw_text'] = main_content.get_text(separator=' ', strip=True)

        # Look for structured data in tables
        tables = main_content.find_all('table')
        from bs4.element import Tag
        for table in tables:
            if not isinstance(table, Tag):
                continue
            rows = table.find_all('tr')
            for row in rows:
                if not isinstance(row, Tag):
                    continue
                cells = row.find_all(['td', 'th']) if isinstance(row, Tag) else []
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        variety_details['characteristics'][key] = value

        # Look for description in paragraphs
        paragraphs = main_content.find_all('p')
        if paragraphs:
            variety_details['description'] = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])

        # Extract images
        images = main_content.find_all('img')
        from bs4.element import Tag
        for img in images:
            if not isinstance(img, Tag):
                continue
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src:
                full_img_url = urljoin(variety_url, str(src))
                variety_details['images'].append({
                    'url': full_img_url,
                    'alt': alt
                })

        # Look for specific growing information
        text_lower = variety_details['raw_text'].lower()

        # Extract days to maturity
        days_match = re.search(r'(\d+)\s*days?\s*(?:to\s*)?(?:maturity|harvest)', text_lower)
        if days_match:
            variety_details['growing_info']['days_to_maturity'] = days_match.group(1)

        # Extract plant type
        if 'determinate' in text_lower:
            variety_details['growing_info']['plant_type'] = 'determinate'
        elif 'indeterminate' in text_lower:
            variety_details['growing_info']['plant_type'] = 'indeterminate'

        # Extract fruit size/weight
        weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:oz|ounce|lb|pound|g|gram)', text_lower)
        if weight_match:
            variety_details['growing_info']['fruit_weight'] = weight_match.group(0)

        thread_safe_print(f"{thread_prefix}✓ Successfully scraped: {variety_name}")
        return variety_details

    except requests.RequestException as e:
        thread_safe_print(f"{thread_prefix}✗ Error fetching variety page {variety_url}: {e}")
        return None
    except Exception as e:
        thread_safe_print(f"{thread_prefix}✗ Error parsing variety page {variety_url}: {e}")
        return None

def scrape_variety_worker(variety_link, thread_id):
    """Worker function for threading"""
    details = scrape_variety_details(variety_link['url'], variety_link['name'], thread_id)
    if details:
        details['slug'] = variety_link['slug']
        return details
    return None

def scrape_tomato_varieties_multithreaded(max_workers=5, max_varieties=None):
    """Main function to scrape all tomato varieties using multithreading"""

    base_url = "https://njaes.rutgers.edu/tomato-varieties/"

    # Step 1: Get all variety links
    thread_safe_print("Step 1: Fetching variety links...")
    variety_links = get_tomato_variety_links(base_url)

    if not variety_links:
        thread_safe_print("No variety links found!")
        return []

    # Limit varieties if specified
    if max_varieties:
        variety_links = variety_links[:max_varieties]

    thread_safe_print(f"\nFound {len(variety_links)} varieties to scrape")
    thread_safe_print(f"Using {max_workers} concurrent threads")
    thread_safe_print("Sample varieties:")
    for i, variety in enumerate(variety_links[:5]):
        thread_safe_print(f"  {i+1}. {variety['name']} -> {variety['url']}")

    # Step 2: Scrape details for each variety using ThreadPoolExecutor
    thread_safe_print(f"\nStep 2: Scraping variety details with {max_workers} threads...")
    all_varieties = []
    failed_count = 0
    
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_variety = {
            executor.submit(scrape_variety_worker, variety_link, i % max_workers + 1): variety_link 
            for i, variety_link in enumerate(variety_links)
        }

        # Process completed tasks
        for i, future in enumerate(as_completed(future_to_variety)):
            variety_link = future_to_variety[future]
            try:
                result = future.result()
                if result:
                    all_varieties.append(result)
                    thread_safe_print(f"Progress: {len(all_varieties)}/{len(variety_links)} completed ({len(all_varieties)/len(variety_links)*100:.1f}%)")
                else:
                    failed_count += 1
                    thread_safe_print(f"Failed to scrape: {variety_link['name']}")
            except Exception as exc:
                failed_count += 1
                thread_safe_print(f"Exception occurred for {variety_link['name']}: {exc}")

    end_time = time.time()
    duration = end_time - start_time

    thread_safe_print(f"\n🎉 Scraping completed!")
    thread_safe_print(f"⏱️  Total time: {duration:.2f} seconds")
    thread_safe_print(f"✅ Successfully scraped: {len(all_varieties)} varieties")
    thread_safe_print(f"❌ Failed: {failed_count} varieties")
    thread_safe_print(f"🚀 Average time per variety: {duration/len(variety_links):.2f} seconds")

    return all_varieties

def save_to_json(data, filename="tomato_varieties.json"):
    """Save the scraped data to a JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        thread_safe_print(f"Data saved to {filename}")
    except Exception as e:
        thread_safe_print(f"Error saving data: {e}")

if __name__ == "__main__":
    thread_safe_print("🍅 Starting Multithreaded Tomato Varieties Scraper...")
    
    # Configuration
    MAX_WORKERS = 8  # Number of concurrent threads
    MAX_VARIETIES = None  # Set to a number to limit varieties for testing, None for all
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        try:
            MAX_WORKERS = int(sys.argv[1])
        except ValueError:
            thread_safe_print("Invalid number of workers, using default: 8")
    
    if len(sys.argv) > 2:
        try:
            MAX_VARIETIES = int(sys.argv[2])
        except ValueError:
            thread_safe_print("Invalid max varieties, scraping all")

    thread_safe_print(f"Configuration: {MAX_WORKERS} workers, {MAX_VARIETIES or 'all'} varieties")
    
    start_total = time.time()
    varieties = scrape_tomato_varieties_multithreaded(max_workers=MAX_WORKERS, max_varieties=MAX_VARIETIES)
    end_total = time.time()

    # Save the scraped data
    result = {
        "varieties": varieties,
        "total_count": len(varieties),
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": "https://njaes.rutgers.edu/tomato-varieties/",
        "scraping_stats": {
            "total_time_seconds": round(end_total - start_total, 2),
            "workers_used": MAX_WORKERS,
            "avg_time_per_variety": round((end_total - start_total) / len(varieties), 2) if varieties else 0
        }
    }

    save_to_json(result, "tomato_varieties_multithreaded.json")
    thread_safe_print(f"\n🎉 All done! Found {len(varieties)} varieties in {end_total - start_total:.2f} seconds.")
    thread_safe_print("Data saved to 'tomato_varieties_multithreaded.json'")