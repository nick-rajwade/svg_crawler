#!/usr/bin/env python3
"""
Example Usage Script for Temenos SVG Crawler
This script demonstrates how to use the crawler with your credentials
"""

from temenos_svg_crawler import TemenosSVGCrawler
import os
from pathlib import Path

def main():
    print("🚀 Temenos SVG Crawler - Example Usage")
    print("=" * 50)
    
    # Your credentials (replace with actual values)
    USERNAME = "h03298"  # Replace with your username
    PASSWORD = "Temenos@12345"  # Replace with your password
    
    # Output directory
    OUTPUT_DIR = "Example_SVG_Output"
    
    print(f"📋 Configuration:")
    print(f"   Username: {USERNAME}")
    print(f"   Output Directory: {OUTPUT_DIR}")
    print(f"   Mode: Sample (2 sections, 1 process each)")
    
    # Create crawler instance
    crawler = TemenosSVGCrawler(
        username=USERNAME,
        password=PASSWORD,
        output_dir=OUTPUT_DIR,
        headless=True  # Set to False to see browser in action
    )
    
    print("\n🔄 Starting sample extraction...")
    
    # Run a small sample crawl
    success = crawler.run_sample_crawl(
        max_sections=2,           # Only crawl first 2 sections
        max_processes_per_section=1  # Only 1 process per section
    )
    
    if success:
        print("\n✅ Sample extraction completed successfully!")
        
        # Show results
        output_path = Path(OUTPUT_DIR)
        if output_path.exists():
            svg_files = list(output_path.rglob("*.svg"))
            
            print(f"\n📁 Extracted {len(svg_files)} SVG files:")
            total_size = 0
            
            for svg_file in svg_files:
                file_size = svg_file.stat().st_size
                total_size += file_size
                print(f"   📄 {svg_file.relative_to(output_path)} ({file_size:,} bytes)")
            
            print(f"\n📊 Total size: {total_size:,} bytes")
            
            # Check log file
            log_file = output_path / "crawl_log.json"
            if log_file.exists():
                print(f"📋 Crawl log: {log_file}")
                
                # Show log summary
                import json
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
                
                summary = log_data.get('summary', {})
                print(f"   ✅ Successful: {summary.get('extracted_count', 0)}")
                print(f"   ❌ Failed: {summary.get('failed_count', 0)}")
                print(f"   📝 Total processed: {summary.get('total_processed', 0)}")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Check the '{OUTPUT_DIR}' directory for extracted SVG files")
        print(f"   2. Open SVG files in a browser or SVG editor to view diagrams")
        print(f"   3. Run full extraction: python3 temenos_svg_crawler.py --username {USERNAME} --password {PASSWORD} --mode full")
        
    else:
        print("\n❌ Sample extraction failed!")
        print("   Check your credentials and network connection")
    
    print("\n" + "=" * 50)
    return success

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Example completed successfully!")
    else:
        print("❌ Example failed!")
    
    exit(0 if success else 1)

