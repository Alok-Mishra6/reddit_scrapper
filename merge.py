"""
Proxy File Merger & Deduplicator
=================================

Merges multiple proxy JSON files and removes duplicates.
Keeps the best version of each proxy (fastest speed).

Usage:
    python merge_proxies.py
    
Or specify files:
    python merge_proxies.py file1.json file2.json file3.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class ProxyMerger:
    """Merge and deduplicate proxy files"""
    
    def __init__(self):
        self.all_proxies = []
        self.unique_proxies = {}
        self.stats = {
            'total_loaded': 0,
            'duplicates_removed': 0,
            'unique_count': 0,
            'files_processed': 0
        }
    
    def load_json_file(self, filepath: str) -> List[Dict]:
        """Load proxies from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Handle both list and single dict
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                print(f"  ⚠️  Warning: {filepath} has unexpected format")
                return []
        
        except FileNotFoundError:
            print(f"  ❌ File not found: {filepath}")
            return []
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON in {filepath}: {e}")
            return []
        except Exception as e:
            print(f"  ❌ Error loading {filepath}: {e}")
            return []
    
    def merge_files(self, filepaths: List[str]):
        """Merge multiple proxy files"""
        print("="*80)
        print("LOADING PROXY FILES")
        print("="*80)
        
        for filepath in filepaths:
            print(f"\n📂 Loading: {filepath}")
            proxies = self.load_json_file(filepath)
            
            if proxies:
                print(f"  ✓ Found {len(proxies)} proxies")
                self.all_proxies.extend(proxies)
                self.stats['total_loaded'] += len(proxies)
                self.stats['files_processed'] += 1
            else:
                print(f"  ⚠️  No proxies loaded from this file")
        
        print(f"\n{'='*80}")
        print(f"Total proxies loaded: {self.stats['total_loaded']}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"{'='*80}\n")
    
    def deduplicate(self):
        """Remove duplicates, keeping the best version (fastest)"""
        print("="*80)
        print("DEDUPLICATING PROXIES")
        print("="*80)
        
        for proxy_data in self.all_proxies:
            proxy_url = proxy_data.get('proxy')
            
            if not proxy_url:
                continue
            
            # If this proxy hasn't been seen, add it
            if proxy_url not in self.unique_proxies:
                self.unique_proxies[proxy_url] = proxy_data
            else:
                # Proxy exists - keep the faster one
                existing_speed = self.unique_proxies[proxy_url].get('speed', 999)
                new_speed = proxy_data.get('speed', 999)
                
                if new_speed < existing_speed:
                    # New one is faster, replace
                    self.unique_proxies[proxy_url] = proxy_data
                    print(f"  ⚡ Updated (faster): {proxy_url[:50]} - {new_speed:.2f}s < {existing_speed:.2f}s")
                
                self.stats['duplicates_removed'] += 1
        
        self.stats['unique_count'] = len(self.unique_proxies)
        
        print(f"\n{'='*80}")
        print(f"Duplicates removed: {self.stats['duplicates_removed']}")
        print(f"Unique proxies: {self.stats['unique_count']}")
        print(f"{'='*80}\n")
    
    def get_sorted_proxies(self) -> List[Dict]:
        """Get unique proxies sorted by speed (fastest first)"""
        proxies_list = list(self.unique_proxies.values())
        proxies_list.sort(key=lambda x: x.get('speed', 999))
        return proxies_list
    
    def save_results(self, output_prefix='merged_proxies'):
        """Save unique proxies to multiple formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_proxies = self.get_sorted_proxies()
        
        if not unique_proxies:
            print("❌ No proxies to save!")
            return
        
        print("="*80)
        print("SAVING RESULTS")
        print("="*80)
        
        # 1. Save as JSON (full data)
        json_file = f'{output_prefix}_{len(unique_proxies)}proxies_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(unique_proxies, f, indent=2)
        print(f"✓ Saved JSON: {json_file}")
        
        # 2. Save as Python list
        py_file = f'{output_prefix}_{len(unique_proxies)}proxies_{timestamp}.py'
        with open(py_file, 'w') as f:
            f.write(f"# Merged and deduplicated proxies - {datetime.now().isoformat()}\n")
            f.write(f"# Total unique proxies: {len(unique_proxies)}\n")
            f.write(f"# All work on Reddit\n\n")
            f.write("REDDIT_PROXIES = [\n")
            for p in unique_proxies:
                f.write(f"    '{p['proxy']}',  # Speed: {p.get('speed', 0):.2f}s | Source: {p.get('source', 'unknown')}\n")
            f.write("]\n\n")
            f.write("# Quick stats:\n")
            f.write(f"# Total proxies: {len(unique_proxies)}\n")
            f.write(f"# Fastest: {unique_proxies[0]['proxy']} ({unique_proxies[0].get('speed', 0):.2f}s)\n")
            f.write(f"# Slowest: {unique_proxies[-1]['proxy']} ({unique_proxies[-1].get('speed', 0):.2f}s)\n")
        print(f"✓ Saved Python: {py_file}")
        
        # 3. Save as plain text (just URLs)
        txt_file = f'{output_prefix}_{len(unique_proxies)}proxies_{timestamp}.txt'
        with open(txt_file, 'w') as f:
            for p in unique_proxies:
                f.write(f"{p['proxy']}\n")
        print(f"✓ Saved TXT: {txt_file}")
        
        # 4. Save statistics
        stats_file = f'{output_prefix}_stats_{timestamp}.txt'
        with open(stats_file, 'w') as f:
            f.write("PROXY MERGE STATISTICS\n")
            f.write("="*80 + "\n\n")
            f.write(f"Files processed: {self.stats['files_processed']}\n")
            f.write(f"Total proxies loaded: {self.stats['total_loaded']}\n")
            f.write(f"Duplicates removed: {self.stats['duplicates_removed']}\n")
            f.write(f"Unique proxies: {self.stats['unique_count']}\n\n")
            
            f.write("SPEED STATISTICS\n")
            f.write("="*80 + "\n\n")
            speeds = [p.get('speed', 0) for p in unique_proxies]
            f.write(f"Fastest: {min(speeds):.2f}s\n")
            f.write(f"Slowest: {max(speeds):.2f}s\n")
            f.write(f"Average: {sum(speeds)/len(speeds):.2f}s\n\n")
            
            f.write("SOURCE BREAKDOWN\n")
            f.write("="*80 + "\n\n")
            sources = {}
            for p in unique_proxies:
                source = p.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1
            
            for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{source}: {count} proxies\n")
        
        print(f"✓ Saved Stats: {stats_file}")
        
        print(f"\n{'='*80}")
        print(f"✅ ALL FILES SAVED!")
        print(f"{'='*80}\n")
    
    def print_summary(self):
        """Print detailed summary"""
        unique_proxies = self.get_sorted_proxies()
        
        print("="*80)
        print("FINAL SUMMARY")
        print("="*80)
        
        print(f"\n📊 Statistics:")
        print(f"  Total loaded: {self.stats['total_loaded']}")
        print(f"  Duplicates: {self.stats['duplicates_removed']}")
        print(f"  Unique proxies: {self.stats['unique_count']}")
        print(f"  Deduplication rate: {(self.stats['duplicates_removed']/self.stats['total_loaded']*100) if self.stats['total_loaded'] > 0 else 0:.1f}%")
        
        if unique_proxies:
            speeds = [p.get('speed', 0) for p in unique_proxies]
            print(f"\n⚡ Speed Statistics:")
            print(f"  Fastest: {min(speeds):.2f}s")
            print(f"  Slowest: {max(speeds):.2f}s")
            print(f"  Average: {sum(speeds)/len(speeds):.2f}s")
            
            print(f"\n📍 Source Breakdown:")
            sources = {}
            for p in unique_proxies:
                source = p.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1
            
            for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                print(f"  {source}: {count} proxies")
            
            print(f"\n🏆 Top 10 Fastest Proxies:")
            for i, p in enumerate(unique_proxies[:10], 1):
                print(f"  {i:2d}. {p['proxy'][:50]:<50} {p.get('speed', 0):5.2f}s")
            
            print(f"\n{'='*80}")
            print("COPY-PASTE READY (First 20):")
            print(f"{'='*80}\n")
            print("REDDIT_PROXIES = [")
            for p in unique_proxies[:20]:
                print(f"    '{p['proxy']}',")
            print("]")
            if len(unique_proxies) > 20:
                print(f"\n# ... and {len(unique_proxies) - 20} more in the saved files!")
        
        print(f"\n{'='*80}\n")


def find_proxy_files_auto():
    """Automatically find all proxy JSON files in current directory"""
    current_dir = Path('.')
    proxy_files = []
    
    # Look for files matching common patterns
    patterns = [
        'reddit*.json',
        '*proxy*.json',
        '*proxies*.json'
    ]
    
    for pattern in patterns:
        proxy_files.extend(current_dir.glob(pattern))
    
    # Remove duplicates and convert to strings
    return [str(f) for f in sorted(set(proxy_files))]


def main():
    """Main function"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "       🔄 PROXY FILE MERGER & DEDUPLICATOR 🔄".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    merger = ProxyMerger()
    
    # Get files to merge
    if len(sys.argv) > 1:
        # Files specified as command line arguments
        files = sys.argv[1:]
        print(f"Using {len(files)} files from command line arguments")
    else:
        # Auto-detect proxy files
        print("Auto-detecting proxy files in current directory...\n")
        files = find_proxy_files_auto()
        
        if not files:
            print("❌ No proxy files found!")
            print("\nUsage:")
            print("  python merge_proxies.py file1.json file2.json file3.json")
            print("\nOr place your proxy JSON files in the current directory")
            print("with names like: reddit*.json, *proxy*.json")
            return
        
        print(f"Found {len(files)} files:")
        for f in files:
            print(f"  - {f}")
        print()
        
        response = input("Merge these files? [Y/n]: ").strip().lower()
        if response and response not in ['y', 'yes']:
            print("Cancelled.")
            return
    
    # Merge files
    merger.merge_files(files)
    
    if merger.stats['total_loaded'] == 0:
        print("❌ No proxies loaded. Exiting.")
        return
    
    # Deduplicate
    merger.deduplicate()
    
    # Save results
    merger.save_results()
    
    # Print summary
    merger.print_summary()


if __name__ == "__main__":
    main()