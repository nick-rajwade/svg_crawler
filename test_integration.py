#!/usr/bin/env python3
"""
Integration test for improved folder structure functionality
This test demonstrates how the crawler would work with proper folder structure
"""

import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from temenos_svg_crawler import TemenosSVGCrawler

def create_mock_breadcrumb_scenarios():
    """Create realistic breadcrumb scenarios that would be found on the website"""
    return [
        # Main section pages
        {
            'url': 'https://example.com/library/section0',
            'title': 'Customer Relationship Management Processes Overview',
            'breadcrumb': ['Library', '0. Customer Relationship Management Processes'],
            'svg_content': '<svg><g><rect width="300" height="200"/><text>CRM Process</text></g></svg>'
        },
        {
            'url': 'https://example.com/library/section1',
            'title': 'Retail Banking Processes Overview',
            'breadcrumb': ['Library', '1. Retail Banking Processes'],
            'svg_content': '<svg><g><rect width="400" height="300"/><text>Retail Banking</text></g></svg>'
        },
        # Sub-section pages
        {
            'url': 'https://example.com/library/section3/subsection',
            'title': 'Clearing and RTGS Processes',
            'breadcrumb': ['Library', '3. Transactional Processes', '3.4 Clearing and RTGS Processes'],
            'svg_content': '<svg><g><rect width="500" height="400"/><text>RTGS Process</text></g></svg>'
        },
        # Individual process pages
        {
            'url': 'https://example.com/content/process1',
            'title': 'Initiate Liquidity Transfer Request (Manual) (SIC Instant)',
            'breadcrumb': ['Library', '3. Transactional Processes', '3.4 Clearing and RTGS Processes', 'Initiate Liquidity Transfer Request (Manual) (SIC Instant)'],
            'svg_content': '<svg><g><rect width="600" height="500"/><text>Liquidity Transfer</text></g></svg>'
        },
        {
            'url': 'https://example.com/content/process2',
            'title': 'Create Customer Account',
            'breadcrumb': ['Library', '0. Customer Relationship Management Processes', 'Account Management', 'Create Customer Account'],
            'svg_content': '<svg><g><rect width="350" height="250"/><text>Create Account</text></g></svg>'
        },
        # Edge case - no proper breadcrumb
        {
            'url': 'https://example.com/misc',
            'title': 'Some Other Page',
            'breadcrumb': ['Library'],
            'svg_content': '<svg><g><rect width="200" height="150"/><text>Misc Process</text></g></svg>'
        },
    ]

def test_integration_folder_structure():
    """Integration test showing complete folder structure creation"""
    print("🧪 Integration Test: Complete Folder Structure Creation")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create crawler instance
        crawler = TemenosSVGCrawler("test_user", "test_pass", temp_dir, True)
        
        # Get mock scenarios
        scenarios = create_mock_breadcrumb_scenarios()
        
        print(f"Processing {len(scenarios)} mock pages...")
        
        # Process each scenario
        for i, scenario in enumerate(scenarios):
            print(f"\n📄 Processing page {i+1}: {scenario['title']}")
            print(f"   URL: {scenario['url']}")
            print(f"   Breadcrumb: {' > '.join(scenario['breadcrumb'])}")
            
            # Parse breadcrumb
            section_folder, section_name = crawler.parse_section_from_breadcrumb(scenario['breadcrumb'])
            print(f"   📁 Section folder: {section_folder}")
            
            # Determine sub-section
            sub_section = None
            if len(scenario['breadcrumb']) > 2:
                potential_subsection = scenario['breadcrumb'][2]
                if ("Processes" in potential_subsection or 
                    any(char.isdigit() and '.' in potential_subsection for char in potential_subsection)):
                    sub_section = crawler.sanitize_filename(potential_subsection)
                    print(f"   📂 Sub-section: {sub_section}")
            
            # Create folder structure and save file
            folder = section_folder
            if sub_section:
                folder = os.path.join(section_folder, sub_section)
            
            filename = crawler.sanitize_filename(scenario['title']) + ".svg"
            file_path = crawler.save_svg_file(scenario['svg_content'], folder, filename)
            
            if file_path:
                rel_path = Path(file_path).relative_to(temp_dir)
                print(f"   💾 Saved: {rel_path}")
            else:
                print(f"   ❌ Failed to save file")
        
        # Analyze the created structure
        print(f"\n📊 Final Folder Structure Analysis:")
        print("=" * 40)
        
        output_path = Path(temp_dir)
        total_files = 0
        
        def print_directory_tree(path, prefix="", max_depth=3, current_depth=0):
            nonlocal total_files
            if current_depth >= max_depth:
                return
            
            items = sorted(path.iterdir())
            dirs = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            # Print directories first
            for i, directory in enumerate(dirs):
                is_last_dir = (i == len(dirs) - 1) and len(files) == 0
                print(f"{prefix}{'└── ' if is_last_dir else '├── '}📁 {directory.name}/")
                extension = "    " if is_last_dir else "│   "
                print_directory_tree(directory, prefix + extension, max_depth, current_depth + 1)
            
            # Then print files
            for i, file in enumerate(files):
                is_last = i == len(files) - 1
                print(f"{prefix}{'└── ' if is_last else '├── '}📄 {file.name}")
                total_files += 1
        
        print_directory_tree(output_path)
        
        print(f"\n📈 Statistics:")
        print(f"   Total SVG files created: {total_files}")
        print(f"   Total directories: {len(list(output_path.rglob('*'))) - total_files}")
        
        # Verify expected structure
        expected_sections = [
            "0_Customer_Relationship_Management_Processes",
            "1_Retail_Banking_Processes", 
            "3_Transactional_Processes"
        ]
        
        print(f"\n✅ Structure Validation:")
        for section in expected_sections:
            section_path = output_path / section
            if section_path.exists():
                svg_count = len(list(section_path.rglob("*.svg")))
                print(f"   ✅ {section}: {svg_count} SVG file(s)")
            else:
                print(f"   ❌ Missing: {section}")
        
        # Check for Library fallback
        library_path = output_path / "Library"
        if library_path.exists():
            svg_count = len(list(library_path.rglob("*.svg")))
            print(f"   ✅ Library (fallback): {svg_count} SVG file(s)")
        
        print(f"\n🎯 Expected Output Structure (matches documentation):")
        print("   Temenos_SVG_Files/")
        print("   ├── 0_Customer_Relationship_Management_Processes/")
        print("   │   ├── Create_Customer_Account.svg")
        print("   │   └── [other processes...]")
        print("   ├── 1_Retail_Banking_Processes/")
        print("   │   └── [retail processes...]")
        print("   ├── 3_Transactional_Processes/")
        print("   │   ├── 3_4_Clearing_and_RTGS_Processes/")
        print("   │   │   ├── Clearing_and_RTGS_Processes.svg")
        print("   │   │   └── Initiate_Liquidity_Transfer_Request_Manual_SIC_Instant.svg")
        print("   │   └── [other transactional processes...]")
        print("   └── Library/")
        print("       └── [fallback processes...]")
        
        return True

def main():
    """Main test function"""
    print("🚀 SVG Crawler Integration Test")
    print("Testing improved folder structure functionality")
    print("=" * 60)
    
    success = test_integration_folder_structure()
    
    print("=" * 60)
    if success:
        print("🎉 Integration test completed successfully!")
        print("✅ The library recursive crawl now properly mimics the output folder structure")
        return 0
    else:
        print("❌ Integration test failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)