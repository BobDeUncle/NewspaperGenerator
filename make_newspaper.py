#!/usr/bin/env python3
"""
Newspaper Generator - Convert article URLs to a printable PDF newspaper
"""
import argparse
import sys
from pathlib import Path
from article_fetcher import fetch_article
from pdf_generator import generate_newspaper_pdf


def load_urls(filepath):
    """Load URLs from a text file (one per line)"""
    with open(filepath, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return urls


def main():
    parser = argparse.ArgumentParser(description='Generate a newspaper PDF from article URLs')
    parser.add_argument('urls_file', help='Text file containing article URLs (one per line)')
    parser.add_argument('-o', '--output', default=None, help='Output PDF filename (default: Newspapers/YYYY-MM-DD.pdf)')
    parser.add_argument('--debug', action='store_true', help='Keep intermediate files for debugging')
    
    args = parser.parse_args()
    
    # Set default output path with date
    if args.output is None:
        from datetime import datetime
        # Create Newspapers folder if it doesn't exist
        newspapers_dir = Path('Newspapers')
        newspapers_dir.mkdir(exist_ok=True)
        
        # Use today's date as filename
        today = datetime.now().strftime('%Y-%m-%d')
        args.output = str(newspapers_dir / f'{today}.pdf')
    
    # Load URLs
    if not Path(args.urls_file).exists():
        print(f"Error: File '{args.urls_file}' not found")
        sys.exit(1)
    
    urls = load_urls(args.urls_file)
    print(f"Loaded {len(urls)} URLs")
    
    # Fetch articles
    articles = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Fetching: {url}")
        try:
            article = fetch_article(url)
            articles.append(article)
            print(f"  → Got: {article['title']}")
        except Exception as e:
            print(f"  → Failed: {e}")
            continue
    
    if not articles:
        print("Error: No articles were successfully fetched")
        sys.exit(1)
    
    print(f"\nSuccessfully fetched {len(articles)} articles")
    
    # Generate PDF
    print(f"Generating PDF: {args.output}")
    generate_newspaper_pdf(articles, args.output, debug=args.debug)
    print(f"Done! PDF saved to: {args.output}")


if __name__ == '__main__':
    main()