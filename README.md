# Reddit Scraper - Complete Guide

A powerful Reddit scraper that fetches posts, comments, and user data using Reddit's public JSON API.

## 📁 Project Files

### Core Files (Main Functionality)

| File | Purpose | Use |
|------|---------|-----|
| **`main.py`** | Main Reddit scraper class | Primary scraper to use |
| **`requirements.txt`** | Python dependencies | `pip install -r requirements.txt` |
| **`README.md`** | This file | Documentation |

### Optional/Utility Files

| File | Purpose | Use |
|------|---------|-----|
| **`proxy_testing.py`** | Tests if proxies work | `python proxy_testing.py` |
| **`proxy_finder.py`** | Finds free proxies from multiple sources | `python proxy_finder.py` |
| **`merge.py`** | Merges & deduplicates proxy files | `python merge.py` |

### Data Folders

| Folder | Contents |
|--------|----------|
| **`reddit_data/`** | Output files (auto-created) |
| **`reddit_data01/`** | Backup output folder |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

That's it! Only `requests` library needed.

### 2. Use the Scraper

```python
from main import RedditJSONScraper

# Create scraper instance
scraper = RedditJSONScraper()

# Scrape posts from a subreddit
posts = scraper.scrape_subreddit('python', limit=10)

# Save to JSON
scraper.save_to_json(posts, 'posts.json')
```

### 3. Run Example

```bash
python main.py
```

---

## 📚 What Each File Does

### `main.py` - The Main Scraper

**Contains:**
- `RedditJSONScraper` class - Main scraper
- `scrape_subreddit()` - Get posts from a subreddit
- `scrape_post_comments()` - Get comments from a post
- `scrape_user_posts()` - Get posts from a user profile
- `save_to_json()` - Save data to JSON file
- `get_stats()` - Get scraper statistics

**Example Usage:**

```python
scraper = RedditJSONScraper(rate_limit_delay=(2, 4))

# Get hot posts
posts = scraper.scrape_subreddit('python', sort='hot', limit=50)

# Get top posts from last week
posts = scraper.scrape_subreddit('learnprogramming', sort='top', 
                                  limit=30, timeframe='week')

# Get comments from a post
comments = scraper.scrape_post_comments(
    post_url='https://www.reddit.com/r/python/comments/xxxxx/title/',
    limit=100
)

# Get user's posts
user_posts = scraper.scrape_user_posts('spez', limit=25)

# Save data
scraper.save_to_json(posts, 'my_posts.json')
```

---

### `proxy_testing.py` - Test Your Proxies

**Purpose:** Validate if proxies work before using them

**Usage:**

```bash
python proxy_testing.py
```

**What it does:**
- Loads proxies from `proxies.txt`
- Tests each proxy on httpbin.org
- Tests each proxy on Reddit specifically
- Shows which proxies work
- Generates ready-to-use code

**Requirements:**
- `proxies.txt` file with one proxy per line:
  ```
  http://192.168.1.1:8080
  http://192.168.1.2:8080
  ```

---

### `proxy_finder.py` - Find Free Proxies

**Purpose:** Automatically collect proxies from 20+ free sources and test on Reddit

**Usage:**

```bash
python proxy_finder.py
```

**What it does:**
1. Scrapes proxies from GitHub repos
2. Scrapes proxies from APIs
3. Tests all proxies on Reddit (parallel)
4. Saves working proxies to JSON/Python/TXT
5. Shows statistics

**Advanced options:**

```bash
# Test only 500 proxies (faster)
python proxy_finder.py --max-test 500

# Use 100 parallel workers (faster but uses more resources)
python proxy_finder.py --workers 100
```

**Output files:**
- `reddit_proxies_TIMESTAMP.json` - Full proxy data
- `reddit_proxies_TIMESTAMP.py` - Python-ready list
- `reddit_proxies_TIMESTAMP.txt` - Plain text list
- `reddit_proxies_stats_TIMESTAMP.txt` - Statistics

---

### `merge.py` - Merge Proxy Files

**Purpose:** Combine multiple proxy files and remove duplicates

**Usage:**

```bash
# Auto-detect proxy files
python merge.py

# Or specify files manually
python merge.py file1.json file2.json file3.json
```

**What it does:**
1. Loads proxies from multiple files
2. Removes duplicates
3. Keeps the fastest version of each proxy
4. Sorts by speed
5. Saves 4 formats (JSON, Python, TXT, Stats)

**Output files:**
- `merged_proxies_XXproxies_TIMESTAMP.json`
- `merged_proxies_XXproxies_TIMESTAMP.py`
- `merged_proxies_XXproxies_TIMESTAMP.txt`
- `merged_proxies_stats_TIMESTAMP.txt`

---

---

## 📊 Output Format

### Post Data Example

```json
{
  "title": "How to learn Python?",
  "author": "user123",
  "subreddit": "learnprogramming",
  "score": 1234,
  "num_comments": 156,
  "url": "https://...",
  "permalink": "/r/learnprogramming/comments/xxxxx/how_to_learn_python/",
  "selftext": "Post body text...",
  "created_date": "2024-01-01T00:00:00",
  "upvote_ratio": 0.95,
  "is_video": false
}
```

### Comment Data Example

```json
{
  "post": { /* post data */ },
  "comments": [
    {
      "author": "commenter",
      "body": "Great post!",
      "score": 42,
      "created_date": "2024-01-01T01:00:00",
      "depth": 0
    }
  ],
  "total_comments": 156
}
```

---

## ⚙️ Configuration

### Rate Limiting

Control request speed to avoid being blocked:

```python
# Slow and safe (default)
scraper = RedditJSONScraper(rate_limit_delay=(2, 5))

# Slower (safest)
scraper = RedditJSONScraper(rate_limit_delay=(5, 10))

# Faster (risky)
scraper = RedditJSONScraper(rate_limit_delay=(1, 2))
```

---

## 🔍 Troubleshooting

### Error: "403 Forbidden"
- Reddit blocked your request
- Solution: Wait 5-10 minutes and try again, or increase rate limit delay

### Error: "429 Too Many Requests"
- You're making requests too fast
- Solution: Increase `rate_limit_delay` to (5, 10)

### No posts found
- Subreddit name is wrong or private
- Solution: Check subreddit name is correct and public

### "ModuleNotFoundError: No module named 'requests'"
- Dependencies not installed
- Solution: Run `pip install -r requirements.txt`

---

## 📋 File Structure

```
reddit_scrapping/
├── main.py                    ← Main scraper
├── proxy_testing.py           ← Test proxies
├── proxy_finder.py            ← Find free proxies
├── merge.py                   ← Merge proxy files
├── requirements.txt           ← Dependencies
├── README.md                  ← This file
└── reddit_data/               ← Output folder
    ├── posts.json
    └── comments.json
```

---

## ✨ Key Features

✅ **No Browser Needed** - Uses Reddit's JSON API  
✅ **Fast** - 1-3 seconds per request  
✅ **Reliable** - 95-99% success rate  
✅ **Simple** - Minimal dependencies  
✅ **Full Data** - Posts, comments, user data  
✅ **Auto-Pagination** - Handles large datasets  
✅ **Rate Limited** - Built-in safety delays  

---

## 📞 Support

**Common issues:**

1. **Not finding proxies?** Run `python proxy_finder.py` again - proxies change frequently

2. **Scraper too slow?** Increase workers in `proxy_finder.py --workers 100`

3. **Too many errors?** Increase rate limit delay in `main.py`

4. **Need more features?** Check method signatures in `main.py` for all available options

---

## 🎯 Next Steps

1. ✅ Install: `pip install -r requirements.txt`
2. ✅ Test: `python main.py`
3. ✅ Customize: Edit `main.py` for your needs
4. ✅ Deploy: Run on your server

---

**Last Updated:** June 2026  
**Version:** 1.0.0

Happy scraping! 🚀
