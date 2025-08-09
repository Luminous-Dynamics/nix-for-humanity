#!/usr/bin/env python3
"""
from typing import Optional
NixOS Documentation Scraper for Model Training
Ethically scrapes and processes NixOS documentation for local model fine-tuning
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import argparse
import hashlib
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter decorator"""
    def __init__(self, calls_per_second: float = 0.5):
        self.min_interval = 1.0 / calls_per_second
        self.last_called = 0.0
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            elapsed = time.time() - self.last_called
            left_to_wait = self.min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            result = func(*args, **kwargs)
            self.last_called = time.time()
            return result
        return wrapper


class NixOSDocScraper:
    """Ethical scraper for NixOS documentation"""
    
    def __init__(self, output_dir: str = "training-data/nixos-docs"):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NixForHumanity-DocBot/1.0 (Educational; +https://github.com/Luminous-Dynamics/nix-for-humanity)'
        })
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limiter = RateLimiter(0.5)  # 2 requests per second
        self.robot_parsers = {}
        
    def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt"""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        if base_url not in self.robot_parsers:
            rp = RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt")
            try:
                rp.read()
                self.robot_parsers[base_url] = rp
            except Exception:
                logger.warning(f"Could not read robots.txt for {base_url}")
                return True
        
        return self.robot_parsers[base_url].can_fetch("*", url)
    
    @RateLimiter(0.5)
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page with rate limiting and error handling"""
        if not self.can_fetch(url):
            logger.warning(f"Robots.txt disallows fetching {url}")
            return None
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_manual_page(self, html: str, source_url: str) -> Optional[Dict]:
        """Parse NixOS manual HTML page"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find main content area
        content = (soup.find('div', class_='chapter') or 
                  soup.find('div', class_='section') or
                  soup.find('main') or
                  soup.find('article'))
        
        if not content:
            return None
        
        # Extract title
        title = soup.find('title')
        if title:
            title = title.text.strip()
        else:
            h1 = content.find('h1')
            title = h1.text.strip() if h1 else "Untitled"
        
        # Extract code examples
        code_examples = []
        for pre in content.find_all('pre'):
            code = pre.get_text(strip=True)
            if code:  # Skip empty code blocks
                code_examples.append({
                    'code': code,
                    'language': pre.get('class', [''])[0] if pre.get('class') else 'nix'
                })
        
        # Extract sections for Q&A generation
        sections = []
        for header in content.find_all(['h2', 'h3', 'h4']):
            section_content = []
            for sibling in header.find_next_siblings():
                if sibling.name in ['h2', 'h3', 'h4']:
                    break
                section_content.append(sibling.get_text(strip=True))
            
            if section_content:
                sections.append({
                    'heading': header.get_text(strip=True),
                    'content': ' '.join(section_content),
                    'level': int(header.name[1])
                })
        
        # Create structured document
        return {
            'source': source_url,
            'title': title,
            'content': content.get_text(strip=True),
            'sections': sections,
            'code_examples': code_examples,
            'timestamp': time.time(),
            'doc_hash': hashlib.md5(content.get_text().encode()).hexdigest()
        }
    
    def scrape_nix_pills(self):
        """Scrape Nix Pills tutorial series"""
        base_url = "https://nixos.org/guides/nix-pills/"
        logger.info("Scraping Nix Pills...")
        
        # Get index page
        index_html = self.fetch_page(base_url)
        if not index_html:
            return
        
        soup = BeautifulSoup(index_html, 'html.parser')
        
        # Find all pill links
        pills = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if 'pill' in href and href.endswith('.html'):
                pill_url = urljoin(base_url, href)
                pills.append(pill_url)
        
        # Scrape each pill
        for i, pill_url in enumerate(pills):
            logger.info(f"Scraping pill {i+1}/{len(pills)}: {pill_url}")
            
            html = self.fetch_page(pill_url)
            if html:
                data = self.parse_manual_page(html, pill_url)
                if data:
                    filename = f"nix-pills-{i+1:02d}"
                    self.save_training_data(data, filename)
    
    def scrape_nixos_manual(self):
        """Scrape the main NixOS manual"""
        base_url = "https://nixos.org/manual/nixos/stable/"
        logger.info("Scraping NixOS manual...")
        
        # Key sections to scrape
        sections = [
            "index.html",
            "options.html",
            "release-notes.html",
            # Add more sections as needed
        ]
        
        for section in sections:
            url = urljoin(base_url, section)
            logger.info(f"Scraping section: {url}")
            
            html = self.fetch_page(url)
            if html:
                data = self.parse_manual_page(html, url)
                if data:
                    filename = f"nixos-manual-{section.replace('.html', '')}"
                    self.save_training_data(data, filename)
    
    def scrape_wiki_page(self, page_title: str):
        """Scrape a specific NixOS Wiki page"""
        base_url = "https://nixos.wiki/wiki/"
        url = urljoin(base_url, page_title.replace(' ', '_'))
        
        logger.info(f"Scraping wiki page: {url}")
        
        html = self.fetch_page(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Wiki-specific parsing
            content = soup.find('div', id='mw-content-text')
            if content:
                # Remove edit links and other wiki-specific elements
                for elem in content.find_all(['span', 'div'], class_=['mw-editsection', 'toc']):
                    elem.decompose()
                
                data = {
                    'source': url,
                    'title': page_title,
                    'content': content.get_text(strip=True),
                    'sections': self._extract_wiki_sections(content),
                    'code_examples': self._extract_wiki_code(content),
                    'timestamp': time.time(),
                    'source_type': 'wiki'
                }
                
                filename = f"wiki-{page_title.replace(' ', '-').lower()}"
                self.save_training_data(data, filename)
    
    def _extract_wiki_sections(self, content):
        """Extract sections from wiki content"""
        sections = []
        for header in content.find_all(['h2', 'h3', 'h4']):
            # Skip if it's the contents header
            if header.get_text(strip=True).lower() == 'contents':
                continue
                
            section_content = []
            for sibling in header.find_next_siblings():
                if sibling.name in ['h2', 'h3', 'h4']:
                    break
                section_content.append(sibling.get_text(strip=True))
            
            sections.append({
                'heading': header.get_text(strip=True),
                'content': ' '.join(section_content),
                'level': int(header.name[1])
            })
        
        return sections
    
    def _extract_wiki_code(self, content):
        """Extract code examples from wiki content"""
        code_examples = []
        
        # Look for syntaxhighlight tags (MediaWiki style)
        for code_block in content.find_all(['syntaxhighlight', 'source', 'pre']):
            lang = code_block.get('lang', 'nix')
            code = code_block.get_text(strip=True)
            
            if code:
                code_examples.append({
                    'code': code,
                    'language': lang
                })
        
        return code_examples
    
    def save_training_data(self, data: Dict, filename: str):
        """Save scraped data to JSON file"""
        output_path = self.output_dir / f"{filename}.json"
        
        # Add metadata
        data['_metadata'] = {
            'scraper_version': '1.0',
            'license': 'MIT',  # NixOS docs are MIT licensed
            'attribution': 'NixOS Contributors',
            'purpose': 'Educational - Local model training for Nix for Humanity'
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved: {output_path}")
    
    def scrape_important_wiki_pages(self):
        """Scrape the most important wiki pages for training"""
        important_pages = [
            "Flakes",
            "Home Manager",
            "Overlays", 
            "NixOS modules",
            "Nix language basics",
            "Configuration.nix",
            "Development environment with nix-shell",
            "Garbage collection",
            "Nix channels",
            "Cross compilation",
            "Packaging software",
            "NixOS on ARM",
            "Distributed builds",
            "Binary cache",
            "Hydra",
        ]
        
        for page in important_pages:
            self.scrape_wiki_page(page)
            time.sleep(2)  # Extra delay between wiki pages


def main():
    parser = argparse.ArgumentParser(description='Scrape NixOS documentation for model training')
    parser.add_argument('--source', choices=['manual', 'pills', 'wiki', 'all'], 
                       default='all', help='Which documentation to scrape')
    parser.add_argument('--output', default='training-data/nixos-docs',
                       help='Output directory for scraped data')
    
    args = parser.parse_args()
    
    scraper = NixOSDocScraper(args.output)
    
    if args.source in ['manual', 'all']:
        scraper.scrape_nixos_manual()
    
    if args.source in ['pills', 'all']:
        scraper.scrape_nix_pills()
    
    if args.source in ['wiki', 'all']:
        scraper.scrape_important_wiki_pages()
    
    logger.info("Scraping complete!")
    
    # Print summary
    doc_count = len(list(Path(args.output).glob('*.json')))
    logger.info(f"Total documents scraped: {doc_count}")


if __name__ == '__main__':
    main()