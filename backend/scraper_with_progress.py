#!/usr/bin/env python3
"""
Multithreaded Tomato Varieties Scraper with Beautiful Progress Bars
Scrapes tomato variety data from Rutgers NJAES website using concurrent threads and tqdm
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from tqdm import tqdm

def get_tomato_variety_links(base_url):
    """Get all tomato variety names and their individual page links"""

    print(f"🔍 Fetching tomato variety links from: {base_url}")

    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        print("✅ Main page fetched successfully!")

        # Look specifically for tomato variety links
        variety_links = []

        # First, try to find the main content area
        main_content = soup.find('main') or soup.find('div', class_='content') or soup.find('div', id='content') or soup.body

        # Look for specific patterns that indicate tomato varieties
        variety_containers = []

        # Look for common patterns in variety listing pages
        for container in main_content.find_all(['ul', 'ol', 'div', 'table', 'section']):
            container_text = container.get_text().lower()
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
                    3 <= len(text) <= 50 and
                    not any(skip in text.lower() for skip in skip_terms) and
                    not any(skip in str(href).lower() for skip in skip_terms) and
                    isinstance(href, str) and
                    not href.startswith(('mailto:', 'tel:', 'javascript:', '#')) and
                    not href.endswith(('.jpg', '.png', '.gif', '.pdf', '.doc', '.docx'))):

                    full_url = urljoin(base_url, href)

                    if (full_url != base_url and
                        full_url not in [v['url'] for v in variety_links] and
                        ('tomato' in full_url.lower() or 'varieties' in full_url.lower() or
                         full_url.startswith(base_url))):

                        variety_links.append({
                            'name': text,
                            'url': full_url,
                            'slug': re.sub(r'[^a-zA-Z0-9\-_]', '-', text.lower()).strip('-')
                        })

        # If still no varieties found, try a more targeted approach
        if not variety_links:
            print("🔄 No varieties found with container approach. Trying direct search...")

            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                if (text and
                    re.match(r'^[A-Za-z][A-Za-z0-9\s\-\'\.]+$', text) and
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

        print(f"📊 Found {len(variety_links)} potential tomato variety links")
        return variety_links

    except requests.RequestException as e:
        print(f"❌ Error fetching the webpage: {e}")
        return []
    except Exception as e:
        print(f"❌ Error parsing the webpage: {e}")
        return []

def scrape_variety_details(variety_url, variety_name, pbar=None):
    """Scrape detailed information from an individual tomato variety page"""

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

        # Update progress bar if provided
        if pbar:
            pbar.set_postfix_str(f"✅ {variety_name[:20]}...")
            
        return variety_details

    except requests.RequestException as e:
        if pbar:
            pbar.set_postfix_str(f"❌ Network error: {variety_name[:15]}...")
        return None
    except Exception as e:
        if pbar:
            pbar.set_postfix_str(f"❌ Parse error: {variety_name[:15]}...")
        return None

def scrape_variety_worker(variety_link, pbar=None):
    """Worker function for threading"""
    details = scrape_variety_details(variety_link['url'], variety_link['name'], pbar)
    if details:
        details['slug'] = variety_link['slug']
        return details
    return None

def scrape_tomato_varieties_with_progress(max_workers=8, max_varieties=None):
    """Main function to scrape all tomato varieties using multithreading with progress bars"""

    base_url = "https://njaes.rutgers.edu/tomato-varieties/"

    print("🍅 Tomato Varieties Scraper with Progress Bars")
    print("=" * 50)

    # Step 1: Get all variety links
    variety_links = get_tomato_variety_links(base_url)

    if not variety_links:
        print("❌ No variety links found!")
        return []

    # Limit varieties if specified
    if max_varieties:
        variety_links = variety_links[:max_varieties]
        print(f"🔧 Limited to {max_varieties} varieties for testing")

    print(f"📋 Found {len(variety_links)} varieties to scrape")
    print(f"🧵 Using {max_workers} concurrent threads")
    
    # Show sample varieties
    if variety_links:
        print("\n📝 Sample varieties:")
        for i, variety in enumerate(variety_links[:3]):
            print(f"   {i+1}. {variety['name']}")
        if len(variety_links) > 3:
            print(f"   ... and {len(variety_links) - 3} more")

    print(f"\n🚀 Starting scraping process...")
    
    # Step 2: Scrape details with beautiful progress bar
    all_varieties = []
    failed_count = 0
    
    start_time = time.time()

    # Create main progress bar
    with tqdm(
        total=len(variety_links),
        desc="🍅 Scraping varieties",
        unit="variety",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}",
        colour="green",
        dynamic_ncols=True
    ) as pbar:
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_variety = {
                executor.submit(scrape_variety_worker, variety_link, pbar): variety_link 
                for variety_link in variety_links
            }

            # Process completed tasks
            for future in as_completed(future_to_variety):
                variety_link = future_to_variety[future]
                try:
                    result = future.result()
                    if result:
                        all_varieties.append(result)
                        pbar.set_postfix_str(f"✅ Success: {len(all_varieties)} | ❌ Failed: {failed_count}")
                    else:
                        failed_count += 1
                        pbar.set_postfix_str(f"✅ Success: {len(all_varieties)} | ❌ Failed: {failed_count}")
                except Exception as exc:
                    failed_count += 1
                    pbar.set_postfix_str(f"✅ Success: {len(all_varieties)} | ❌ Failed: {failed_count}")
                
                # Update progress bar
                pbar.update(1)

    end_time = time.time()
    duration = end_time - start_time

    # Final summary
    print(f"\n🎉 Scraping completed!")
    print("=" * 50)
    print(f"⏱️  Total time: {duration:.2f} seconds")
    print(f"✅ Successfully scraped: {len(all_varieties)} varieties")
    print(f"❌ Failed: {failed_count} varieties")
    print(f"🚀 Average time per variety: {duration/len(variety_links):.2f} seconds")
    print(f"📈 Success rate: {len(all_varieties)/len(variety_links)*100:.1f}%")

    return all_varieties

def save_to_json(data, filename="tomato_varieties.json"):
    """Save the scraped data to a JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Data saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving data: {e}")

if __name__ == "__main__":
    print("🍅 Starting Beautiful Tomato Varieties Scraper...")
    
    # Configuration
    MAX_WORKERS = 8  # Number of concurrent threads
    MAX_VARIETIES = None  # Set to a number to limit varieties for testing, None for all
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        try:
            MAX_WORKERS = int(sys.argv[1])
            print(f"🔧 Using {MAX_WORKERS} threads from command line")
        except ValueError:
            print("⚠️  Invalid number of workers, using default: 8")
    
    if len(sys.argv) > 2:
        try:
            MAX_VARIETIES = int(sys.argv[2])
            print(f"🔧 Limiting to {MAX_VARIETIES} varieties from command line")
        except ValueError:
            print("⚠️  Invalid max varieties, scraping all")

    start_total = time.time()
    varieties = scrape_tomato_varieties_with_progress(max_workers=MAX_WORKERS, max_varieties=MAX_VARIETIES)
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
            "avg_time_per_variety": round((end_total - start_total) / len(varieties), 2) if varieties else 0,
            "success_rate": round(len(varieties) / len(varieties) * 100, 1) if varieties else 0
        }
    }

    save_to_json(result, "tomato_varieties_beautiful.json")
    print(f"\n🎊 All done! Scraped {len(varieties)} varieties in {end_total - start_total:.2f} seconds.")