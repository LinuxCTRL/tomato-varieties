#!/usr/bin/env python3
"""
Test script to compare performance between single-threaded and multithreaded scraping
"""

import time
import sys
import os

# Add current directory to path to import our scrapers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_multithreaded_scraper():
    """Test the multithreaded scraper with different configurations"""
    
    print("🧪 Testing Multithreaded Scraper Performance")
    print("=" * 50)
    
    # Test with different thread counts
    thread_counts = [1, 4, 8, 12]
    max_test_varieties = 10  # Limit for testing
    
    results = {}
    
    for thread_count in thread_counts:
        print(f"\n🔧 Testing with {thread_count} threads...")
        print("-" * 30)
        
        # Import here to avoid issues if module doesn't exist
        try:
            from scraper import scrape_tomato_varieties_multithreaded
            
            start_time = time.time()
            varieties = scrape_tomato_varieties_multithreaded(
                max_workers=thread_count, 
                max_varieties=max_test_varieties
            )
            end_time = time.time()
            
            duration = end_time - start_time
            results[thread_count] = {
                'duration': duration,
                'varieties_count': len(varieties),
                'avg_per_variety': duration / len(varieties) if varieties else 0
            }
            
            print(f"✅ Completed in {duration:.2f} seconds")
            print(f"📊 Scraped {len(varieties)} varieties")
            print(f"⚡ Average: {duration/len(varieties):.2f} seconds per variety")
            
        except ImportError as e:
            print(f"❌ Could not import scraper: {e}")
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
    
    # Print summary
    if results:
        print("\n📈 PERFORMANCE SUMMARY")
        print("=" * 50)
        print(f"{'Threads':<8} {'Time (s)':<10} {'Varieties':<10} {'Avg/Variety':<12} {'Speedup':<8}")
        print("-" * 50)
        
        baseline_time = results.get(1, {}).get('duration', 0)
        
        for threads, data in results.items():
            speedup = baseline_time / data['duration'] if data['duration'] > 0 else 0
            print(f"{threads:<8} {data['duration']:<10.2f} {data['varieties_count']:<10} "
                  f"{data['avg_per_variety']:<12.2f} {speedup:<8.2f}x")
        
        # Find optimal thread count
        best_threads = min(results.keys(), key=lambda x: results[x]['duration'])
        best_time = results[best_threads]['duration']
        print(f"\n🏆 Best performance: {best_threads} threads ({best_time:.2f}s)")

def show_usage_examples():
    """Show usage examples for the multithreaded scraper"""
    
    print("\n📚 USAGE EXAMPLES")
    print("=" * 50)
    
    examples = [
        {
            'title': 'Basic usage (8 threads, all varieties)',
            'command': 'python scraper.py'
        },
        {
            'title': 'Custom thread count (12 threads)',
            'command': 'python scraper.py 12'
        },
        {
            'title': 'Limited varieties for testing (4 threads, 20 varieties)',
            'command': 'python scraper.py 4 20'
        },
        {
            'title': 'Single-threaded (for comparison)',
            'command': 'python scraper.py 1'
        },
        {
            'title': 'High concurrency (16 threads)',
            'command': 'python scraper.py 16'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print(f"   {example['command']}")
    
    print(f"\n💡 TIPS:")
    print(f"   • Start with 4-8 threads for most systems")
    print(f"   • Too many threads may overwhelm the server")
    print(f"   • Monitor your network connection during scraping")
    print(f"   • Results are saved to 'tomato_varieties_multithreaded.json'")

if __name__ == "__main__":
    print("🍅 Tomato Scraper Performance Tester")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_multithreaded_scraper()
    else:
        show_usage_examples()
        
        print(f"\n🚀 To run performance tests:")
        print(f"   python test_scraper_performance.py --test")
        
        print(f"\n🏃 To run the multithreaded scraper now:")
        print(f"   python scraper.py")