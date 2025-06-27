#!/usr/bin/env python3
"""
Direct SVG Extraction Test
This script tests SVG extraction from the current browser session
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

def test_svg_extraction():
    """Test SVG extraction from a known process page"""
    print("🧪 Testing Direct SVG Extraction...")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        print("🔐 Logging in...")
        
        # Navigate to the main page
        driver.get("https://tlcengine.temenos.com")
        time.sleep(3)
        
        # Click on Partner Login
        partner_login = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Temenos Partner Login"))
        )
        partner_login.click()
        time.sleep(3)
        
        # Enter credentials
        username_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter your Username']"))
        )
        username_field.clear()
        username_field.send_keys("h03298")
        
        password_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']")
        password_field.clear()
        password_field.send_keys("Temenos@12345")
        
        # Click sign in
        sign_in_btn = driver.find_element(By.XPATH, "//span[text()='Sign in']")
        sign_in_btn.click()
        
        # Wait for successful login
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Library")))
        print("✅ Successfully logged in")
        
        # Navigate directly to a known process page
        test_url = "https://tlcengine.temenos.com/Content/Index/2be628ae-bed3-4d9d-a79c-d7584aa9cc01"
        print(f"🔗 Navigating to test process: {test_url}")
        
        driver.get(test_url)
        time.sleep(5)  # Wait for page to load completely
        
        # Extract SVG content
        print("🎨 Extracting SVG content...")
        
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
            return {
                content: mainSvg.outerHTML,
                size: maxSize,
                count: svgElements.length
            };
        } else {
            return {
                content: null,
                size: 0,
                count: svgElements.length
            };
        }
        """
        
        result = driver.execute_script(svg_script)
        
        if result['content']:
            print(f"✅ SVG extracted successfully!")
            print(f"   SVG size: {result['size']:,} characters")
            print(f"   Total SVG elements found: {result['count']}")
            
            # Save the SVG to verify content
            output_dir = Path("Test_Direct_SVG")
            output_dir.mkdir(exist_ok=True)
            
            svg_file = output_dir / "test_process.svg"
            with open(svg_file, 'w', encoding='utf-8') as f:
                f.write(result['content'])
            
            print(f"💾 SVG saved to: {svg_file}")
            
            # Verify SVG content
            if verify_svg_content(svg_file):
                print("✅ SVG content verification passed!")
                return True
            else:
                print("❌ SVG content verification failed!")
                return False
        else:
            print(f"❌ No SVG content found!")
            print(f"   Total elements checked: {result['count']}")
            
            # Take screenshot for debugging
            driver.save_screenshot("debug_no_svg.png")
            print("📸 Debug screenshot saved: debug_no_svg.png")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        driver.quit()

def verify_svg_content(svg_file):
    """Verify that the file contains valid SVG content"""
    try:
        with open(svg_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 SVG file size: {len(content):,} characters")
        
        # Basic SVG validation
        if not content.strip():
            print("❌ Empty SVG content")
            return False
            
        if not content.startswith('<svg'):
            print("❌ SVG doesn't start with <svg tag")
            return False
            
        if not content.endswith('</svg>'):
            print("❌ SVG doesn't end with </svg> tag")
            return False
            
        # Check for basic SVG elements
        svg_elements = ['<g', '<path', '<rect', '<circle', '<line', '<polyline', '<polygon', '<text']
        found_elements = [elem for elem in svg_elements if elem in content]
        
        print(f"📊 Found SVG elements: {', '.join(found_elements)}")
        
        if found_elements:
            print("✅ SVG contains valid drawing elements")
            return True
        else:
            print("❌ SVG doesn't contain drawing elements")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying SVG content: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Direct SVG Extraction Test")
    print("=" * 50)
    
    success = test_svg_extraction()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Direct SVG extraction test passed!")
    else:
        print("❌ Direct SVG extraction test failed!")
    
    exit(0 if success else 1)

