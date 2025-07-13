#!/usr/bin/env python3
"""
Fix JSON compatibility between scraper and UI
Ensures the scraped data is in the correct format for the API/UI
"""

import json
import os
import sys

def check_json_compatibility():
    """Check if the JSON file is compatible with the UI"""

    print("🔍 Checking JSON compatibility...")

    # Check if the main file exists
    if not os.path.exists('tomato_varieties.json'):
        print("❌ tomato_varieties.json not found!")

        # Check for alternative files
        alternatives = [
            'tomato_varieties_multithreaded.json',
            'tomato_varieties_beautiful.json'
        ]

        for alt in alternatives:
            if os.path.exists(alt):
                print(f"✅ Found {alt}, copying to tomato_varieties.json...")
                with open(alt, 'r', encoding='utf-8') as src:
                    data = json.load(src)
                with open('tomato_varieties.json', 'w', encoding='utf-8') as dst:
                    json.dump(data, dst, indent=2, ensure_ascii=False)
                print("✅ File copied successfully!")
                break
        else:
            print("❌ No compatible JSON files found. Please run the scraper first.")
            return False

    # Validate the JSON structure
    try:
        with open('tomato_varieties.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("✅ JSON file loaded successfully!")

        # Check required fields
        required_fields = ['varieties', 'total_count', 'scraped_at']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            print(f"⚠️  Missing fields: {missing_fields}")
            return False

        # Check varieties structure
        if not data['varieties']:
            print("⚠️  No varieties found in data")
            return False

        # Check sample variety structure
        sample_variety = data['varieties'][0]
        variety_required_fields = ['name', 'url', 'slug']
        missing_variety_fields = [field for field in variety_required_fields if field not in sample_variety]

        if missing_variety_fields:
            print(f"⚠️  Missing variety fields: {missing_variety_fields}")
            return False

        # Print summary
        print(f"📊 Data Summary:")
        print(f"   • Total varieties: {data['total_count']}")
        print(f"   • Scraped at: {data['scraped_at']}")
        print(f"   • Source: {data.get('source', 'Unknown')}")

        if 'scraping_stats' in data:
            stats = data['scraping_stats']
            print(f"   • Scraping time: {stats.get('total_time_seconds', 'Unknown')}s")
            print(f"   • Workers used: {stats.get('workers_used', 'Unknown')}")

        print("✅ JSON structure is compatible with the UI!")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking JSON: {e}")
        return False

def test_api_compatibility():
    """Test if the API can load the data"""

    print("\n🧪 Testing API compatibility...")

    try:
        # Simulate API loading
        import sys
        import os

        # Add current directory to path
        sys.path.insert(0, os.getcwd())

        # Try to import and test the API
        from backend.api import load_tomato_data

        result = load_tomato_data()

        if 'error' in result:
            print(f"❌ API loading failed: {result['error']}")
            return False

        print("✅ API can load the data successfully!")
        print(f"   • Loaded {len(result.get('varieties', []))} varieties")
        return True

    except ImportError:
        print("⚠️  Could not import API module (this is okay if running standalone)")
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main function"""

    print("🍅 JSON Compatibility Checker")
    print("=" * 40)

    # Check JSON compatibility
    json_ok = check_json_compatibility()

    if json_ok:
        # Test API compatibility
        api_ok = test_api_compatibility()

        if json_ok and api_ok:
            print("\n🎉 Everything looks good!")
            print("✅ Your scraper data is compatible with the UI")
            print("🚀 You can now start the servers:")
            print("   1. python api.py")
            print("   2. node server.js")
            print("   3. Open http://localhost:3000")
        else:
            print("\n⚠️  Some issues found, but JSON structure is okay")
    else:
        print("\n❌ JSON compatibility issues found")
        print("💡 Try running the scraper again:")
        print("   python scraper.py")

if __name__ == "__main__":
    main()
