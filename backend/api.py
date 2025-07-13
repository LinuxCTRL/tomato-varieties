#!/usr/bin/env python3
"""
Tomato Varieties Database API
Flask backend for serving tomato variety data
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global variable to cache tomato data
tomato_data = None

def load_tomato_data():
    """Load tomato varieties data from JSON file"""
    global tomato_data
    
    if tomato_data is not None:
        return tomato_data
    
    try:
        if os.path.exists('tomato_varieties.json'):
            with open('tomato_varieties.json', 'r', encoding='utf-8') as f:
                tomato_data = json.load(f)
                return tomato_data
        else:
            return {
                "error": "Data file not found",
                "message": "Please run the scraper first: python scraper.py"
            }
    except Exception as e:
        return {
            "error": "Failed to load data",
            "message": str(e)
        }

@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        "message": "Tomato Varieties Database API",
        "version": "1.0",
        "endpoints": {
            "/varieties": "Get all tomato varieties",
            "/variety/<name>": "Get specific variety by name",
            "/search?q=<query>": "Search varieties",
            "/stats": "Get database statistics",
            "/refresh": "Refresh data from file",
            "/scrape": "Start scraper (POST)",
            "/scrape/status": "Check scraper status"
        }
    })

@app.route('/varieties')
def get_varieties():
    """Get all tomato varieties"""
    data = load_tomato_data()
    
    if 'error' in data:
        return jsonify(data), 500
    
    return jsonify({
        "varieties": data.get('varieties', []),
        "total_count": data.get('total_count', 0),
        "scraped_at": data.get('scraped_at', ''),
        "source": data.get('source', '')
    })

@app.route('/variety/<variety_name>')
def get_variety(variety_name):
    """Get specific variety by name"""
    data = load_tomato_data()
    
    if 'error' in data:
        return jsonify(data), 500
    
    varieties = data.get('varieties', [])
    
    # Search by name or slug
    variety = None
    for v in varieties:
        if (v.get('name', '').lower() == variety_name.lower() or 
            v.get('slug', '').lower() == variety_name.lower()):
            variety = v
            break
    
    if variety:
        return jsonify(variety)
    else:
        return jsonify({
            "error": "Variety not found",
            "message": f"No variety found with name: {variety_name}"
        }), 404

@app.route('/search')
def search_varieties():
    """Search varieties by query"""
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return jsonify({
            "error": "No query provided",
            "message": "Please provide a search query using ?q=<query>"
        }), 400
    
    data = load_tomato_data()
    
    if 'error' in data:
        return jsonify(data), 500
    
    varieties = data.get('varieties', [])
    results = []
    
    for variety in varieties:
        # Search in name, description, and characteristics
        searchable_text = ' '.join([
            variety.get('name', ''),
            variety.get('description', ''),
            ' '.join(variety.get('characteristics', {}).values()),
            ' '.join(variety.get('growing_info', {}).values())
        ]).lower()
        
        if query in searchable_text:
            results.append(variety)
    
    return jsonify({
        "query": query,
        "results": results,
        "total_results": len(results),
        "searched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/stats')
def get_stats():
    """Get database statistics"""
    data = load_tomato_data()
    
    if 'error' in data:
        return jsonify(data), 500
    
    varieties = data.get('varieties', [])
    
    # Calculate statistics
    stats = {
        "total_varieties": len(varieties),
        "scraped_at": data.get('scraped_at', ''),
        "source": data.get('source', ''),
        "characteristics_stats": {},
        "growing_info_stats": {}
    }
    
    # Count characteristics
    char_counts = {}
    growing_counts = {}
    
    for variety in varieties:
        # Count characteristics
        for key in variety.get('characteristics', {}).keys():
            char_counts[key] = char_counts.get(key, 0) + 1
        
        # Count growing info
        for key in variety.get('growing_info', {}).keys():
            growing_counts[key] = growing_counts.get(key, 0) + 1
    
    stats['characteristics_stats'] = char_counts
    stats['growing_info_stats'] = growing_counts
    
    return jsonify(stats)

@app.route('/refresh')
def refresh_data():
    """Refresh the tomato data by reloading from file"""
    global tomato_data
    tomato_data = None  # Clear cache

    data = load_tomato_data()

    if 'error' in data:
        return jsonify(data), 500

    return jsonify({
        "message": "Data refreshed successfully",
        "total_varieties": len(data.get('varieties', [])),
        "refreshed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/scrape", methods=["POST"])
def start_scraper():
    """Start the scraper to fetch fresh tomato data"""
    import subprocess
    import threading
    
    def run_scraper():
        """Run the scraper in a separate thread"""
        try:
            # Run the scraper script
            result = subprocess.run(
                ["python3", "scraper.py"], 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print("Scraper completed successfully!")
                print(f"Output: {result.stdout}")
            else:
                print("Scraper failed!")
                print(f"Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("Scraper timed out after 5 minutes")
        except Exception as e:
            print(f"Error running scraper: {e}")
    
    # Start scraper in background thread
    scraper_thread = threading.Thread(target=run_scraper)
    scraper_thread.daemon = True
    scraper_thread.start()
    
    return jsonify({
        "message": "Scraper started successfully! This may take a few minutes.",
        "status": "running",
        "estimated_time": "2-5 minutes",
        "tip": "You can refresh the page to see new data when scraping is complete."
    })

@app.route("/scrape/status")
def scraper_status():
    """Check if scraper is currently running"""
    try:
        import psutil
        
        # Check if any python process is running scraper.py
        scraper_running = False
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if proc.info["name"] == "python3" and proc.info["cmdline"]:
                    if any("scraper.py" in arg for arg in proc.info["cmdline"]):
                        scraper_running = True
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return jsonify({
            "scraper_running": scraper_running,
            "status": "running" if scraper_running else "idle"
        })
    except ImportError:
        # psutil not available, return basic status
        return jsonify({
            "scraper_running": False,
            "status": "unknown",
            "note": "Install psutil for better status monitoring"
        })

if __name__ == '__main__':
    print("Starting Tomato Varieties Database API...")
    print("API will be available at: http://localhost:5000")
    print("Available endpoints:")
    print("   GET  /varieties           - All varieties")
    print("   GET  /variety/<name>      - Specific variety")
    print("   GET  /search?q=<query>    - Search varieties")
    print("   GET  /stats               - Database statistics")
    print("   GET  /refresh             - Refresh data")
    print("   POST /scrape              - Start scraper")
    print("   GET  /scrape/status       - Scraper status")
    print("")
    
    app.run(debug=True, host='0.0.0.0', port=5000)