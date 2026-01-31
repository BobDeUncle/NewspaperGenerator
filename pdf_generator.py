"""
PDF Generator using ReportLab - Creates a newspaper-style PDF
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib import colors
from bs4 import BeautifulSoup
from datetime import datetime
import re


def create_styles():
    """Create newspaper-specific paragraph styles"""
    styles = getSampleStyleSheet()
    
    # Newspaper title
    styles.add(ParagraphStyle(
        name='NewspaperTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=0.75*cm,
        fontName='Times-Bold',
    ))
    
    # Date style
    styles.add(ParagraphStyle(
        name='NewspaperDate',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Times-Italic',
        spaceAfter=0.5*cm
    ))
    
    # Article title
    styles.add(ParagraphStyle(
        name='ArticleTitle',
        parent=styles['Heading1'],
        fontSize=16,
        fontName='Times-Bold',
        spaceAfter=0.2*cm,
        spaceBefore=0.3*cm,
        textColor=colors.black,
        leading=20
    ))
    
    # Article metadata
    styles.add(ParagraphStyle(
        name='ArticleMeta',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Times-Italic',
        textColor=colors.HexColor('#666666'),
        spaceAfter=0.3*cm
    ))
    
    # Body text
    styles.add(ParagraphStyle(
        name='ColumnBody',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Times-Roman',
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=0.3*cm,
        textColor=colors.HexColor('#1a1a1a'),
        firstLineIndent=0
    ))
    
    # Heading in article
    styles.add(ParagraphStyle(
        name='ArticleHeading',
        parent=styles['Heading2'],
        fontSize=12,
        fontName='Times-Bold',
        spaceAfter=0.2*cm,
        spaceBefore=0.4*cm,
        textColor=colors.black
    ))
    
    # Subheading
    styles.add(ParagraphStyle(
        name='ArticleSubheading',
        parent=styles['Heading3'],
        fontSize=11,
        fontName='Times-Bold',
        spaceAfter=0.2*cm,
        spaceBefore=0.3*cm,
        textColor=colors.black
    ))
    
    # Quote
    styles.add(ParagraphStyle(
        name='Quote',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Times-Italic',
        textColor=colors.HexColor('#555555'),
        leftIndent=0.5*cm,
        spaceAfter=0.3*cm,
        alignment=TA_JUSTIFY
    ))
    
    return styles


def html_to_flowables(html_content, styles):
    """Convert HTML content to ReportLab flowables"""
    soup = BeautifulSoup(html_content, 'html.parser')
    flowables = []
    
    # Remove unwanted tags
    for tag in soup.find_all(['script', 'style', 'button', 'form', 'nav']):
        tag.decompose()

    # Remove subscription widgets:
    for tag in soup.find_all('div', class_='subscription-widget-wrap'):
        tag.decompose()

    # Remove References sections:
    for h_tag in soup.find_all(['h1', 'h2', 'h3']):
        if h_tag.get_text(strip=True).lower() == 'references':
            # Delete everything between this heading and the next heading (or end)
            current = h_tag.next_sibling
            while current:
                next_sibling = current.next_sibling
                if hasattr(current, 'name') and current.name in ['h1', 'h2', 'h3']:
                    break
                if hasattr(current, 'decompose'):
                    current.decompose()
                current = next_sibling
            # Delete the References heading itself
            h_tag.decompose()
            break
    
    # Process top-level elements
    def process_element(elem):
        result = []
        
        if elem.name == 'p':
            text = elem.get_text(strip=True)
            if text:
                result.append(Paragraph(text, styles['ColumnBody']))
        
        elif elem.name in ['h1', 'h2']:
            text = elem.get_text(strip=True)
            if text:
                result.append(Paragraph(text, styles['ArticleHeading']))
        
        elif elem.name == 'h3':
            text = elem.get_text(strip=True)
            if text:
                result.append(Paragraph(text, styles['ArticleSubheading']))
        
        elif elem.name == 'blockquote':
            text = elem.get_text(strip=True)
            if text:
                result.append(Paragraph(text, styles['Quote']))
        
        elif elem.name in ['ul', 'ol']:
            for li in elem.find_all('li', recursive=False):
                text = li.get_text(strip=True)
                if text:
                    # Simple bullet point
                    bullet = '•' if elem.name == 'ul' else f"{len(result)+1}."
                    result.append(Paragraph(f"{bullet} {text}", styles['ColumnBody']))
        
        elif elem.name == 'div':
            # Process children
            for child in elem.children:
                if hasattr(child, 'name'):
                    result.extend(process_element(child))
        
        return result
    
    # Find main content
    body = soup.find('body') or soup
    for elem in body.children:
        if hasattr(elem, 'name'):
            flowables.extend(process_element(elem))
    
    return flowables


def generate_newspaper_pdf(articles, output_path, debug=False):
    """Generate the newspaper PDF with 3-column layout"""
    
    # Page dimensions
    page_width, page_height = A4
    margin_left = 1.2*cm
    margin_right = 1.2*cm  
    margin_top = 1.5*cm
    margin_bottom = 1.5*cm
    
    # Calculate frame dimensions for 3 columns
    usable_width = page_width - margin_left - margin_right
    column_gap = 0.5*cm
    column_width = (usable_width - (2 * column_gap)) / 3
    
    # Create document
    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=margin_left,
        rightMargin=margin_right,
        topMargin=margin_top,
        bottomMargin=margin_bottom
    )
    
    # Create 3-column frames
    frame_height = page_height - margin_top - margin_bottom
    
    frames = [
        Frame(
            margin_left,
            margin_bottom,
            column_width,
            frame_height,
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            id='col1'
        ),
        Frame(
            margin_left + column_width + column_gap,
            margin_bottom,
            column_width,
            frame_height,
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            id='col2'
        ),
        Frame(
            margin_left + (column_width + column_gap) * 2,
            margin_bottom,
            column_width,
            frame_height,
            leftPadding=0,
            bottomPadding=0,
            rightPadding=0,
            topPadding=0,
            id='col3'
        )
    ]
    
    # Create page template
    template = PageTemplate(id='ThreeColumn', frames=frames)
    doc.addPageTemplates([template])
    
    # Create styles
    styles = create_styles()
    
    # Build story
    story = []
    
    # Newspaper header (first article will start in columns)
    today = datetime.now().strftime('%A, %B %d, %Y')
    story.append(Paragraph('THE WEEKLY', styles['NewspaperTitle']))
    story.append(Paragraph(today, styles['NewspaperDate']))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.black))
    story.append(Spacer(1, 0.3*cm))
    
    # Add articles
    for i, article in enumerate(articles):
        # Article divider (except for first)
        if i > 0:
            story.append(Spacer(1, 0.5*cm))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
            story.append(Spacer(1, 0.3*cm))
        
        # Article title and metadata
        story.append(Paragraph(article['title'], styles['ArticleTitle']))
        
        meta_text = article['author']
        if article.get('date'):
            meta_text += f" • {article['date']}"
        story.append(Paragraph(meta_text, styles['ArticleMeta']))
        
        # Article content
        content_flowables = html_to_flowables(article['content_html'], styles)
        story.extend(content_flowables)
    
    # Build PDF
    doc.build(story)