# Workflow Procesare - Setup Instructions

## Configurare Environment

### 1. Creează fișierul .env

Creează un fișier `.env` în directorul rădăcină al proiectului cu următorul conținut:

```env
# ===========================================
# WORKFLOW PROCESARE - ENVIRONMENT CONFIG
# ===========================================

# Google Gemini API Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here

# ===========================================
# PATH CONFIGURATION
# ===========================================

# Base directories
BASE_PATH=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla\Data-IN-OUT
PROJECT_PATH=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla

# Step 1 - PDF to TXT
PDF_INPUT_DIR=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla\Data-IN-OUT\01. Gemini OCR PDF to TXT\IN
PDF_OUTPUT_DIR=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla\Data-IN-OUT\01. Gemini OCR PDF to TXT\OUT

# Step 2 - TXT to XLSX
TXT_INPUT_DIR=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla\Data-IN-OUT\01. Gemini OCR PDF to TXT\OUT
XLSX_OUTPUT_DIR=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla\Data-IN-OUT\02. Structurare TXT to XLSX

# Step 3 - PDF Copy
EXCEL_PATH=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla\Data-IN-OUT\02. Structurare TXT to XLSX\2.structured_extract.xlsx
PDF_COPY_BASE_DIR=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla\Data-IN-OUT\03. PDF_Copy doc suport

# Step 4 - Date Validation
DATE_VALIDATION_INPUT=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla\Data-IN-OUT\02. Structurare TXT to XLSX\2.structured_extract.xlsx
DATE_VALIDATION_OUTPUT=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla\Data-IN-OUT\04. Date si validare XLSX

# Step 5 - Monthly Expansion
MONTHLY_INPUT=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla\Data-IN-OUT\04. Date si validare XLSX\4.transformed_data.xlsx
MONTHLY_OUTPUT=C:\Users\george.nadrag\01.Cursor_WF\workflow.procesare\App.Simpla\Data-IN-OUT\05. Monthly Split Logic

# ===========================================
# API CONFIGURATION
# ===========================================

# Gemini API Settings
GEMINI_MODEL=gemini-1.5-flash
API_BATCH_SIZE=10
API_DELAY_SECONDS=2
API_MAX_RETRIES=3

# ===========================================
# PROCESSING CONFIGURATION
# ===========================================

# File Processing
MAX_WORKERS=8
DEBUG_MODE=False
ENABLE_CACHE=True

# Date Processing
DATE_FORMAT=%d/%m/%Y
FALLBACK_TO_INVOICE_MONTH=True
VAT_TOLERANCE=0.001

# ===========================================
# OUTPUT CONFIGURATION
# ===========================================

# Excel Output
EXCEL_ENGINE=openpyxl
INCLUDE_HYPERLINKS=True
AUTO_COLUMN_WIDTH=True

# File Naming
OUTPUT_PREFIX=structured_extract
TRANSFORMED_PREFIX=transformed_data
EXPANDED_PREFIX=expanded_monthly_rows
```

### 2. Instalare Dependențe

Rulează următoarea comandă pentru a instala toate dependențele necesare:

```bash
pip install -r requirements.txt
```

### 3. Configurare API Key

1. Obține un API key de la Google AI Studio
2. Înlocuiește `your_actual_gemini_api_key_here` cu API key-ul tău real în fișierul `.env`

### 4. Verificare Configurare

Rulează următorul script pentru a verifica configurarea:

```python
from config import config
print("✅ Configuration loaded successfully!")
print(f"API Key configured: {bool(config.GEMINI_API_KEY and config.GEMINI_API_KEY != 'your_gemini_api_key_here')}")
```

## Structura Proiectului

```
App.Simpla/
├── 1.PDF_to_Txt.py          # Step 1: Convert PDF to text using Gemini OCR
├── 2.Txt_to_XLSX.py         # Step 2: Extract structured data to Excel
├── 3.PDF_copy.py            # Step 3: Copy PDFs based on 'considered' flag
├── 4.XLSX_validation_dates.py  # Step 4: Extract and validate service dates
├── 5.Monthly expansion+clear data.py  # Step 5: Split invoices by month
├── X.DELETE_IN_OUT.py       # Utility: Clean input/output directories
├── config.py                # Configuration management
├── .env                     # Environment variables (create this)
├── requirements.txt         # Python dependencies
└── Data-IN-OUT/             # Data directories
    ├── 01. Gemini OCR PDF to TXT/
    │   ├── IN/              # PDF input files
    │   └── OUT/             # TXT output files
    ├── 02. Structurare TXT to XLSX/
    │   └── 2.structured_extract.xlsx
    ├── 03. PDF_Copy doc suport/
    │   ├── Considered/      # PDFs marked as considered
    │   └── Not Considered/  # PDFs not considered
    ├── 04. Date si validare XLSX/
    │   └── 4.transformed_data.xlsx
    └── 05. Monthly Split Logic/
        └── 5.expanded_monthly_rows.xlsx
```

## Utilizare

1. **Pregătire**: Pune PDF-urile în directorul `Data-IN-OUT/01. Gemini OCR PDF to TXT/IN/`
2. **Step 1**: Rulează `1.PDF_to_Txt.py` pentru OCR (va salva în `Data-IN-OUT/01. Gemini OCR PDF to TXT/OUT/`)
3. **Step 2**: Rulează `2.Txt_to_XLSX.py` pentru extragere structurată (va salva în `Data-IN-OUT/02. Structurare TXT to XLSX/`)
4. **Step 3**: Rulează `3.PDF_copy.py` pentru copiere PDF-uri (va salva în `Data-IN-OUT/03. PDF_Copy doc suport/`)
5. **Step 4**: Rulează `4.XLSX_validation_dates.py` pentru validare date (va salva în `Data-IN-OUT/04. Date si validare XLSX/`)
6. **Step 5**: Rulează `5.Monthly expansion+clear data.py` pentru expansiune lunară (va salva în `Data-IN-OUT/05. Monthly Split Logic/`)

## Configurare GitHub Desktop

1. Inițializează repository-ul local
2. Adaugă fișierul `.env` la `.gitignore` (conține informații sensibile)
3. Adaugă toate fișierele la staging
4. Fă primul commit
5. Conectează la un repository remote pe GitHub
