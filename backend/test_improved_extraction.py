#!/usr/bin/env python3
"""
Test the improved data extraction on existing scraped data
"""

import json
import re

def test_improved_extraction_on_sample():
    """Test the improved extraction logic on sample raw text"""
    
    # Sample raw text that would come from a Rutgers variety page
    sample_raw_text = """
    Home Tomato Varieties A Grappoli D'Inverno
    
    Tomato Type: Heirloom
    Breed: Open Pollinated
    Origin: Italy
    Season: Early
    Leaf Type: Normal
    Plant Type: Semi-Determinate
    Plant Height: 4 ft.
    Fruit Size: 1 oz.
    Fruit Shape: Grape
    Skin Color: Red
    Flesh Color: Red
    Comments: Roma/grape (winter grape). A cherry version of 'Green Zebra'.
    
    Variety Search:
    """
    
    print("🧪 Testing Improved Extraction Logic")
    print("=" * 50)
    
    # Test the regex patterns
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
    
    characteristics = {}
    
    print("📊 Extracted characteristics:")
    for key, pattern in patterns.items():
        match = re.search(pattern, sample_raw_text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            value = re.sub(r'\s+', ' ', value).strip()
            if value and value != 'N/A' and value != '-':
                characteristics[key] = value
                print(f"   ✅ {key}: {value}")
    
    print(f"\n📈 Total characteristics extracted: {len(characteristics)}")
    
    # Test growing info mapping
    char_to_growing = {
        'plant_type': 'plant_type',
        'plant_height': 'plant_height', 
        'fruit_size': 'fruit_size',
        'fruit_shape': 'fruit_shape',
        'days_to_maturity': 'days_to_maturity',
        'season': 'season',
    }
    
    growing_info = {}
    for char_key, growing_key in char_to_growing.items():
        if char_key in characteristics:
            growing_info[growing_key] = characteristics[char_key]
    
    print(f"\n🌱 Growing info extracted:")
    for key, value in growing_info.items():
        print(f"   ✅ {key}: {value}")
    
    return characteristics, growing_info

def check_existing_data_quality():
    """Check the quality of existing scraped data"""
    
    try:
        with open('tomato_varieties.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        varieties = data.get('varieties', [])
        if not varieties:
            print("❌ No varieties found in existing data")
            return
        
        print(f"\n📊 Analyzing existing data quality ({len(varieties)} varieties):")
        print("=" * 50)
        
        # Count varieties with different types of data
        has_characteristics = 0
        has_growing_info = 0
        has_images = 0
        has_description = 0
        
        characteristic_fields = {}
        growing_info_fields = {}
        
        for variety in varieties[:100]:  # Sample first 100
            if variety.get('characteristics'):
                has_characteristics += 1
                for key in variety['characteristics'].keys():
                    characteristic_fields[key] = characteristic_fields.get(key, 0) + 1
            
            if variety.get('growing_info'):
                has_growing_info += 1
                for key in variety['growing_info'].keys():
                    growing_info_fields[key] = growing_info_fields.get(key, 0) + 1
            
            if variety.get('images'):
                has_images += 1
            
            if variety.get('description'):
                has_description += 1
        
        sample_size = min(100, len(varieties))
        print(f"📈 Data quality (sample of {sample_size} varieties):")
        print(f"   • Has characteristics: {has_characteristics}/{sample_size} ({has_characteristics/sample_size*100:.1f}%)")
        print(f"   • Has growing info: {has_growing_info}/{sample_size} ({has_growing_info/sample_size*100:.1f}%)")
        print(f"   • Has images: {has_images}/{sample_size} ({has_images/sample_size*100:.1f}%)")
        print(f"   • Has description: {has_description}/{sample_size} ({has_description/sample_size*100:.1f}%)")
        
        print(f"\n🔍 Most common characteristic fields:")
        for field, count in sorted(characteristic_fields.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {field}: {count}/{sample_size} ({count/sample_size*100:.1f}%)")
        
        print(f"\n🌱 Most common growing info fields:")
        for field, count in sorted(growing_info_fields.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {field}: {count}/{sample_size} ({count/sample_size*100:.1f}%)")
        
        # Show a sample variety with the most data
        best_variety = None
        best_score = 0
        
        for variety in varieties[:50]:
            score = len(variety.get('characteristics', {})) + len(variety.get('growing_info', {}))
            if score > best_score:
                best_score = score
                best_variety = variety
        
        if best_variety:
            print(f"\n🏆 Best variety example: {best_variety['name']}")
            print(f"   • Characteristics: {len(best_variety.get('characteristics', {}))}")
            print(f"   • Growing info: {len(best_variety.get('growing_info', {}))}")
            if best_variety.get('characteristics'):
                print("   • Sample characteristics:")
                for key, value in list(best_variety['characteristics'].items())[:5]:
                    print(f"     - {key}: {value}")
        
    except FileNotFoundError:
        print("❌ tomato_varieties.json not found. Run the scraper first.")
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")

if __name__ == "__main__":
    # Test the improved extraction logic
    test_improved_extraction_on_sample()
    
    # Check existing data quality
    check_existing_data_quality()
    
    print(f"\n💡 Recommendations:")
    print(f"   1. Run the improved scraper to get better data extraction")
    print(f"   2. The new regex patterns should capture more structured data")
    print(f"   3. Use: python scraper.py 4 10  (to test with 4 threads, 10 varieties)")
    print(f"   4. Compare the results with the current data")