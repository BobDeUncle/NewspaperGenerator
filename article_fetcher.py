"""
Article fetcher - handles Substack and general web URLs
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def is_substack_url(url):
    """Check if URL is a Substack article"""
    return 'substack.com' in url


def fetch_substack_article(url):
    """
    Fetch a Substack article using web scraping.
    Handles both direct URLs and reader view URLs.
    """
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # If this is a reader view URL, find the canonical article URL and re-fetch
    if '/home/post/' in url:
        canonical_link = soup.find('link', rel='canonical')
        if canonical_link and canonical_link.get('href'):
            canonical_url = canonical_link.get('href')
            print(f"DEBUG: Reader view detected, redirecting to canonical URL: {canonical_url}")
            return fetch_substack_article(canonical_url)  # Recursive call with real URL
    
    # Extract title
    title = None
    title_tag = soup.find('h1', class_='post-title')
    if title_tag:
        title = title_tag.get_text(strip=True)
    else:
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
    
    # Extract author and publication
    author = None
    publication = None

    # Publication name - h1 title with link to home
    pub_heading = soup.find('h1', class_=lambda c: c and 'title' in c)
    if pub_heading:
        pub_link = pub_heading.find('a', href='/')
        if pub_link:
            publication = pub_link.get_text(strip=True)
            # Fallback: check for img alt if text is empty
            if not publication:
                img = pub_link.find('img', alt=True)
                if img and img.get('alt'):
                    publication = img.get('alt')

    # Author name - link to @username profile with non-empty text
    author_links = soup.find_all('a', href=lambda h: h and h.startswith('https://substack.com/@'))
    for link in author_links:
        text = link.get_text(strip=True)
        if text:
            author = text
            break

    # Format author string
    if author and publication and author != publication:
        author = f"Written by {author} from {publication}"
    elif author:
        author = f"Written by {author}"
    else:
        author = "Unknown Author"
    
    # Extract date
    date = None
    time_tag = soup.find('time')
    if time_tag:
        date = time_tag.get('datetime') or time_tag.get_text(strip=True)
    
    # Extract content
    content_html = ""
    
    # Try to find main content container
    content_div = soup.find('div', class_='available-content')
    if not content_div:
        content_div = soup.find('div', class_='body')
    if not content_div:
        # Fallback: find article tag
        content_div = soup.find('article')
    
    if content_div:
        # Remove unwanted elements
        for tag in content_div.find_all(['script', 'style', 'button', 'form']):
            tag.decompose()
        
        # Get HTML content
        content_html = str(content_div)
    
    return {
        'title': title or 'Untitled',
        'author': author or 'Unknown Author',
        'date': date or '',
        'content_html': content_html,
        'url': url
    }


def fetch_general_article(url):
    """
    Fetch a general web article using BeautifulSoup.
    This is a simple extraction - works for basic articles but not all sites.
    """
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract title
    title = None
    # Try various common title locations
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text(strip=True)
    else:
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
    
    # Extract author (common meta tags)
    author = None
    author_meta = soup.find('meta', attrs={'name': 'author'})
    if author_meta:
        author = author_meta.get('content')
    
    # Extract date
    date = None
    time_tag = soup.find('time')
    if time_tag:
        date = time_tag.get('datetime') or time_tag.get_text(strip=True)
    
    # Extract main content
    # Try common article containers
    content_div = None
    for selector in [
        ('article', {}),
        ('div', {'class': 'article'}),
        ('div', {'class': 'content'}),
        ('div', {'class': 'post'}),
        ('main', {}),
    ]:
        content_div = soup.find(selector[0], selector[1])
        if content_div:
            break
    
    # Fallback: try to find the longest div with paragraphs
    if not content_div:
        all_divs = soup.find_all('div')
        max_text_len = 0
        for div in all_divs:
            text_len = len(div.get_text())
            if text_len > max_text_len:
                max_text_len = text_len
                content_div = div
    
    content_html = ""
    if content_div:
        # Remove unwanted elements
        for tag in content_div.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        content_html = str(content_div)
    
    return {
        'title': title or 'Untitled',
        'author': author or 'Unknown Author',
        'date': date or '',
        'content_html': content_html,
        'url': url
    }


def fetch_article(url):
    """
    Fetch an article from any URL.
    Automatically detects Substack vs general web articles.
    """
    if is_substack_url(url):
        return fetch_substack_article(url)
    else:
        return fetch_general_article(url)