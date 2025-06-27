# Temenos TLC Engine SVG Crawler

## Overview
This Python automation script crawls the Temenos TLC Engine website to extract all SVG process diagrams and organize them by sections. The script has been tested and verified to successfully extract valid SVG content.

## ✅ Test Results
- **Direct SVG Extraction Test**: ✅ PASSED
- **SVG Content Verification**: ✅ PASSED  
- **File Size**: 78,650 characters
- **SVG Elements Found**: `<g>`, `<path>`, `<rect>`, `<circle>`, `<polyline>`, `<polygon>`, `<text>`

## Features
- 🔐 **Automated Login**: Handles Temenos Partner Login authentication
- 📊 **Complete Website Crawl**: Discovers all 16 main sections (0-15) with 200+ processes
- 🎨 **SVG Extraction**: Extracts high-quality SVG diagrams from each process
- 📁 **Organized Storage**: Saves files in structured folders by section
- 📋 **Detailed Logging**: Creates comprehensive crawl logs in JSON format
- 🧪 **Testing Modes**: Sample mode for testing, full mode for complete extraction
- 🖥️ **Headless Support**: Can run with or without browser UI

## Website Structure Discovered
```
0. Customer Relationship Management Processes (5 processes)
1. Retail Banking Processes (7 processes)
2. Corporate Banking Processes (9 processes)
3. Transactional Processes (11 processes)
4. Treasury Processes (13 processes)
5. Private Wealth Management Processes (15 processes)
6. Online Channels Processes (17 processes)
7. SMS Processes (19 processes)
8. Financial Accounting Parameter Maintenance Processes (21 processes)
9. Core Parameter Maintenance Processes (23 processes)
10. Islamic Banking Processes (25 processes)
11. Regionalized Solution Processes (27 processes)
12. Digital Engagement Processes (29 processes)
13. Regulatory Reporting and Compliance Processes (31 processes)
14. Financial Crime Mitigation Processes (33 processes)
15. Fund Accounting Processes (35 processes)
```

## Installation

### Prerequisites
- Python 3.7+
- Google Chrome browser
- Internet connection

### Setup
```bash
# Install required packages
pip install -r requirements.txt

# The script will automatically install ChromeDriver
```

## Usage

### Command Line Interface
```bash
# Sample crawl (recommended for testing)
python3 temenos_svg_crawler.py --username YOUR_USERNAME --password YOUR_PASSWORD --mode sample

# Full crawl (extracts everything)
python3 temenos_svg_crawler.py --username YOUR_USERNAME --password YOUR_PASSWORD --mode full

# Custom sample crawl
python3 temenos_svg_crawler.py --username YOUR_USERNAME --password YOUR_PASSWORD --mode sample --max-sections 5 --max-processes 3

# Run with visible browser (for debugging)
python3 temenos_svg_crawler.py --username YOUR_USERNAME --password YOUR_PASSWORD --mode sample --headless
```

### Parameters
- `--username`: Your Temenos login username (required)
- `--password`: Your Temenos login password (required)
- `--mode`: Crawl mode - `sample` or `full` (default: sample)
- `--output-dir`: Output directory for SVG files (default: Temenos_SVG_Files)
- `--max-sections`: Max sections for sample mode (default: 3)
- `--max-processes`: Max processes per section for sample mode (default: 2)
- `--headless`: Run browser in headless mode (default: True)

### Python API Usage
```python
from temenos_svg_crawler import TemenosSVGCrawler

# Create crawler instance
crawler = TemenosSVGCrawler(
    username="your_username",
    password="your_password",
    output_dir="My_SVG_Files",
    headless=True
)

# Run sample crawl
success = crawler.run_sample_crawl(max_sections=2, max_processes_per_section=1)

# Run full crawl
success = crawler.run_full_crawl()
```

## Output Structure
```
Temenos_SVG_Files/
├── 0_Customer_Relationship_Management_Processes/
│   ├── Process_Name_1.svg
│   └── Process_Name_2.svg
├── 1_Retail_Banking_Processes/
│   ├── Process_Name_3.svg
│   └── Process_Name_4.svg
├── ...
├── 15_Fund_Accounting_Processes/
│   ├── Process_Name_N.svg
│   └── Process_Name_N+1.svg
└── crawl_log.json
```

## Crawl Log Format
The script generates a detailed JSON log file:
```json
{
  "summary": {
    "extracted_count": 25,
    "failed_count": 2,
    "total_processed": 27
  },
  "processes": [
    {
      "section": "3. Transactional Processes",
      "page_title": "Initiate Liquidity Transfer Request (Manual) (SIC Instant)",
      "breadcrumb": "3. Transactional Processes > 3.4 Clearing and RTGS Processes > ...",
      "url": "https://tlcengine.temenos.com/Content/Index/...",
      "file_path": "/path/to/saved/file.svg",
      "svg_size": 78650,
      "status": "success"
    }
  ]
}
```

## Testing

### Run Tests
```bash
# Test direct SVG extraction (recommended first test)
python3 test_direct_svg.py

# Test full crawler functionality
python3 test_crawler.py
```

### Verify SVG Content
The extracted SVG files contain:
- Complete BPMN process diagrams
- All visual elements (shapes, connectors, text)
- Proper SVG structure and formatting
- Scalable vector graphics suitable for viewing/editing

## Performance Estimates
- **Sample Mode**: 5-10 minutes (extracts ~6 processes)
- **Full Mode**: 2-4 hours (extracts 200+ processes)
- **Network dependent**: Actual time varies based on connection speed

## Troubleshooting

### Common Issues
1. **Login Failed**: Verify username/password are correct
2. **ChromeDriver Issues**: Script auto-installs ChromeDriver, but ensure Chrome browser is installed
3. **Loading Timeouts**: Increase wait times in script if network is slow
4. **Permission Errors**: Ensure write permissions to output directory

### Debug Mode
Run with visible browser to see what's happening:
```bash
python3 temenos_svg_crawler.py --username USER --password PASS --mode sample
```

### Debug Screenshots
The script automatically saves debug screenshots when errors occur.

## Files Included
- `temenos_svg_crawler.py` - Main crawler script
- `test_direct_svg.py` - Direct SVG extraction test
- `test_crawler.py` - Full crawler test
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## Security Notes
- Credentials are not stored or logged
- Use environment variables for credentials in production
- Run in secure environment when processing sensitive data

## License
This script is provided as-is for educational and automation purposes.

