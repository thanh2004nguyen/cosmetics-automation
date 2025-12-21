# Cosmetics API Automation

This project automates data collection from the Health Ministry API and updates Google Sheets with cosmetics data.

## Prerequisites

### Python Version
- **Python 3.12** or higher is required
- To check your Python version, run: `python --version`
- If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/)

## Setup Instructions

### 1. Create Virtual Environment

Navigate to the project directory and create a virtual environment:

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt when the virtual environment is active.

### 3. Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Credentials

Place the `credentials.json` file (provided separately) in the project root directory. This file contains the Google Service Account credentials needed to access Google Sheets API. The credentials file should be in the same folder as `main.py`.

### 5. Configure Google Sheet

The project is configured to work with an existing Google Sheet. The spreadsheet ID is already set in the code. Make sure the Google Sheet is shared with the service account email found in your `credentials.json` file. The project will automatically update two sheets: "Sheet1_Filtered" and "Sheet2_AllColumns".

## Running the Project

### Update Google Sheet (Default)

To update the Google Sheet with all data from the API:

```bash
python main.py
```

### Test API Connection

To test the API connection and verify data retrieval:

```bash
python main.py test
```

## Project Structure

```
.
├── main.py                 # Main script for updating Google Sheets
├── requirements.txt        # Python dependencies
├── credentials.json        # Google Service Account credentials (provided)
├── .github/workflows/       # GitHub Actions workflow
├── venv/                   # Virtual environment (created during setup)
└── logs/                   # Log files (created automatically)
```

## Logs

Log files are automatically created in the `logs` directory with the format `automation-DD-MM-YYYY.log`. Check these files for detailed execution information and any errors.

## Troubleshooting

- **"credentials.json not found"**: Make sure the `credentials.json` file is in the project root directory
- **"Cannot open sheet"**: Verify that the Google Sheet is shared with the service account email from your credentials file
- **Import errors**: Ensure the virtual environment is activated and all dependencies are installed with `pip install -r requirements.txt`
- **Permission errors**: Make sure the service account has edit access to the Google Sheet

## Notes

- The project fetches data from the Health Ministry API and processes it into two separate sheets
- Sheet 1 contains filtered columns (nameCosmeticHeb, nameCosmeticEng, notificationCode, importTrack, rpCorporation, manufacturer, importer)
- Sheet 2 contains all columns with special handling for packages and shades
- The automation can be scheduled to run monthly using GitHub Actions (see `.github/workflows/automation.yml`)

