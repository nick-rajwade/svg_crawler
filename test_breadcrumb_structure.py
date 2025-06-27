#!/usr/bin/env python3
"""
Test script to analyze breadcrumb structure
"""

import sys
import os
import re
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def parse_section_from_breadcrumb(breadcrumb_list):
    """
    Parse section information from breadcrumb list
    Expected format from documentation:
    0. Customer Relationship Management Processes
    1. Retail Banking Processes
    etc.
    """
    if not breadcrumb_list or len(breadcrumb_list) < 2:
        return "Library", None
    
    # Look for numbered sections in breadcrumb
    for item in breadcrumb_list:
        # Match pattern like "0. Customer Relationship Management Processes"
        match = re.match(r'^(\d+)\.\s+(.+)$', item.strip())
        if match:
            section_num = match.group(1)
            section_name = match.group(2)
            # Create folder name in expected format
            folder_name = f"{section_num}_{section_name.replace(' ', '_')}"
            return folder_name, section_name
    
    # If no numbered section found, use the second item (after "Library")
    if len(breadcrumb_list) > 1:
        section_text = breadcrumb_list[1]
        # Check if it contains "Processes"
        if "Processes" in section_text:
            # Try to extract number if present
            match = re.search(r'(\d+)', section_text)
            if match:
                section_num = match.group(1)
                folder_name = f"{section_num}_{section_text.replace(' ', '_').replace('.', '')}"
                return folder_name, section_text
        
        # Fallback to sanitized section text
        return section_text.replace(' ', '_').replace('.', ''), section_text
    
    return "Library", None

def test_breadcrumb_parsing():
    """Test breadcrumb parsing with various examples"""
    test_cases = [
        # Expected format from documentation
        ["Library", "0. Customer Relationship Management Processes", "Some Process"],
        ["Library", "1. Retail Banking Processes", "Another Process"],
        ["Library", "15. Fund Accounting Processes", "Final Process"],
        
        # Possible variations
        ["Library", "Customer Relationship Management Processes", "Some Process"],
        ["Library", "3. Transactional Processes", "3.4 Clearing and RTGS Processes", "Some Process"],
        ["Library"],
        ["Library", "0. Customer Relationship Management Processes"],
        
        # Edge cases
        [],
        ["Library", "Unknown Section"],
    ]
    
    print("🧪 Testing breadcrumb parsing...")
    print("=" * 60)
    
    for i, breadcrumb in enumerate(test_cases):
        folder_name, section_name = parse_section_from_breadcrumb(breadcrumb)
        print(f"Test {i+1}:")
        print(f"  Input: {breadcrumb}")
        print(f"  Folder: {folder_name}")
        print(f"  Section: {section_name}")
        print()

if __name__ == "__main__":
    test_breadcrumb_parsing()