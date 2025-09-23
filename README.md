# Workflow Procesare - PDF Invoice Processing

## 🎯 What We're Building

An automated PDF invoice processing workflow that extracts, structures, and analyzes invoice data using AI. The system converts PDF invoices to structured Excel data with intelligent date extraction and monthly expense splitting.

## 🚀 Why This Exists

- **Manual processing is time-consuming** - Converting PDF invoices to structured data manually takes hours
- **Data accuracy issues** - Human error in data entry leads to incorrect financial records
- **Complex date handling** - Service periods and billing cycles need intelligent parsing
- **Monthly reporting** - Need to split multi-month invoices across correct accounting periods

## 🛠️ Tools & Technology

- **Python 3.8+** - Core processing language
- **Google Gemini AI** - OCR and intelligent data extraction
- **pandas** - Data manipulation and Excel generation
- **pdf2image** - PDF to image conversion for OCR
- **openpyxl** - Excel file handling
- **python-dotenv** - Environment configuration

## 📁 Project Structure

```
App.Simpla/
├── 1.PDF_to_Txt.py          # Step 1: PDF → Text (OCR)
├── 2.Txt_to_XLSX.py         # Step 2: Text → Structured Excel
├── 3.PDF_copy.py            # Step 3: Organize PDFs by status
├── 4.XLSX_validation_dates.py  # Step 4: Extract service dates
├── 5.Monthly expansion+clear data.py  # Step 5: Split by month
├── X.DELETE_IN_OUT.py       # Utility: Clean directories
├── config.py                # Centralized configuration
├── requirements.txt         # Dependencies
└── Data-IN-OUT/             # Data directories
    ├── 01. Gemini OCR PDF to TXT/
    │   ├── IN/              # PDF input files
    │   └── OUT/             # TXT output files
    ├── 02. Structurare TXT to XLSX/
    ├── 03. PDF_Copy doc suport/
    ├── 04. Date si validare XLSX/
    └── 05. Monthly Split Logic/
```

## ⚡ Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your Gemini API key
GEMINI_API_KEY=your_actual_api_key_here
```

### 2. Configure Paths
All paths are managed in `config.py` - no hardcoded paths in scripts.

### 3. Run Workflow
```bash
# Step 1: Convert PDFs to text
python 1.PDF_to_Txt.py

# Step 2: Extract structured data
python 2.Txt_to_XLSX.py

# Step 3: Organize PDFs
python 3.PDF_copy.py

# Step 4: Extract service dates
python 4.XLSX_validation_dates.py

# Step 5: Split by month
python 5.Monthly expansion+clear data.py
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (defaults in config.py)
API_BATCH_SIZE=10
API_DELAY_SECONDS=2
DEBUG_MODE=False
```

### Path Configuration
All paths are centralized in `config.py`:
- **PDF_INPUT_DIR** - Where to place PDF invoices
- **PDF_OUTPUT_DIR** - Where OCR text files are saved
- **XLSX_OUTPUT_DIR** - Where structured Excel files are created
- **PDF_COPY_BASE_DIR** - Where organized PDFs are stored

## 📊 Workflow Steps

1. **PDF → Text**: Uses Gemini AI to extract text from PDF invoices
2. **Text → Excel**: Structures extracted data into Excel with confidence scores
3. **PDF Organization**: Copies PDFs to "Considered" or "Not Considered" folders
4. **Date Extraction**: Intelligently extracts service periods from item descriptions
5. **Monthly Split**: Distributes multi-month invoices across correct accounting periods

## 🎯 Key Features

- **AI-Powered OCR** - High accuracy text extraction from PDFs
- **Intelligent Date Parsing** - Handles various date formats and service periods
- **Confidence Scoring** - Each extracted field has a confidence score (1-10)
- **Data Validation** - Automatic validation of extracted data
- **Monthly Proration** - Smart splitting of invoices across months
- **Centralized Config** - All paths and settings in one place

## 🚨 Requirements

- Python 3.8+
- Google Gemini API key
- Windows (paths configured for Windows)
- PDF files in supported formats

## 📝 Usage Notes

- Place PDF invoices in `Data-IN-OUT/01. Gemini OCR PDF to TXT/IN/`
- Review Excel output in `Data-IN-OUT/02. Structurare TXT to XLSX/`
- Mark invoices as "considered" in the Excel file
- Final monthly data in `Data-IN-OUT/05. Monthly Split Logic/`

## 🔄 GitHub Integration

This project is designed for GitHub Desktop:
- `.env` file should be added to `.gitignore`
- All configuration is centralized in `config.py`
- Data directories are separate from code
