#!/usr/bin/env python3
"""
Test script for Temenos SVG Crawler
This script tests the crawler with a small sample to verify functionality
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from temenos_svg_crawler import TemenosSVGCrawler

def test_crawler():
    """Test the crawler with sample data"""
    print("🧪 Testing Temenos SVG Crawler...")
    
    # Test credentials (replace with actual credentials)
    username = "h03298"
    password = "Temenos@12345"
    
    # Create test output directory
    test_output_dir = "Test_SVG_Output"
    
    # Create crawler instance
    crawler = TemenosSVGCrawler(
        username=username,
        password=password,
        output_dir=test_output_dir,
        headless=True  # Run in headless mode for testing
    )
    
    print("📋 Test Configuration:")
    print(f"   Username: {username}")
    print(f"   Output Directory: {test_output_dir}")
    print(f"   Headless Mode: True")
    
    # Run sample crawl (limited scope for testing)
    success = crawler.run_sample_crawl(max_sections=2, max_processes_per_section=1)
    
    if success:
        print("\n✅ Test completed successfully!")
        
        # Verify extracted files
        output_path = Path(test_output_dir)
        if output_path.exists():
            svg_files = list(output_path.rglob("*.svg"))
            print(f"📁 Found {len(svg_files)} SVG files:")
            
            for svg_file in svg_files:
                file_size = svg_file.stat().st_size
                print(f"   📄 {svg_file.name} ({file_size:,} bytes)")
                
                # Verify SVG content
                if verify_svg_content(svg_file):
                    print(f"      ✅ Valid SVG content")
                else:
                    print(f"      ❌ Invalid SVG content")
            
            # Check crawl log
            log_file = output_path / "crawl_log.json"
            if log_file.exists():
                print(f"📋 Crawl log created: {log_file}")
            else:
                print("⚠️  No crawl log found")
        else:
            print("❌ No output directory created")
            
    else:
        print("\n❌ Test failed!")
    
    return success

def verify_svg_content(svg_file):
    """Verify that the file contains valid SVG content"""
    try:
        with open(svg_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic SVG validation
        if not content.strip():
            return False
            
        if not content.startswith('<svg'):
            return False
            
        if not content.endswith('</svg>'):
            return False
            
        # Check for basic SVG elements
        svg_elements = ['<g', '<path', '<rect', '<circle', '<line', '<polyline', '<polygon']
        has_elements = any(element in content for element in svg_elements)
        
        return has_elements
        
    except Exception as e:
        print(f"❌ Error verifying SVG content: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Temenos SVG Crawler Test")
    print("=" * 50)
    
    success = test_crawler()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

