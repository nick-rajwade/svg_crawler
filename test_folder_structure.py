#!/usr/bin/env python3
"""
Test script for improved folder structure functionality
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from temenos_svg_crawler import TemenosSVGCrawler

def test_breadcrumb_parsing():
    """Test the parse_section_from_breadcrumb method"""
    print("🧪 Testing breadcrumb parsing functionality...")
    
    # Create a mock crawler instance
    crawler = TemenosSVGCrawler("test", "test", "test_output", True)
    
    test_cases = [
        # Expected format from documentation
        (["Library", "0. Customer Relationship Management Processes", "Some Process"], 
         "0_Customer_Relationship_Management_Processes", 
         "Customer Relationship Management Processes"),
         
        (["Library", "1. Retail Banking Processes", "Another Process"], 
         "1_Retail_Banking_Processes", 
         "Retail Banking Processes"),
         
        (["Library", "15. Fund Accounting Processes", "Final Process"], 
         "15_Fund_Accounting_Processes", 
         "Fund Accounting Processes"),
         
        # Possible variations without numbers
        (["Library", "Customer Relationship Management Processes", "Some Process"], 
         "Customer_Relationship_Management_Processes", 
         "Customer Relationship Management Processes"),
         
        # Sub-section structure
        (["Library", "3. Transactional Processes", "3.4 Clearing and RTGS Processes", "Some Process"], 
         "3_Transactional_Processes", 
         "Transactional Processes"),
         
        # Edge cases
        (["Library"], "Library", None),
        ([], "Library", None),
        (["Library", "Unknown Section"], "Unknown_Section", "Unknown Section"),
    ]
    
    all_passed = True
    for i, (breadcrumb, expected_folder, expected_section) in enumerate(test_cases):
        folder_name, section_name = crawler.parse_section_from_breadcrumb(breadcrumb)
        
        print(f"Test {i+1}:")
        print(f"  Input: {breadcrumb}")
        print(f"  Expected folder: {expected_folder}")
        print(f"  Actual folder: {folder_name}")
        print(f"  Expected section: {expected_section}")
        print(f"  Actual section: {section_name}")
        
        if folder_name == expected_folder and section_name == expected_section:
            print(f"  ✅ PASS")
        else:
            print(f"  ❌ FAIL")
            all_passed = False
        print()
    
    return all_passed

def test_folder_structure_creation():
    """Test that folder structure is created correctly"""
    print("🧪 Testing folder structure creation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock crawler instance
        crawler = TemenosSVGCrawler("test", "test", temp_dir, True)
        
        # Test SVG content
        test_svg = '<svg><rect width="100" height="100"/></svg>'
        
        # Test cases for folder creation
        test_cases = [
            ("0_Customer_Relationship_Management_Processes", None, "test_process.svg"),
            ("1_Retail_Banking_Processes", "SubSection", "another_process.svg"),
            ("Library", None, "fallback_process.svg"),
        ]
        
        all_passed = True
        for section, sub_section, filename in test_cases:
            # Save a test SVG file
            result_path = crawler.save_svg_file(test_svg, section if not sub_section else f"{section}/{sub_section}", filename)
            
            if result_path:
                # Check if file exists
                file_path = Path(result_path)
                if file_path.exists():
                    print(f"✅ Created: {file_path.relative_to(temp_dir)}")
                    
                    # Verify content
                    with open(file_path, 'r') as f:
                        content = f.read()
                    if content == test_svg:
                        print(f"  ✅ Content verified")
                    else:
                        print(f"  ❌ Content mismatch")
                        all_passed = False
                else:
                    print(f"❌ File not created: {result_path}")
                    all_passed = False
            else:
                print(f"❌ Failed to save: {section}/{filename}")
                all_passed = False
        
        # Check the overall structure
        output_path = Path(temp_dir)
        folders = [f.name for f in output_path.iterdir() if f.is_dir()]
        expected_folders = ["0_Customer_Relationship_Management_Processes", "1_Retail_Banking_Processes", "Library"]
        
        print(f"\nFolder structure created:")
        for folder in sorted(folders):
            print(f"  📁 {folder}")
            # List files in each folder
            folder_path = output_path / folder
            for file in folder_path.rglob("*.svg"):
                print(f"    📄 {file.relative_to(folder_path)}")
        
        # Verify all expected folders exist
        for expected in expected_folders:
            if expected in folders:
                print(f"✅ Expected folder exists: {expected}")
            else:
                print(f"❌ Missing expected folder: {expected}")
                all_passed = False
    
    return all_passed

def main():
    """Main test function"""
    print("🚀 Testing Improved Folder Structure Functionality")
    print("=" * 60)
    
    # Test breadcrumb parsing
    breadcrumb_pass = test_breadcrumb_parsing()
    print("=" * 60)
    
    # Test folder structure creation
    folder_pass = test_folder_structure_creation()
    print("=" * 60)
    
    if breadcrumb_pass and folder_pass:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)