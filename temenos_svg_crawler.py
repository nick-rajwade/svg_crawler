#!/usr/bin/env python3
"""
Temenos TLC Engine SVG Crawler
Automated script to extract all SVG content from the Temenos TLC Engine website
"""

import os
import time
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup

class TemenosSVGCrawler:
    def __init__(self, username, password, output_dir="Temenos_SVG_Files", headless=True):
        """
        Initialize the Temenos SVG Crawler
        
        Args:
            username (str): Temenos login username
            password (str): Temenos login password
            output_dir (str): Directory to save SVG files
            headless (bool): Run browser in headless mode
        """
        self.username = username
        self.password = password
        self.output_dir = Path(output_dir)
        self.base_url = "https://tlcengine.temenos.com"
        self.driver = None
        self.wait = None
        self.extracted_count = 0
        self.failed_count = 0
        self.process_log = []
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup Chrome options
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
    def setup_driver(self):
        """Initialize the Chrome WebDriver"""
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            print("✅ WebDriver initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            return False
            
    def login(self):
        """Login to the Temenos TLC Engine website"""
        try:
            print("🔐 Logging into Temenos TLC Engine...")
            
            # Navigate to the main page
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Click on Partner Login
            partner_login = self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Temenos Partner Login"))
            )
            partner_login.click()
            time.sleep(3)
            
            # Enter username
            username_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter your Username']"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Enter password
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click sign in
            sign_in_btn = self.driver.find_element(By.XPATH, "//span[text()='Sign in']")
            sign_in_btn.click()
            
            # Wait for successful login
            self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Library")))
            print("✅ Successfully logged in")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def get_main_sections(self):
        """Get all main sections from the library"""
        try:
            print("📚 Fetching main sections...")
            
            # Wait for any loading overlays to disappear before clicking Library
            try:
                self.wait.until(EC.invisibility_of_element_located((By.ID, "mainLoader")))
            except Exception:
                pass

            # Navigate to Library
            library_link = self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Library"))
            )
            library_link.click()

            # Wait for loading to complete
            time.sleep(2)
            # Wait for any loading overlays to disappear after clicking Library
            try:
                self.wait.until(EC.invisibility_of_element_located((By.ID, "mainLoader")))
            except Exception:
                pass

            # Additional wait for page stability
            time.sleep(2)
            
            # Get all main sections - try different selectors
            sections = []
            
            # Try to find section elements with different approaches
            section_selectors = [
                "li[contains(text(), 'Processes')]",
                ".section-item",
                "li",
                "a[href*='section']"
            ]
            
            for selector in section_selectors:
                try:
                    if 'contains' in selector:
                        # Use XPath for text-based selection
                        elements = self.driver.find_elements(By.XPATH, f"//li[contains(text(), 'Processes')]")
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements:
                        print(f"Found {len(elements)} elements with selector: {selector}")
                        for element in elements:
                            text = element.text.strip()
                            if re.match(r'^\d+\.\s+.*Processes$', text):
                                sections.append({
                                    'title': text,
                                    'element': element
                                })
                        
                        if sections:
                            break  # Found sections, stop trying other selectors
                            
                except Exception as e:
                    print(f"Selector {selector} failed: {e}")
                    continue
            
            # If no sections found with CSS selectors, try clicking around to find the structure
            if not sections:
                print("🔍 Trying to navigate to find sections...")
                
                # Look for any clickable elements that might lead to sections
                clickable_elements = self.driver.find_elements(By.CSS_SELECTOR, "a, button, li[role='button']")
                
                for element in clickable_elements[:10]:  # Check first 10 elements
                    try:
                        text = element.text.strip()
                        if 'process' in text.lower() or 'section' in text.lower():
                            print(f"Found potential section: {text}")
                            sections.append({
                                'title': text,
                                'element': element
                            })
                    except:
                        continue
            
            print(f"✅ Found {len(sections)} main sections")
            return sections
            
        except Exception as e:
            print(f"❌ Failed to get main sections: {e}")
            # Take a screenshot for debugging
            try:
                self.driver.save_screenshot("/home/ubuntu/debug_screenshot.png")
                print("📸 Debug screenshot saved to /home/ubuntu/debug_screenshot.png")
            except:
                pass
            return []
    
    def extract_svg_from_page(self, page_title="Unknown"):
        """Extract SVG content from the current page"""
        try:
            # Wait for the page to load completely
            time.sleep(3)
            
            # Execute JavaScript to get SVG content
            svg_script = """
            var svgElements = document.querySelectorAll('svg');
            var mainSvg = null;
            var maxSize = 0;
            
            for (var i = 0; i < svgElements.length; i++) {
                var svg = svgElements[i];
                if (svg.outerHTML.length > maxSize) {
                    maxSize = svg.outerHTML.length;
                    mainSvg = svg;
                }
            }
            
            if (mainSvg && maxSize > 1000) {
                return mainSvg.outerHTML;
            } else {
                return null;
            }
            """
            
            svg_content = self.driver.execute_script(svg_script)
            
            if svg_content:
                print(f"✅ Extracted SVG from: {page_title}")
                return svg_content
            else:
                print(f"⚠️  No substantial SVG found in: {page_title}")
                return None
                
        except Exception as e:
            print(f"❌ Failed to extract SVG from {page_title}: {e}")
            return None
    
    def is_process_map_svg(self, svg_content):
        """Heuristic to determine if an SVG is a process map (not an icon/image)"""
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(svg_content)
            width = root.attrib.get('width', '')
            height = root.attrib.get('height', '')
            # Try to parse width/height as int (strip px if present)
            def parse_dim(val):
                try:
                    return int(float(val.replace('px', '')))
                except:
                    return 0
            w = parse_dim(width)
            h = parse_dim(height)
            # Count number of child elements (complexity)
            num_elements = len(list(root.iter()))
            # Heuristic: process maps are large and complex
            if (w > 300 or h > 300) or num_elements > 20:
                return True
            return False
        except Exception:
            # If parsing fails, treat as icon/image
            return False
    
    def extract_all_svgs_from_page(self, page_title="Unknown", section_name="Unknown", prefix="overview", sub_section=None):
        """Extract and save all process map SVGs from the current page, ignoring icons/images"""
        try:
            time.sleep(2)
            svg_script = """
            var svgElements = document.querySelectorAll('svg');
            var svgs = [];
            for (var i = 0; i < svgElements.length; i++) {
                svgs.push(svgElements[i].outerHTML);
            }
            return svgs;
            """
            svg_list = self.driver.execute_script(svg_script)
            if svg_list:
                print(f"✅ Found {len(svg_list)} SVG(s) on {page_title}")
                for idx, svg_content in enumerate(svg_list):
                    if self.is_process_map_svg(svg_content):
                        # Use section/sub-section and process name for folder/filename
                        folder = section_name
                        if sub_section:
                            folder = os.path.join(section_name, sub_section)
                        filename = self.sanitize_filename(page_title) + ".svg"
                        self.save_svg_file(svg_content, folder, filename)
                    else:
                        print(f"   ⏩ Ignored icon/image SVG {idx+1} on {page_title}")
            else:
                print(f"⚠️  No SVGs found in: {page_title}")
        except Exception as e:
            print(f"❌ Failed to extract SVGs from {page_title}: {e}")

    def sanitize_filename(self, filename):
        """Sanitize filename for safe file system usage"""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', '_', filename)
        filename = filename.strip('._')
        return filename[:200]  # Limit length
    
    def save_svg_file(self, svg_content, section_path, filename):
        """Save SVG content to file"""
        try:
            # Create section directory
            section_dir = self.output_dir / section_path
            section_dir.mkdir(parents=True, exist_ok=True)
            
            # Sanitize filename
            safe_filename = self.sanitize_filename(filename)
            if not safe_filename.endswith('.svg'):
                safe_filename += '.svg'
            
            # Save file
            file_path = section_dir / safe_filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            print(f"💾 Saved: {file_path}")
            self.extracted_count += 1
            return str(file_path)
            
        except Exception as e:
            print(f"❌ Failed to save SVG file {filename}: {e}")
            self.failed_count += 1
            return None
    
    def crawl_process_page(self, section_info):
        """Crawl a specific process page and extract SVG"""
        try:
            # Get page title and URL
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            # Get breadcrumb for better organization
            breadcrumb_elements = self.driver.find_elements(By.CSS_SELECTOR, ".breadcrumb a, .breadcrumb span")
            breadcrumb = " > ".join([elem.text.strip() for elem in breadcrumb_elements if elem.text.strip()])
            
            if not breadcrumb:
                breadcrumb = page_title
            
            # Extract SVG content
            svg_content = self.extract_svg_from_page(page_title)
            
            if svg_content:
                # Create file path based on section and breadcrumb
                section_name = self.sanitize_filename(section_info['title'])
                filename = self.sanitize_filename(page_title)
                
                file_path = self.save_svg_file(svg_content, section_name, filename)
                
                # Log the process
                log_entry = {
                    'section': section_info['title'],
                    'page_title': page_title,
                    'breadcrumb': breadcrumb,
                    'url': current_url,
                    'file_path': file_path,
                    'svg_size': len(svg_content),
                    'status': 'success'
                }
                self.process_log.append(log_entry)
                return True
            else:
                # Log failed extraction
                log_entry = {
                    'section': section_info['title'],
                    'page_title': page_title,
                    'breadcrumb': breadcrumb,
                    'url': current_url,
                    'file_path': None,
                    'svg_size': 0,
                    'status': 'no_svg'
                }
                self.process_log.append(log_entry)
                return False
                
        except Exception as e:
            print(f"❌ Error crawling process page: {e}")
            return False
    
    def crawl_section(self, section_info, max_processes=None):
        """Crawl all processes in a section, and extract SVGs from the overview page"""
        try:
            print(f"\n🔍 Crawling section: {section_info['title']}")
            # Click on the section
            section_info['element'].click()
            time.sleep(3)
            # Extract SVGs from the section overview page
            section_name = self.sanitize_filename(section_info['title'])
            self.extract_all_svgs_from_page(page_title=self.driver.title, section_name=section_name, prefix="overview")
            # Find all process links in this section
            process_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/Content/Index/']")
            if max_processes:
                process_links = process_links[:max_processes]
            print(f"📄 Found {len(process_links)} processes in this section")
            for i, link in enumerate(process_links):
                try:
                    print(f"  Processing {i+1}/{len(process_links)}: {link.text[:50]}...")
                    self.driver.execute_script("arguments[0].click();", link)
                    time.sleep(3)
                    # Extract all SVGs from this process page
                    self.extract_all_svgs_from_page(page_title=self.driver.title, section_name=section_name, prefix=f"process_{i+1}")
                    self.driver.back()
                    time.sleep(2)
                    section_link = self.driver.find_element(By.XPATH, f"//li[contains(text(), '{section_info['title']}')]")
                    section_link.click()
                    time.sleep(2)
                    process_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/Content/Index/']")
                    if max_processes:
                        process_links = process_links[:max_processes]
                except Exception as e:
                    print(f"    ❌ Error processing link {i+1}: {e}")
                    continue
            return True
        except Exception as e:
            print(f"❌ Error crawling section {section_info['title']}: {e}")
            return False
    
    def run_sample_crawl(self, max_sections=3, max_processes_per_section=2):
        """Run a sample crawl for testing"""
        print("🚀 Starting SAMPLE crawl of Temenos TLC Engine...")
        print(f"   Max sections: {max_sections}")
        print(f"   Max processes per section: {max_processes_per_section}")
        
        if not self.setup_driver():
            return False
        
        try:
            # Login
            if not self.login():
                return False
            
            # Get main sections
            sections = self.get_main_sections()
            if not sections:
                return False
            
            # Limit sections for sample
            sections = sections[:max_sections]
            
            # Crawl each section
            for section in sections:
                self.crawl_section(section, max_processes_per_section)
            
            # Save crawl log
            self.save_crawl_log()
            
            print(f"\n✅ Sample crawl completed!")
            print(f"   Extracted: {self.extracted_count} SVG files")
            print(f"   Failed: {self.failed_count} extractions")
            
            return True
            
        except Exception as e:
            print(f"❌ Sample crawl failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
    
    def run_full_crawl(self):
        """Run a complete crawl of all sections"""
        print("🚀 Starting FULL crawl of Temenos TLC Engine...")
        print("   This will extract ALL SVG files from ALL sections")
        
        if not self.setup_driver():
            return False
        
        try:
            # Login
            if not self.login():
                return False
            
            # Get main sections
            sections = self.get_main_sections()
            if not sections:
                return False
            
            print(f"📊 Total sections to crawl: {len(sections)}")
            
            # Crawl each section
            for i, section in enumerate(sections):
                print(f"\n📂 Section {i+1}/{len(sections)}")
                self.crawl_section(section)
            
            # Save crawl log
            self.save_crawl_log()
            
            print(f"\n🎉 Full crawl completed!")
            print(f"   Extracted: {self.extracted_count} SVG files")
            print(f"   Failed: {self.failed_count} extractions")
            
            return True
            
        except Exception as e:
            print(f"❌ Full crawl failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
    
    def crawl_entire_site(self, max_pages=1000):
        """Crawl the entire authenticated website, extracting SVGs from every unique page"""
        print("\n🌐 Starting full site crawl (all pages after login)...")
        if not self.setup_driver():
            print("❌ WebDriver setup failed.")
            return False
        if self.driver is None:
            print("❌ WebDriver is None after setup.")
            return False
        try:
            if not self.login():
                print("❌ Login failed.")
                return False
            if self.driver is None:
                print("❌ WebDriver is None after login.")
                return False
            driver = self.driver
            driver.get(self.base_url)
            time.sleep(2)
            visited = set()
            queue = [driver.current_url]
            domain = urlparse(self.base_url).netloc
            page_count = 0
            while queue and page_count < max_pages:
                url = queue.pop(0)
                if url in visited:
                    continue
                visited.add(url)
                try:
                    driver.get(url)
                    time.sleep(2)
                    page_title = driver.title
                    section_name = "sitewide"
                    self.extract_all_svgs_from_page(page_title=page_title, section_name=section_name, prefix=f"page_{page_count+1}")
                    # Find all internal links
                    links = driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        try:
                            href = link.get_attribute("href")
                            if href and urlparse(href).netloc == domain and href not in visited and href not in queue:
                                queue.append(href)
                        except Exception:
                            continue
                    page_count += 1
                    print(f"[Crawl] Visited {page_count} pages, queue size: {len(queue)}")
                except Exception as e:
                    print(f"    ❌ Error visiting {url}: {e}")
                    continue
            self.save_crawl_log()
            print(f"\n🎉 Full site crawl completed!\n   Pages visited: {page_count}\n   Extracted: {self.extracted_count} SVG files\n   Failed: {self.failed_count} extractions")
            return True
        except Exception as e:
            print(f"❌ Full site crawl failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
    
    def crawl_library_recursively(self, max_pages=1000):
        """Recursively crawl all unique pages/links under the Library section, extracting SVGs from every page."""
        print("\n📚 Starting recursive Library crawl...")
        if not self.setup_driver():
            print("❌ WebDriver setup failed.")
            return False
        if self.driver is None:
            print("❌ WebDriver is None after setup.")
            return False
        try:
            if not self.login():
                print("❌ Login failed.")
                return False
            if self.driver is None:
                print("❌ WebDriver is None after login.")
                return False
            driver = self.driver
            wait = WebDriverWait(driver, 20)
            # Wait for loader to disappear before clicking Library
            try:
                wait.until(EC.invisibility_of_element_located((By.ID, "mainLoader")))
            except Exception:
                pass
            # Go to Library
            library_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Library")))
            library_link.click()
            # Wait for loader to disappear after clicking Library
            try:
                wait.until(EC.invisibility_of_element_located((By.ID, "mainLoader")))
            except Exception:
                pass
            time.sleep(2)
            visited = set()
            queue = [driver.current_url]
            domain = urlparse(self.base_url).netloc
            page_count = 0
            while queue and page_count < max_pages:
                url = queue.pop(0)
                if url in visited:
                    continue
                visited.add(url)
                try:
                    driver.get(url)
                    time.sleep(2)
                    page_title = driver.title
                    # Try to extract section/sub-section from breadcrumb if available
                    breadcrumb_elements = driver.find_elements(By.CSS_SELECTOR, ".breadcrumb a, .breadcrumb span")
                    breadcrumb = [elem.text.strip() for elem in breadcrumb_elements if elem.text.strip()]
                    section = breadcrumb[1] if len(breadcrumb) > 1 else "Library"
                    sub_section = breadcrumb[2] if len(breadcrumb) > 2 else None
                    self.extract_all_svgs_from_page(page_title=page_title, section_name=section, prefix=f"page_{page_count+1}", sub_section=sub_section)
                    # Only crawl links that are under the Library section or are process/content pages
                    links = driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        try:
                            href = link.get_attribute("href")
                            if not href:
                                continue
                            # Broader filter: crawl if link contains '/Library', '/Content/', or starts with the current Library base URL
                            if (
                                ("/Library" in href or "/Content/" in href)
                                or href.startswith(queue[0] if queue else driver.current_url)
                            ) and href not in visited and href not in queue:
                                queue.append(href)
                        except Exception:
                            continue
                    page_count += 1
                    print(f"[Library Recursive] Visited {page_count} pages, queue size: {len(queue)}")
                except Exception as e:
                    print(f"    ❌ Error visiting {url}: {e}")
                    continue
            self.save_crawl_log()
            print(f"\n🎉 Library recursive crawl completed!\n   Pages visited: {page_count}\n   Extracted: {self.extracted_count} SVG files\n   Failed: {self.failed_count} extractions")
            return True
        except Exception as e:
            print(f"❌ Library recursive crawl failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_crawl_log(self):
        """Save the crawl log to a JSON file"""
        try:
            log_file = self.output_dir / "crawl_log.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'summary': {
                        'extracted_count': self.extracted_count,
                        'failed_count': self.failed_count,
                        'total_processed': len(self.process_log)
                    },
                    'processes': self.process_log
                }, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Crawl log saved to: {log_file}")
            
        except Exception as e:
            print(f"❌ Failed to save crawl log: {e}")

def main():
    """Main function to run the crawler"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Temenos TLC Engine SVG Crawler')
    parser.add_argument('--username', required=True, help='Temenos login username')
    parser.add_argument('--password', required=True, help='Temenos login password')
    parser.add_argument('--output-dir', default='Temenos_SVG_Files', help='Output directory for SVG files')
    parser.add_argument('--mode', choices=['sample', 'full', 'library-recursive'], default='sample', help='Crawl mode: sample, full, or library-recursive')
    parser.add_argument('--max-sections', type=int, default=3, help='Max sections for sample mode')
    parser.add_argument('--max-processes', type=int, default=2, help='Max processes per section for sample mode')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    
    args = parser.parse_args()
    
    # Create crawler instance
    crawler = TemenosSVGCrawler(
        username=args.username,
        password=args.password,
        output_dir=args.output_dir,
        headless=args.headless
    )
    
    # Run crawl based on mode
    if args.mode == 'sample':
        success = crawler.run_sample_crawl(args.max_sections, args.max_processes)
    elif args.mode == 'full':
        success = crawler.run_full_crawl()
    elif args.mode == 'library-recursive':
        success = crawler.crawl_library_recursively()
    else:
        print('❌ Unknown mode!')
        success = False
    
    if success:
        print("\n🎉 Crawl completed successfully!")
    else:
        print("\n❌ Crawl failed!")
    
    return success

if __name__ == "__main__":
    main()

