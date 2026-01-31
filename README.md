# NewspaperGenerator

Convert online articles (as of now, only from Substack) into a printable 3-column newspaper PDF. Perfect for weekend reading away from screens.

## Quick Start

### Installation

1. Clone this repository:
```bash
git clone https://github.com/BobDeUncle/NewspaperGenerator.git
cd NewspaperGenerator
```

2. Install dependencies:
```bash
pip install requests beautifulsoup4 lxml reportlab
```

Requirements:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser
- `reportlab` - PDF generation

### Usage

1. Create a text file with your article URLs (one per line):
```
# urls.txt
https://substack.com/home/post/p-011111111
https://example.com/article
https://blog.example.com/post
```

Lines starting with `#` are treated as comments and ignored.

2. Run the generator:
```bash
python make_newspaper.py urls.txt
```

3. Your PDF will be saved as `Newspapers/YYYY-MM-DD.pdf` (e.g., `Newspapers/2026-01-31.pdf`)

### Custom output filename

```bash
python make_newspaper.py urls.txt -o weekly-reading.pdf
```

### Debug mode

Keep the intermediate HTML file for inspection:
```bash
python make_newspaper.py urls.txt --debug
```

## How It Works

1. **Fetch**: Downloads each article from the URL list
   - Detects Substack articles and uses custom scraping
   - Uses `trafilatura` for general web articles
   - Extracts title, author, date, and content

2. **Format**: Converts articles to ReportLab flowables
   - Parses HTML to extract paragraphs, headings, quotes
   - Applies newspaper typography styles
   - Preserves article structure

3. **Generate**: Creates PDF with 3-column layout
   - Uses ReportLab's multi-frame system for true column flow
   - A4 page size with optimised margins
   - Text flows naturally across columns and pages

## Architecture

**Files:**
- `make_newspaper.py` - Main CLI script
- `article_fetcher.py` - Fetches and parses articles from URLs
- `pdf_generator.py` - PDF generation with 3-column layout
- `urls.txt` - Example URL list

**PDF Generation:**
Uses ReportLab's `BaseDocTemplate` with three `Frame` objects per page. Text flows automatically from column to column and page to page. This gives you true newspaper-style layout where articles can span multiple columns.

## Supported Sites

**Full support:**
- Substack (both direct URLs and reader view URLs like `substack.com/home/post/p-*`)
- Most text-based websites

**Partial support:**
- Sites with heavy JavaScript (may need manual intervention)
- Paywalled content (only if you have access)

The fetcher tries `trafilatura` for non-Substack URLs, which works well for most news sites and blogs.

## Further Improvements

Non-Substack articles have had limited testing and may not work well, if at all. When I find myself reading more articles off Substack I will get this sorted but for now it's in a half-baked state.

## Contributing

Issues and pull requests welcome. This is a weekend project built quickly with AI to scratch a personal itch.

## License

MIT License - feel free to use and modify.
