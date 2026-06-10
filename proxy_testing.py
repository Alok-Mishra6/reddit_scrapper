"""
Proxy Tester - Test if your proxies work
=========================================

This script tests your proxies to see which ones work before using them
in the Reddit scraper.

Usage:
    python test_proxies.py
"""


import requests
import time
import json
from datetime import datetime
from typing import List,Tuple



def test_proxy(proxy: str, timeout: int = 10) -> Tuple[bool, float, str]:
    """
    Test a single proxy
    
    Args:
        proxy: Proxy URL (format: http://ip:port)
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (is_working, response_time, info)
    """
    # Use httpbin.org to test - it returns your IP address
    test_url = 'http://httpbin.org/ip'
    
    try:
        start_time = time.time()
        
        response = requests.get(
            test_url,
            proxies={'http': proxy, 'https': proxy},
            timeout=timeout
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            ip = response.json().get('origin', 'unknown')
            return True, response_time, ip
        else:
            return False, 0, f'HTTP {response.status_code}'
            
    except requests.exceptions.Timeout:
        return False, 0, 'Timeout'
    except requests.exceptions.ProxyError:
        return False, 0, 'Proxy Error'
    except requests.exceptions.ConnectionError:
        return False, 0, 'Connection Error'
    except Exception as e:
        return False, 0, str(e)[:30]


def test_proxy_on_reddit(proxy: str) -> Tuple[bool, str]:
    """
    Test if proxy works specifically on Reddit
    
    Args:
        proxy: Proxy URL
    
    Returns:
        Tuple of (is_working, message)
    """
    reddit_url = 'https://www.reddit.com/r/python.json'
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(
            reddit_url,
            proxies={'http': proxy, 'https': proxy},
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            posts_count = len(data['data']['children'])
            return True, f'Got {posts_count} posts'
        elif response.status_code == 429:
            return False, 'Rate limited (429)'
        elif response.status_code == 403:
            return False, 'Forbidden (403) - blocked by Reddit'
        else:
            return False, f'HTTP {response.status_code}'
    
    except Exception as e:
        return False, str(e)[:40]


def test_all_proxies(proxies: List[str], test_reddit: bool = False):
    """
    Test a list of proxies
    
    Args:
        proxies: List of proxy URLs
        test_reddit: Also test on Reddit specifically
    """
    print(f"\n{'='*80}")
    print(f"TESTING {len(proxies)} PROXIES")
    print(f"{'='*80}\n")
    
    working = []
    failed = []
    
    for i, proxy in enumerate(proxies, 1):
        print(f"[{i}/{len(proxies)}] Testing: {proxy}")
        print(f"  General test...", end=' ')
        
        is_working, response_time, info = test_proxy(proxy)
        
        if is_working:
            print(f"✓ WORKS (IP: {info}, {response_time:.2f}s)")
            
            proxy_info = {
                'proxy': proxy,
                'response_time': response_time,
                'ip': info,
                'works_on_reddit': None
            }
            
            # Test on Reddit if requested
            if test_reddit:
                print(f"  Reddit test...", end=' ')
                reddit_works, reddit_msg = test_proxy_on_reddit(proxy)
                
                if reddit_works:
                    print(f"✓ {reddit_msg}")
                    proxy_info['works_on_reddit'] = True
                else:
                    print(f"✗ {reddit_msg}")
                    proxy_info['works_on_reddit'] = False
            
            working.append(proxy_info)
            
        else:
            print(f"✗ FAILED ({info})")
            failed.append({'proxy': proxy, 'error': info})
        
        print()  # Blank line between proxies
    
    # Print summary
    print_summary(working, failed, len(proxies))
    
    return working, failed


def print_summary(working: list, failed: list, total: int):
    """Print test summary"""
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total proxies tested: {total}")
    print(f"✓ Working: {len(working)} ({len(working)/total*100:.1f}%)")
    print(f"✗ Failed: {len(failed)} ({len(failed)/total*100:.1f}%)")
    
    if working:
        print("\n" + "="*80)
        print("WORKING PROXIES (sorted by speed)")
        print("="*80)
        
        # Sort by response time
        sorted_proxies = sorted(working, key=lambda x: x['response_time'])
        
        for i, proxy_info in enumerate(sorted_proxies, 1):
            print(f"\n{i}. {proxy_info['proxy']}")
            print(f"   IP Address: {proxy_info['ip']}")
            print(f"   Response Time: {proxy_info['response_time']:.2f} seconds")
            
            if proxy_info['works_on_reddit'] is not None:
                status = "✓ Yes" if proxy_info['works_on_reddit'] else "✗ No"
                print(f"   Works on Reddit: {status}")
        
        # Generate copy-paste ready code
        print("\n" + "="*80)
        print("COPY THIS TO YOUR SCRAPER:")
        print("="*80)
        print("\nproxies = [")
        for proxy_info in sorted_proxies:
            if proxy_info['works_on_reddit'] is False:
                print(f"    # '{proxy_info['proxy']}',  # Works generally but not on Reddit")
            else:
                print(f"    '{proxy_info['proxy']}',")
        print("]\n")
    else:
        print("\n" + "="*80)
        print("⚠️  WARNING: NO WORKING PROXIES FOUND!")
        print("="*80)
        print("\nSuggestions:")
        print("1. Try different free proxy sources")
        print("2. Use paid proxy services (Bright Data, Smartproxy, Oxylabs)")
        print("3. Run scraper without proxies (slower, higher ban risk)")
    
    print("="*80 + "\n")


def save_results(working: list, failed: list, filename: str = 'proxy_test_results.json'):
    """Save results to JSON file"""
    results = {
        'tested_at': datetime.now().isoformat(),
        'total': len(working) + len(failed),
        'working': working,
        'failed': failed
    }
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {filename}")

PROXY_FILE = "proxies.txt"

with open(PROXY_FILE, "r") as f:
        proxy_list = [line.strip() for line in f if line.strip()]

def main(proxy_list=proxy_list):
    """Main function"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                       🔍  PROXY TESTER UTILITY  🔍                         ║
║                                                                            ║
║              Test your proxies before using them in the scraper            ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Your proxies here - EDIT THIS LIST
    proxies = proxy_list

    print(f"Found {len(proxies)} proxies to test\n")
    
    # Ask if user wants to test on Reddit specifically
    test_reddit = input("Also test on Reddit specifically? (y/n): ").strip().lower() == 'y'
    
    print("\nStarting tests...")
    
    # Test all proxies
    working, failed = test_all_proxies(proxies, test_reddit=test_reddit)
    
    # Save results
    save_results(working, failed)


if __name__ == "__main__":
    main()