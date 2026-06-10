"""
Ultimate Reddit Proxy Finder - 2026 Edition
============================================

Automatically pulls proxies from:
- 10+ GitHub repositories (updated hourly/daily)
- 5+ Free proxy APIs
- Multiple proxy scraping services
- Tests EVERYTHING on Reddit

This is the ULTIMATE solution for finding working Reddit proxies!

Usage:
    python ultimate_reddit_proxy_finder.py
    
Or with specific options:
    python ultimate_reddit_proxy_finder.py --max-test 1000 --workers 50
"""

import requests
import json
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Set
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UltimateProxyFinder:
    """The ultimate proxy finder - scrapes from ALL free sources"""
    
    def __init__(self):
        self.all_proxies = []
        self.unique_proxies = set()
        self.working_proxies = []
        self.reddit_proxies = []
        
        # GitHub repositories with free proxies (updated frequently)
        self.github_sources = {
            'TheSpeedX': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'clarketm': 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'jetkai_http': 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
            'jetkai_https': 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt',
            'jetkai_socks4': 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt',
            'jetkai_socks5': 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt',
            'monosans_http': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'monosans_socks4': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
            'monosans_socks5': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
            'ErcinDedeoglu_http': 'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt',
            'ErcinDedeoglu_https': 'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt',
            'ErcinDedeoglu_socks4': 'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt',
            'ErcinDedeoglu_socks5': 'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt',
            'vakhov_http': 'https://vakhov.github.io/fresh-proxy-list/http.txt',
            'vakhov_https': 'https://vakhov.github.io/fresh-proxy-list/https.txt',
            'vakhov_socks4': 'https://vakhov.github.io/fresh-proxy-list/socks4.txt',
            'vakhov_socks5': 'https://vakhov.github.io/fresh-proxy-list/socks5.txt',
            'KangProxy': 'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/xResults/Proxies.txt',
            'Proxifly_all': 'https://raw.githubusercontent.com/Proxifly/free-proxy-list/main/proxies/all/data.txt',
            'Proxifly_http': 'https://raw.githubusercontent.com/Proxifly/free-proxy-list/main/proxies/http/data.txt',
        }
        
        # API endpoints for proxy lists
        self.api_sources = [
            'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
            'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all',
            'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://www.proxy-list.download/api/v1/get?type=https',
            'https://www.proxy-list.download/api/v1/get?type=socks4',
            'https://www.proxy-list.download/api/v1/get?type=socks5',
        ]
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_github_source(self, name: str, url: str) -> int:
        """Scrape proxies from a GitHub raw file"""
        try:
            logger.info(f"Fetching from {name}...")
            response = requests.get(url, timeout=15, headers=self.headers)
            
            if response.status_code != 200:
                logger.warning(f"  ✗ {name}: HTTP {response.status_code}")
                return 0
            
            count = 0
            for line in response.text.strip().split('\n'):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Handle different formats
                if ':' in line:
                    # Extract IP:PORT
                    parts = line.split()
                    proxy_part = parts[0] if parts else line
                    
                    if ':' in proxy_part:
                        # Add protocol if missing
                        if not proxy_part.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
                            # Guess protocol from source name
                            if 'socks5' in name.lower():
                                proxy_part = f'socks5://{proxy_part}'
                            elif 'socks4' in name.lower():
                                proxy_part = f'socks4://{proxy_part}'
                            elif 'https' in name.lower():
                                proxy_part = f'https://{proxy_part}'
                            else:
                                proxy_part = f'http://{proxy_part}'
                        
                        if proxy_part not in self.unique_proxies:
                            self.unique_proxies.add(proxy_part)
                            self.all_proxies.append({
                                'proxy': proxy_part,
                                'source': name
                            })
                            count += 1
            
            logger.info(f"  ✓ {name}: {count} new proxies")
            return count
        
        except Exception as e:
            logger.error(f"  ✗ {name}: {e}")
            return 0
    
    def scrape_api_source(self, url: str) -> int:
        """Scrape proxies from an API endpoint"""
        try:
            source_name = url.split('/')[2]  # Extract domain
            logger.info(f"Fetching from API: {source_name}...")
            
            response = requests.get(url, timeout=15, headers=self.headers)
            
            if response.status_code != 200:
                logger.warning(f"  ✗ {source_name}: HTTP {response.status_code}")
                return 0
            
            count = 0
            
            # Try JSON first
            try:
                data = response.json()
                
                # Handle Geonode format
                if isinstance(data, dict) and 'data' in data:
                    for item in data['data']:
                        ip = item.get('ip')
                        port = item.get('port')
                        protocols = item.get('protocols', ['http'])
                        
                        if ip and port:
                            for protocol in protocols:
                                proxy = f"{protocol}://{ip}:{port}"
                                if proxy not in self.unique_proxies:
                                    self.unique_proxies.add(proxy)
                                    self.all_proxies.append({
                                        'proxy': proxy,
                                        'source': f'{source_name}_api'
                                    })
                                    count += 1
            
            except json.JSONDecodeError:
                # Plain text format
                for line in response.text.strip().split('\n'):
                    line = line.strip()
                    if line and ':' in line:
                        if not line.startswith(('http://', 'https://', 'socks')):
                            # Guess protocol from URL
                            if 'socks5' in url:
                                line = f'socks5://{line}'
                            elif 'socks4' in url:
                                line = f'socks4://{line}'
                            elif 'https' in url:
                                line = f'https://{line}'
                            else:
                                line = f'http://{line}'
                        
                        if line not in self.unique_proxies:
                            self.unique_proxies.add(line)
                            self.all_proxies.append({
                                'proxy': line,
                                'source': f'{source_name}_api'
                            })
                            count += 1
            
            logger.info(f"  ✓ {source_name}: {count} new proxies")
            return count
        
        except Exception as e:
            logger.error(f"  ✗ API error: {e}")
            return 0
    
    def scrape_all_sources(self):
        """Scrape proxies from all sources"""
        logger.info("="*80)
        logger.info("SCRAPING PROXIES FROM ALL SOURCES")
        logger.info("="*80)
        
        total_from_github = 0
        total_from_apis = 0
        
        # Scrape GitHub sources
        logger.info("\n📦 Scraping GitHub repositories...")
        for name, url in self.github_sources.items():
            count = self.scrape_github_source(name, url)
            total_from_github += count
            time.sleep(0.5)  # Be nice to GitHub
        
        # Scrape API sources
        logger.info("\n🌐 Scraping API endpoints...")
        for url in self.api_sources:
            count = self.scrape_api_source(url)
            total_from_apis += count
            time.sleep(1)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"SCRAPING COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"From GitHub: {total_from_github}")
        logger.info(f"From APIs: {total_from_apis}")
        logger.info(f"Total unique proxies: {len(self.all_proxies)}")
        logger.info(f"{'='*80}\n")
        
        return self.all_proxies
    
    def test_single_proxy(self, proxy_info: Dict) -> Dict:
        """Test a single proxy on Reddit"""
        proxy = proxy_info['proxy']
        
        result = {
            **proxy_info,
            'working': False,
            'speed': 999,
            'works_on_reddit': False,
            'reddit_status': 'not_tested'
        }
        
        # Create proxy dict
        proxies = {
            'http': proxy,
            'https': proxy
        }
        
        try:
            # Test 1: Basic connectivity
            start = time.time()
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                timeout=10,
                headers=self.headers
            )
            basic_time = time.time() - start
            
            if response.status_code != 200:
                return result
            
            result['working'] = True
            result['speed'] = basic_time
            
            # Test 2: Reddit
            time.sleep(0.3)
            start = time.time()
            reddit_response = requests.get(
                'https://www.reddit.com/r/python.json',
                proxies=proxies,
                headers=self.headers,
                timeout=15
            )
            reddit_time = time.time() - start
            
            if reddit_response.status_code == 200:
                try:
                    data = reddit_response.json()
                    if 'data' in data and 'children' in data.get('data', {}):
                        result['works_on_reddit'] = True
                        result['reddit_status'] = 'success'
                        result['speed'] = reddit_time
                except:
                    result['reddit_status'] = 'invalid_json'
            
            elif reddit_response.status_code == 403:
                result['reddit_status'] = 'blocked'
            elif reddit_response.status_code == 429:
                result['reddit_status'] = 'rate_limited'
            else:
                result['reddit_status'] = f'http_{reddit_response.status_code}'
        
        except requests.exceptions.Timeout:
            result['reddit_status'] = 'timeout'
        except requests.exceptions.ProxyError:
            result['reddit_status'] = 'proxy_error'
        except Exception as e:
            result['reddit_status'] = f'error'
        
        return result
    
    def test_all_proxies(self, max_workers: int = 50, max_test: int = None):
        """Test all proxies in parallel"""
        
        proxies_to_test = self.all_proxies[:max_test] if max_test else self.all_proxies
        
        logger.info("="*80)
        logger.info(f"TESTING {len(proxies_to_test)} PROXIES ON REDDIT")
        logger.info("="*80)
        logger.info(f"Workers: {max_workers}")
        logger.info(f"Estimated time: {len(proxies_to_test) * 15 / max_workers / 60:.1f} minutes")
        logger.info("="*80 + "\n")
        
        working_count = 0
        reddit_count = 0
        status_counts = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.test_single_proxy, p): p 
                for p in proxies_to_test
            }
            
            for i, future in enumerate(as_completed(future_to_proxy), 1):
                result = future.result()
                
                status = result['reddit_status']
                status_counts[status] = status_counts.get(status, 0) + 1
                
                if result['working']:
                    self.working_proxies.append(result)
                    working_count += 1
                    
                    if result['works_on_reddit']:
                        self.reddit_proxies.append(result)
                        reddit_count += 1
                        logger.info(f"[{i}/{len(proxies_to_test)}] 🎉 {result['proxy'][:50]} - REDDIT WORKS ({result['speed']:.2f}s)")
                
                # Progress update every 100
                if i % 100 == 0:
                    logger.info(f"Progress: {i}/{len(proxies_to_test)} | Working: {working_count} | Reddit: {reddit_count}")
        
        # Sort by speed
        self.reddit_proxies.sort(key=lambda x: x['speed'])
        
        logger.info(f"\n{'='*80}")
        logger.info("TEST COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Total tested: {len(proxies_to_test)}")
        logger.info(f"Working (basic): {working_count} ({working_count/len(proxies_to_test)*100:.1f}%)")
        logger.info(f"✅ REDDIT-COMPATIBLE: {reddit_count} ({reddit_count/len(proxies_to_test)*100:.1f}%)")
        logger.info(f"\nTop failure reasons:")
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"  {status}: {count}")
        logger.info(f"{'='*80}\n")
        
        return self.reddit_proxies
    
    def save_results(self):
        """Save results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if self.reddit_proxies:
            # JSON format
            json_file = f'reddit_proxies_{timestamp}.json'
            with open(json_file, 'w') as f:
                json.dump(self.reddit_proxies, f, indent=2)
            logger.info(f"✓ Saved JSON: {json_file}")
            
            # Python list
            py_file = f'reddit_proxies_{timestamp}.py'
            with open(py_file, 'w') as f:
                f.write(f"# Reddit-compatible proxies - {datetime.now().isoformat()}\n")
                f.write(f"# Found {len(self.reddit_proxies)} working proxies\n\n")
                f.write("REDDIT_PROXIES = [\n")
                for p in self.reddit_proxies:
                    f.write(f"    '{p['proxy']}',  # {p['speed']:.2f}s | {p['source']}\n")
                f.write("]\n")
            logger.info(f"✓ Saved Python: {py_file}")
            
            # Plain text
            txt_file = f'reddit_proxies_{timestamp}.txt'
            with open(txt_file, 'w') as f:
                for p in self.reddit_proxies:
                    f.write(f"{p['proxy']}\n")
            logger.info(f"✓ Saved TXT: {txt_file}")
            
            logger.info(f"\n🎉 SUCCESS! {len(self.reddit_proxies)} Reddit proxies saved!")
        
        else:
            logger.warning("\n⚠️  No Reddit-compatible proxies found")
            
            if self.working_proxies:
                logger.info(f"But {len(self.working_proxies)} proxies work for basic connections")
    
    def print_summary(self):
        """Print summary"""
        logger.info("\n" + "="*80)
        logger.info("FINAL SUMMARY")
        logger.info("="*80)
        
        if self.reddit_proxies:
            logger.info(f"\n🎉 {len(self.reddit_proxies)} REDDIT-COMPATIBLE PROXIES FOUND!\n")
            
            for i, p in enumerate(self.reddit_proxies[:10], 1):
                logger.info(f"{i}. {p['proxy']}")
                logger.info(f"   Speed: {p['speed']:.2f}s | Source: {p['source']}")
            
            if len(self.reddit_proxies) > 10:
                logger.info(f"\n... and {len(self.reddit_proxies) - 10} more in the saved files!")
            
            logger.info(f"\n{'='*80}")
            logger.info("NEXT STEPS:")
            logger.info("="*80)
            logger.info(f"""
1. Use the proxies from the saved .txt or .py file
2. Rotate between them (don't reuse same proxy)  
3. Add 10-15 second delays between requests
4. Monitor for blocks (403/429 errors)
5. Run this script daily for fresh proxies
            """)
        else:
            logger.info("\n❌ No Reddit-compatible proxies found this time.")
            logger.info("\nTry:")
            logger.info("1. Run again (proxies change frequently)")
            logger.info("2. Increase --max-test to test more proxies")
            logger.info("3. Consider paid proxies (Webshare.io, Bright Data)")
        
        logger.info("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Ultimate Reddit Proxy Finder - Scrapes from 20+ sources'
    )
    parser.add_argument(
        '--max-test',
        type=int,
        default=None,
        help='Maximum number of proxies to test (default: all)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=50,
        help='Number of parallel workers (default: 50)'
    )
    
    args = parser.parse_args()
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          🚀 ULTIMATE REDDIT PROXY FINDER - 2026 EDITION 🚀                 ║
║                                                                            ║
║  Scrapes from:                                                             ║
║  • 20+ GitHub repositories                                                 ║
║  • 7+ Free proxy APIs                                                      ║
║  • Tests everything on Reddit                                              ║
║  • Saves only working proxies                                              ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    finder = UltimateProxyFinder()
    
    # Step 1: Scrape all sources
    finder.scrape_all_sources()
    
    if not finder.all_proxies:
        logger.error("❌ No proxies found from any source!")
        return
    
    # Ask user
    test_limit = args.max_test or len(finder.all_proxies)
    logger.info(f"\nFound {len(finder.all_proxies)} total proxies")
    logger.info(f"Will test {test_limit} proxies")
    logger.info(f"Using {args.workers} parallel workers")
    logger.info(f"Estimated time: {test_limit * 15 / args.workers / 60:.1f} minutes\n")
    
    response = input("Start testing? [Y/n]: ").strip().lower()
    if response and response not in ['y', 'yes']:
        logger.info("Cancelled.")
        return
    
    # Step 2: Test proxies
    finder.test_all_proxies(max_workers=args.workers, max_test=args.max_test)
    
    # Step 3: Save results
    finder.save_results()
    
    # Step 4: Print summary
    finder.print_summary()


if __name__ == "__main__":
    main()