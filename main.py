# API Data Scraping and Google Sheets Integration
import requests
import json
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import math
import logging
import sys

# ==================== CONFIGURATION ====================
# Google Sheets Configuration
SPREADSHEET_ID = "1p7Ft5JxI1wA6Qvqc6OieMeT5sdZyuRygkyfmdlbzXn4"
CREDENTIALS_FILE = "credentials.json"

# API Configuration
API_URL = "https://registries.health.gov.il/api/Cosmetics/GetCosmetics"
MAX_RESULT_PER_PAGE = 100  # Number of records per page when fetching data

# Logging Configuration
ENABLE_LOGGING = True

# ==================== LOGGING SETUP ====================
if ENABLE_LOGGING:
    # Create logs directory if not exists
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create log filename by date: automation-DD-MM-YYYY.log
    today = datetime.now()
    log_filename = f"automation-{today.strftime('%d-%m-%Y')}.log"
    log_file_path = os.path.join(logs_dir, log_filename)
    
    # Log WARNING, ERROR, and INFO to file, not print to terminal
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Log INFO, WARNING and ERROR
    
    # File handler: write all INFO, WARNING and ERROR to file
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
else:
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())

# ==================== API FUNCTIONS ====================

def get_api_data_sheet1(max_result=100, page_number=1):
    # Get data for Sheet 1 (filtered columns) - simple API call without businessNotificationItemId and businessTypeNotificationId
    payload = {
        "isDescending": False,
        "maxResult": max_result,
        "pageNumber": page_number
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'returnObject' in data and 'cosmeticsList' in data['returnObject']:
            return {
                'data': data['returnObject']['cosmeticsList'],
                'totalRows': data['returnObject'].get('totalRows', 0),
                'maxResults': data['returnObject'].get('maxResults', max_result)
            }
        return {'data': [], 'totalRows': 0, 'maxResults': max_result}
    except Exception as e:
        print(f"❌ Error fetching Sheet 1 data: {e}")
        return {'data': [], 'totalRows': 0, 'maxResults': max_result}

def get_api_data_sheet2(max_result=100, page_number=1):
    # Get data for Sheet 2 (all columns) - API call with businessNotificationItemId: 34 and businessTypeNotificationId: 5
    payload = {
        "isDescending": False,
        "maxResult": max_result,
        "pageNumber": page_number,
        "businessNotificationItemId": 34,
        "businessTypeNotificationId": 5
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'returnObject' in data and 'cosmeticsList' in data['returnObject']:
            return {
                'data': data['returnObject']['cosmeticsList'],
                'totalRows': data['returnObject'].get('totalRows', 0),
                'maxResults': data['returnObject'].get('maxResults', max_result)
            }
        return {'data': [], 'totalRows': 0, 'maxResults': max_result}
    except Exception as e:
        print(f"❌ Error fetching Sheet 2 data: {e}")
        return {'data': [], 'totalRows': 0, 'maxResults': max_result}

def get_all_pages_sheet1(max_result=None):
    # Get all data from Sheet 1 via pagination
    if max_result is None:
        max_result = MAX_RESULT_PER_PAGE
    
    print("Fetching Sheet 1 data (all pages)...")
    
    # Get first page to know totalRows
    first_page = get_api_data_sheet1(max_result=max_result, page_number=1)
    all_data = first_page['data']
    total_rows = first_page['totalRows']
    max_results = first_page['maxResults']
    
    if total_rows == 0:
        logger.warning("No data for Sheet 1")
        return []
    
    # Calculate number of pages
    total_pages = math.ceil(total_rows / max_results)
    print(f"  Total rows: {total_rows}, Pages: {total_pages}")
    
    # Get remaining pages
    if total_pages > 1:
        for page in range(2, total_pages + 1):
            print(f"  Fetching page {page}/{total_pages}...")
            page_data = get_api_data_sheet1(max_result=max_result, page_number=page)
            all_data.extend(page_data['data'])
    
    print(f"✓ Fetched {len(all_data)} records for Sheet 1")
    return all_data

def get_all_pages_sheet2(max_result=None):
    # Get all data from Sheet 2 via pagination
    if max_result is None:
        max_result = MAX_RESULT_PER_PAGE
    
    print("Fetching Sheet 2 data (all pages)...")
    
    # Get first page to know totalRows
    first_page = get_api_data_sheet2(max_result=max_result, page_number=1)
    all_data = first_page['data']
    total_rows = first_page['totalRows']
    max_results = first_page['maxResults']
    
    if total_rows == 0:
        logger.warning("No data for Sheet 2")
        return []
    
    # Calculate number of pages
    total_pages = math.ceil(total_rows / max_results)
    print(f"  Total rows: {total_rows}, Pages: {total_pages}")
    
    # Get remaining pages
    if total_pages > 1:
        for page in range(2, total_pages + 1):
            print(f"  Fetching page {page}/{total_pages}...")
            page_data = get_api_data_sheet2(max_result=max_result, page_number=page)
            all_data.extend(page_data['data'])
    
    print(f"✓ Fetched {len(all_data)} records for Sheet 2")
    return all_data

# ==================== DATA PROCESSING ====================

def extract_sheet1_fields(data_list):
    # Extract required columns for Sheet 1: notificationCode, importTrack, rpCorporation, manufacturer, importer
    result = []
    for item in data_list:
        result.append({
            'nameCosmeticHeb': item.get('nameCosmeticHeb', ''),
            'nameCosmeticEng': item.get('nameCosmeticEng', ''),
            'notificationCode': item.get('notificationCode', ''),
            'importTrack': item.get('importTrack', ''),
            'rpCorporation': item.get('rpCorporation', ''),
            'manufacturer': item.get('manufacturer', ''),
            'importer': item.get('importer', '')
        })
    return result

def format_packages(packages_list):
    # Format packages: only get packageName, quantity, measurementDesc - format: "packagename quantity measurementDesc | packagename quantity measurementDesc"
    if not packages_list or not isinstance(packages_list, list):
        return ""
    
    formatted = []
    for pkg in packages_list:
        if isinstance(pkg, dict):
            package_name = pkg.get('packageName', '')
            quantity = pkg.get('quantity', '')
            measurement = pkg.get('measurementDesc', '')
            if package_name or quantity or measurement:
                formatted.append(f"{package_name} {quantity} {measurement}".strip())
    
    return " | ".join(formatted)

def format_shades(shades_list):
    # Format shades: each color is a separate row, only color name - returns list of color names
    if not shades_list or not isinstance(shades_list, list):
        return []
    
    shade_names = []
    for idx, shade in enumerate(shades_list):
        if isinstance(shade, dict):
            shade_name = shade.get('shadeName', '')
            if shade_name:
                shade_names.append(shade_name)
        # Skip invalid shades
    
    return shade_names

def flatten_dict_for_sheet2(d, parent_key='', sep='_'):
    # Flatten nested dictionary for Sheet 2 with special handling for packages and shades - packages: format to string "name qty desc | name qty desc", shades: handled separately (each color one row)
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if k == 'packages' and isinstance(v, list):
            # Handle packages specially
            items.append((new_key, format_packages(v)))
        elif k == 'shades' and isinstance(v, list):
            # Shades will be handled separately, don't flatten here - skip, don't add to items
            pass
        elif isinstance(v, dict):
            items.extend(flatten_dict_for_sheet2(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert list to string representation
            items.append((new_key, json.dumps(v, ensure_ascii=False)))
        else:
            items.append((new_key, v))
    return dict(items)

# ==================== GOOGLE SHEETS FUNCTIONS ====================

def setup_google_sheets_client():
    # Setup Google Sheets client with credentials
    if not os.path.exists(CREDENTIALS_FILE):
        print("\n" + "="*60)
        print("❌ ERROR: credentials.json not found")
        print("="*60)
        print("\nSetup Google Sheets API credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create new project or select existing project")
        print("3. Enable Google Sheets API and Google Drive API")
        print("4. Create Service Account and download JSON key")
        print("5. Rename JSON file to 'credentials.json' and place in this directory")
        print("6. Share Google Sheet with Service Account email")
        return None
    
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"❌ Error setting up Google Sheets client: {e}")
        return None

def create_google_sheet_example(use_sample_data=True, spreadsheet_id=None):
    # Create sample Google Sheet with 2 sheets - use_sample_data=True: get 10 sample records for quick test, use_sample_data=False: get all data (takes time), spreadsheet_id: if provided, update existing sheet instead of creating new
    print("="*60)
    print("CREATE SAMPLE GOOGLE SHEET")
    print("="*60)
    
    # Setup Google Sheets client
    client = setup_google_sheets_client()
    if not client:
        return None
    
    # If spreadsheet_id provided, use existing sheet
    if spreadsheet_id:
        try:
            print(f"\nOpening existing Google Sheet...")
            spreadsheet = client.open_by_key(spreadsheet_id)
            print(f"✓ Opened sheet: {spreadsheet.url}")
        except Exception as e:
            print(f"❌ Cannot open sheet with ID: {spreadsheet_id}")
            print(f"Error: {e}")
            return None
    else:
        # Create new Google Sheet
        sheet_name = f"Cosmetics Data Example - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\nCreating Google Sheet: {sheet_name}...")
        
        try:
            spreadsheet = client.create(sheet_name)
            # Make it readable by anyone with link
            spreadsheet.share('', perm_type='anyone', role='reader')
            
            print(f"✓ Created sheet: {spreadsheet.url}")
        except Exception as e:
            error_msg = str(e)
            if 'storageQuotaExceeded' in error_msg or 'quota' in error_msg.lower():
                print("\n" + "="*60)
                print("❌ ERROR: Google Drive storage quota exceeded!")
                print("="*60)
                print("\n💡 SOLUTION:")
                print("1. Create Google Sheet manually:")
                print("   - Go to https://sheets.google.com")
                print("   - Create new sheet")
                print("   - Share with Service Account email:")
                print(f"     {Credentials.from_service_account_file(CREDENTIALS_FILE).service_account_email}")
                print("   - Copy Spreadsheet ID from URL (between /d/ and /edit)")
                print("   - Run: python main.py create --id <spreadsheet_id>")
                print("\n2. Or delete some files in Google Drive to free up space")
                return None
            else:
                raise
    
    try:
        # Get data from API
        print()
        if use_sample_data:
            print("Fetching sample data (10 records)...")
            data_sheet1 = get_api_data_sheet1(max_result=10, page_number=1)['data']
            data_sheet2 = get_api_data_sheet2(max_result=10, page_number=1)['data']
        else:
            print("Fetching all data (may take time)...")
            data_sheet1 = get_all_pages_sheet1(max_result=100)
            data_sheet2 = get_all_pages_sheet2(max_result=100)
        
        # Create Sheet 1 - filtered columns
        print("\nCreating Sheet 1 (filtered columns)...")
        
        # Check if sheet already exists
        try:
            worksheet1 = spreadsheet.worksheet("Sheet1_Filtered")
            worksheet1.clear()  # Clear if exists
        except:
            worksheet1 = spreadsheet.sheet1
            worksheet1.update_title("Sheet1_Filtered")
        
        # Extract required columns
        sheet1_data = extract_sheet1_fields(data_sheet1)
        
        # Headers in order: notificationCode, importTrack, rpCorporation, manufacturer, importer
        headers1 = ['nameCosmeticHeb', 'nameCosmeticEng', 'notificationCode', 'importTrack', 'rpCorporation', 'manufacturer', 'importer']
        
        # Prepare all rows for batch write
        all_rows = [headers1]  # Header row
        for item in sheet1_data:
            row = [
                item.get('nameCosmeticHeb', ''),
                item.get('nameCosmeticEng', ''),
                item.get('notificationCode', ''),
                item.get('importTrack', ''),
                item.get('rpCorporation', ''),
                item.get('manufacturer', ''),
                item.get('importer', '')
            ]
            all_rows.append(row)
        
        # Write batch to avoid rate limit
        batch_size = 5000
        for i in range(0, len(all_rows), batch_size):
            batch = all_rows[i:i + batch_size]
            worksheet1.append_rows(batch)
        
        print(f"✓ Sheet 1: {len(sheet1_data)} rows")
        
        # Create Sheet 2 - all columns
        print("\nCreating Sheet 2 (all columns)...")
        
        # Check if sheet already exists
        try:
            worksheet2 = spreadsheet.worksheet("Sheet2_AllColumns")
            worksheet2.clear()  # Clear if exists
        except:
            worksheet2 = spreadsheet.add_worksheet(title="Sheet2_AllColumns", rows=1000, cols=50)
        
        if data_sheet2:
            # Process data with special handling for packages and shades
            all_rows2 = []
            
            # Create headers in correct order
            first_item = data_sheet2[0]
            flattened_first = flatten_dict_for_sheet2(first_item)
            
            # Order: notificationCode, importTrack, rpCorporation, manufacturer, importer, ... (other fields)
            base_headers = ['notificationCode', 'importTrack', 'rpCorporation', 'manufacturer', 'importer']
            other_headers = [k for k in flattened_first.keys() if k not in base_headers]
            # Add 'shades' and 'shades2' to headers if not exists - shades: all shades joined by | (first row), shades2: individual shades (subsequent rows)
            if 'shades' not in other_headers:
                other_headers.append('shades')
            if 'shades2' not in other_headers:
                other_headers.append('shades2')
            headers2 = base_headers + other_headers
            
            # Add header row
            all_rows2.append(headers2)
            
            # Process each item
            for idx, item in enumerate(data_sheet2):
                flattened_item = flatten_dict_for_sheet2(item)
                
                # Process shades: each color is a separate row
                shades = item.get('shades', [])
                shade_names = format_shades(shades)
                
                if shade_names:
                    # Create first row: main product with all shades joined by |
                    all_shades_str = " | ".join(shade_names)
                    row = []
                    for h in headers2:
                        if h == 'shades':
                            row.append(all_shades_str)  # All shades joined by |
                        elif h == 'shades2':
                            row.append('')  # Empty in first row
                        else:
                            row.append(flattened_item.get(h, ''))
                    all_rows2.append(row)
                    
                    # Create subsequent rows: each shade in separate row
                    for shade_name in shade_names:
                        row = []
                        for h in headers2:
                            if h == 'shades':
                                row.append('')  # Empty in shade rows
                            elif h == 'shades2':
                                row.append(shade_name)  # Individual shade
                            else:
                                row.append(flattened_item.get(h, ''))
                        all_rows2.append(row)
                else:
                    # If no shades, create 1 row with both columns empty
                    row = []
                    for h in headers2:
                        if h == 'shades' or h == 'shades2':
                            row.append('')  # Empty string when no shades
                        else:
                            row.append(flattened_item.get(h, ''))
                    all_rows2.append(row)
            
            # Write batch to avoid rate limit
            batch_size = 5000
            for i in range(0, len(all_rows2), batch_size):
                batch = all_rows2[i:i + batch_size]
                worksheet2.append_rows(batch)
            
            # Actual row count = total rows (including header) - 1 header row
            total_rows = len(all_rows2) - 1
            print(f"✓ Sheet 2: {total_rows} rows (from {len(data_sheet2)} items) with {len(headers2)} columns")
        else:
            print("⚠ No data for Sheet 2")
        
        # Completed
        print("\n" + "="*60)
        print("✅ COMPLETED!")
        print(f"📊 Google Sheet URL: {spreadsheet.url}")
        print("="*60)
        
        return spreadsheet.url
        
    except Exception as e:
        print(f"\n❌ Error creating Google Sheet: {e}")
        print("\nCheck:")
        print("1. Is credentials.json correct?")
        print("2. Has Service Account been shared with Google Sheet?")
        print("3. Are Google Sheets API and Google Drive API enabled?")
        import traceback
        traceback.print_exc()
        return None

def update_existing_sheet(spreadsheet_id=None):
    # Update data to existing Google Sheet - used for automation, runs monthly
    if spreadsheet_id is None:
        spreadsheet_id = SPREADSHEET_ID
    
    print("="*60)
    print("UPDATE GOOGLE SHEET")
    print("="*60)
    
    logger.info("Starting Google Sheet update")
    
    client = setup_google_sheets_client()
    if not client:
        logger.error("Cannot setup Google Sheets client")
        return False
    
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        print(f"✓ Opened spreadsheet: {spreadsheet.url}")
        
        # Get all data from API
        print("\nFetching all data from API (may take time)...")
        data_sheet1 = get_all_pages_sheet1()
        data_sheet2 = get_all_pages_sheet2()
        
        # Update Sheet 1
        worksheet1 = spreadsheet.worksheet("Sheet1_Filtered")
        sheet1_data = extract_sheet1_fields(data_sheet1)
        
        # Clear and write again
        worksheet1.clear()
        headers1 = ['nameCosmeticHeb', 'nameCosmeticEng', 'notificationCode', 'importTrack', 'rpCorporation', 'manufacturer', 'importer']
        
        # Prepare all rows for batch write
        all_rows = [headers1]  # Header row
        for item in sheet1_data:
            row = [
                item.get('nameCosmeticHeb', ''),
                item.get('nameCosmeticEng', ''),
                item.get('notificationCode', ''),
                item.get('importTrack', ''),
                item.get('rpCorporation', ''),
                item.get('manufacturer', ''),
                item.get('importer', '')
            ]
            all_rows.append(row)
        
        # Write batch to avoid rate limit (write 5000 rows each time)
        batch_size = 5000
        for i in range(0, len(all_rows), batch_size):
            batch = all_rows[i:i + batch_size]
            worksheet1.append_rows(batch)
        
        print(f"✓ Updated Sheet 1: {len(sheet1_data)} rows")
        
        # Update Sheet 2
        worksheet2 = spreadsheet.worksheet("Sheet2_AllColumns")
        
        if data_sheet2:
            
            # Process data with special handling for packages and shades
            all_rows2 = []
            
            # Create headers in correct order - get all fields from first item
            first_item = data_sheet2[0]
            flattened_first = flatten_dict_for_sheet2(first_item)
            
            # Create headers in order: notificationCode, importTrack, rpCorporation, manufacturer, importer, ... (other fields)
            base_headers = ['notificationCode', 'importTrack', 'rpCorporation', 'manufacturer', 'importer']
            other_headers = [k for k in flattened_first.keys() if k not in base_headers]
            # Add 'shades' and 'shades2' to headers if not exists - shades: all shades joined by | (first row), shades2: individual shades (subsequent rows)
            if 'shades' not in other_headers:
                other_headers.append('shades')
            if 'shades2' not in other_headers:
                other_headers.append('shades2')
            headers2 = base_headers + other_headers
            
            # Add header row
            all_rows2.append(headers2)
            
            # Process each item
            for idx, item in enumerate(data_sheet2):
                flattened_item = flatten_dict_for_sheet2(item)
                
                # Process shades: each color is a separate row
                shades = item.get('shades', [])
                shade_names = format_shades(shades)
                
                if shade_names:
                    # Create first row: main product with all shades joined by |
                    all_shades_str = " | ".join(shade_names)
                    row = []
                    for h in headers2:
                        if h == 'shades':
                            row.append(all_shades_str)  # All shades joined by |
                        elif h == 'shades2':
                            row.append('')  # Empty in first row
                        else:
                            row.append(flattened_item.get(h, ''))
                    all_rows2.append(row)
                    
                    # Create subsequent rows: each shade in separate row
                    for shade_name in shade_names:
                        row = []
                        for h in headers2:
                            if h == 'shades':
                                row.append('')  # Empty in shade rows
                            elif h == 'shades2':
                                row.append(shade_name)  # Individual shade
                            else:
                                row.append(flattened_item.get(h, ''))
                        all_rows2.append(row)
                else:
                    # If no shades, create 1 row with both columns empty
                    row = []
                    for h in headers2:
                        if h == 'shades' or h == 'shades2':
                            row.append('')  # Empty string when no shades
                        else:
                            row.append(flattened_item.get(h, ''))
                    all_rows2.append(row)
            
            worksheet2.clear()
            
            # Write batch to avoid rate limit (write 5000 rows each time)
            batch_size = 5000
            for i in range(0, len(all_rows2), batch_size):
                batch = all_rows2[i:i + batch_size]
                worksheet2.append_rows(batch)
            
            # Actual row count = total rows (including header) - 1 header row
            total_rows = len(all_rows2) - 1
            print(f"✓ Updated Sheet 2: {total_rows} rows (from {len(data_sheet2)} items)")
        else:
            logger.warning("No data for Sheet 2")
        
        print("\n✅ Update completed!")
        logger.info("Google Sheet update completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error updating Google Sheet: {e}", exc_info=True)
        print(f"\n❌ Error updating Google Sheet: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== MAIN ====================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            # Test API calls
            print("Testing API calls...")
            data1 = get_api_data_sheet1(max_result=5, page_number=1)
            data2 = get_api_data_sheet2(max_result=5, page_number=1)
            print(f"\nSheet 1 - Total rows: {data1['totalRows']}, Records: {len(data1['data'])}")
            print(f"Sheet 2 - Total rows: {data2['totalRows']}, Records: {len(data2['data'])}")
        else:
            print("❌ Invalid command")
            print("\nUsage:")
            print("  python main.py        # Update Google Sheet with all data")
            print("  python main.py test   # Test API calls")
    else:
        # Default: update Google Sheet with all data
        if not SPREADSHEET_ID:
            print("❌ ERROR: SPREADSHEET_ID not set in main.py")
            sys.exit(1)
        
        update_existing_sheet()

