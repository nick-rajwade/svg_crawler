# Temenos TLC Engine SVG Crawler

This Python script automates the extraction of all SVG diagrams from the Temenos TLC Engine website using Selenium.

## @Tejas - Review the copilot fix in Issues and the feature branch (copilot-fix1)

## Features
- Logs into the Temenos TLC Engine portal with your credentials
- Crawls the Library section recursively, visiting all subpages and processes
- Extracts and saves all SVGs found on each page
- Supports headless mode for background operation
- Crawl log is saved as a JSON file for auditing

## Usage

### 1. Install Requirements
```
pip install -r requirements.txt
```

### 2. Run the Recursive Library Crawl
```
python temenos_svg_crawler.py --mode library-recursive --username <YOUR_USERNAME> --password <YOUR_PASSWORD> --headless
```
- `--mode library-recursive`: Recursively crawls all subpages and processes under the Library section
- `--username` and `--password`: Your Temenos TLC Engine credentials
- `--headless`: (Optional) Runs the browser in headless mode

### 3. Output
- SVG files are saved in the `Temenos_SVG_Files/library_recursive/` directory
- A crawl log is saved as `Temenos_SVG_Files/crawl_log.json`

### 4. Optional Arguments
- `--output-dir`: Change the output directory (default: `Temenos_SVG_Files`)
- `--max-pages`: (If implemented) Limit the number of pages to crawl

## Other Modes
- `sample`: Crawl a few sections and processes for testing
- `full`: Crawl all main sections and their processes (not recursive)

## Notes
- The recursive crawl is designed to cover all SVGs in the Library, including deeply nested processes.
- For large sites, the crawl may take significant time and disk space.

---

For any issues or improvements, please open an issue or pull request.
