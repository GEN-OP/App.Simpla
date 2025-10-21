# 🤖 AI PDF Invoice Processor

> Transform PDF invoices into structured data with AI-powered OCR and validation

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 What This Is

An automated PDF invoice processing system with a modern Streamlit dashboard that extracts, structures, and validates invoice data using Google Gemini AI. The system converts PDF invoices to structured Excel data with intelligent date extraction and comprehensive data validation.

## ✨ Features

### 🖥️ **Modern Streamlit Dashboard**
- **Clean, Professional UI** - Modern gradient design with intuitive navigation
- **Separate Workflow Tabs** - Dedicated tabs for each processing step
- **Real-Time Progress** - Live status updates and progress tracking
- **Interactive Results** - View and download Excel data with metrics
- **Comprehensive Settings** - System status, error logs, and diagnostics
- **Cloud-Ready** - Works locally and on Streamlit Cloud

### 🤖 **AI-Powered Processing**
- **Advanced OCR** - Google Gemini 2.0 Flash for high-accuracy text extraction
- **Intelligent Data Extraction** - Automatic field detection and structuring
- **Date Intelligence** - Smart parsing of service periods and billing cycles
- **Data Validation** - Automatic quality checks and VAT validation
- **Error Handling** - Comprehensive error logging and recovery

### 📊 **Data Management**
- **Excel Export** - Structured data with confidence scores
- **Multi-File Processing** - Batch upload and processing
- **Progress Tracking** - Real-time status for each file
- **Data Validation** - Quality scores and validation checks
- **Results Dashboard** - Interactive data preview with metrics

## 🚀 Quick Start

### 1️⃣ Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd App.Simpla

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Configure API Key

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

Get your API key from: [Google AI Studio](https://makersuite.google.com/app/apikey)

### 3️⃣ Run the Dashboard

**Option 1: Using the batch script (Windows)**
```bash
run_dashboard.bat
```

**Option 2: Manual activation**
```bash
.\.venv\Scripts\activate
streamlit run app_streamlit.py
```

The dashboard will open automatically at `http://localhost:8501`

## 📁 Project Structure

```
App.Simpla/
├── 📄 app_streamlit.py          # Main Streamlit dashboard
├── 📄 1.PDF_to_Txt.py           # Step 1: PDF → Text (OCR)
├── 📄 2.Txt_to_XLSX.py          # Step 2: Text → Structured Excel
├── 📄 3.PDF_copy.py             # Step 3: Organize PDFs
├── 📄 4.XLSX_validation_dates.py # Step 4: Date extraction & validation
├── 📄 5.Monthly expansion+clear data.py  # Step 5: Monthly splitting
├── 📄 config.py                 # Centralized configuration
├── 📄 requirements.txt          # Python dependencies
├── 📄 run_dashboard.bat         # Quick launch script
├── 📄 DASHBOARD_README.md       # Detailed dashboard docs
└── 📁 Data-IN-OUT/              # Data directories
    ├── 01. Gemini OCR PDF to TXT/
    │   ├── IN/                  # 📥 PDF input files
    │   └── OUT/                 # 📤 TXT output files
    ├── 02. Structurare TXT to XLSX/
    ├── 03. PDF_Copy doc suport/
    ├── 04. Date si validare XLSX/
    └── 05. Monthly Split Logic/
```

## 🎨 Dashboard Overview

### 🏠 Home Tab
- Welcome message and feature overview
- Workflow visualization with step-by-step process
- Current system status and metrics
- Processing time and error tracking

### 1️⃣ PDF → TXT Tab
- Upload single or multiple PDF invoices
- Real-time OCR processing with Gemini AI
- Progress tracking for each file
- Success/failure status for each document

### 2️⃣ TXT → XLSX Tab
- Convert extracted text to structured Excel
- Automatic field detection and extraction
- Data validation and quality scoring
- Confidence scores for each field

### 3️⃣ XLSX Validation Tab
- Extract and validate service dates
- VAT calculation verification
- Date range processing
- Final data quality checks

### 📊 Results Tab
- Interactive Excel data preview
- Summary metrics (rows, columns, completion %)
- Download processed files
- File metadata and timestamps
- Refresh and data management

### ⚙️ Settings Tab
- **System Status** - Environment, API, Poppler, directories
- **Error Log** - Filterable log with timestamps
- **Configuration** - API and processing settings
- **Quick Actions** - Refresh, clear data, test Poppler
- **Directory Status** - File counts and availability
- **Deployment Info** - Local and cloud deployment guides

## 🔧 Configuration

### Environment Variables (.env)

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (defaults in config.py)
GEMINI_MODEL=gemini-2.0-flash
API_BATCH_SIZE=10
API_DELAY_SECONDS=2
DEBUG_MODE=False
```

### Path Configuration

All paths are centralized in `config.py`:
- **PDF_INPUT_DIR** - PDF invoice input location
- **PDF_OUTPUT_DIR** - OCR text output location
- **XLSX_OUTPUT_DIR** - Structured Excel output
- **DATE_VALIDATION_OUTPUT** - Validated data with dates
- **MONTHLY_SPLIT_OUTPUT** - Monthly split results

## 📊 Processing Workflow

```mermaid
graph LR
    A[📄 PDF Upload] --> B[🤖 AI OCR]
    B --> C[📝 Text Extraction]
    C --> D[📊 Excel Structuring]
    D --> E[✅ Data Validation]
    E --> F[📅 Date Processing]
    F --> G[📈 Final Report]
```

### Step-by-Step Process

1. **📄 PDF to Text (OCR)**
   - Upload PDF invoices through dashboard
   - Gemini AI extracts text from each page
   - Saves structured text files
   - Handles multi-page documents

2. **📝 Text to Excel**
   - Parses extracted text using AI
   - Identifies invoice fields automatically
   - Creates structured Excel with confidence scores
   - Validates extracted data

3. **✅ Data Validation**
   - Extracts service date ranges
   - Validates VAT calculations
   - Checks data quality and completeness
   - Flags potential issues

4. **📊 Results & Export**
   - View processed data in interactive tables
   - Download Excel files
   - Review metrics and statistics
   - Monitor processing history

## 🛠️ Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| **Language** | Python | 3.11+ |
| **Dashboard** | Streamlit | 1.28+ |
| **AI/ML** | Google Generative AI | Latest |
| **Model** | Gemini 2.0 Flash | Latest |
| **PDF Processing** | pdf2image | 1.17+ |
| **Image Processing** | Pillow | 10.0+ |
| **Data Processing** | pandas | 2.0+ |
| **Excel** | openpyxl | 3.1+ |
| **Date Parsing** | python-dateutil | 2.8+ |
| **Environment** | python-dotenv | 1.0+ |
| **Progress Bars** | tqdm | 4.65+ |

## 📋 Requirements

### System Requirements
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space for processing

### External Dependencies
- **Poppler** - PDF rendering library
  - Windows: Install via `pip install poppler-utils` or download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)
  - Linux: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`

### API Requirements
- Google Gemini API key (free tier available)
- Internet connection for API calls

## 🚀 Deployment

### Local Development

```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Run dashboard
streamlit run app_streamlit.py
```

### Streamlit Cloud Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Streamlit Cloud"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `app_streamlit.py` as main file
   - Add `GEMINI_API_KEY` in Secrets

3. **Configure Secrets**
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   ```

## 🎯 Key Features Explained

### 🤖 AI-Powered OCR
- Uses Google Gemini 2.0 Flash for superior accuracy
- Handles complex invoice layouts
- Multi-language support
- Confidence scoring for extracted data

### 📊 Intelligent Data Extraction
- Automatic field detection (invoice number, date, amounts, etc.)
- Smart parsing of line items
- VAT calculation and validation
- Quality scoring (1-10 scale)

### 📅 Date Intelligence
- Extracts service period dates from descriptions
- Handles various date formats (DD/MM/YYYY, DD.MM.YYYY, etc.)
- Date range validation
- Monthly splitting for multi-period invoices

### ✅ Data Validation
- Automatic data quality checks
- VAT calculation verification
- Field completeness validation
- Error detection and reporting

### 🎨 Modern UI/UX
- Professional gradient design
- Responsive layout
- Real-time feedback
- Interactive data tables
- Comprehensive error logging

## 📝 Usage Guide

### Basic Workflow

1. **Start the Dashboard**
   ```bash
   run_dashboard.bat
   ```

2. **Check System Status**
   - Go to Settings tab
   - Verify all system components are OK
   - Check API key configuration

3. **Process PDFs**
   - Navigate to "1️⃣ PDF → TXT" tab
   - Upload PDF invoice(s)
   - Click "Start PDF Processing"
   - Wait for completion

4. **Convert to Excel**
   - Go to "2️⃣ TXT → XLSX" tab
   - Click "Start TXT to XLSX Conversion"
   - Review progress

5. **Validate Data**
   - Navigate to "3️⃣ XLSX Validation" tab
   - Click "Start Data Validation"
   - Check validation results

6. **View Results**
   - Go to "📊 Results" tab
   - Review processed data
   - Download Excel files

### Tips & Best Practices

✅ **DO:**
- Upload clear, readable PDF files
- Check system status before processing
- Review error logs if issues occur
- Download results regularly
- Keep API key secure in `.env` file

❌ **DON'T:**
- Upload corrupted or password-protected PDFs
- Process extremely large batches at once
- Share your API key publicly
- Modify processing scripts during execution

## 🐛 Troubleshooting

### Common Issues

**Issue: "Poppler not found"**
```bash
# Solution: Install Poppler
pip install poppler-utils
# Or download manually and add to PATH
```

**Issue: "API key not configured"**
```bash
# Solution: Create .env file
echo GEMINI_API_KEY=your_key_here > .env
```

**Issue: "Streamlit not recognized"**
```bash
# Solution: Activate virtual environment
.\.venv\Scripts\activate
```

**Issue: "Unicode encoding error"**
- Fixed in latest version with Windows console encoding support
- Scripts now use `[SUCCESS]`, `[ERROR]` instead of emoji

**Issue: "Processing failed"**
- Check error log in Settings tab
- Verify API key is valid
- Ensure PDF is not corrupted
- Check internet connection

## 🔒 Security

- **API Keys** - Store in `.env`, never commit to Git
- **Data Privacy** - All processing is local except API calls
- **Git Ignore** - `.env` and sensitive data excluded
- **Cloud Deployment** - Use Streamlit secrets for API keys

## 📈 Recent Updates

### Latest Version (v2.0)

✅ **New Streamlit Dashboard**
- Modern, professional UI with gradient design
- Separate tabs for each workflow step
- Real-time progress tracking
- Interactive results visualization

✅ **Enhanced Processing**
- Improved error handling and logging
- Better file management for cloud deployment
- Temporary file cleanup
- Progress indicators

✅ **Better Typography**
- Optimized text sizes for readability
- Improved contrast (no more white on white)
- Consistent spacing throughout
- Professional color scheme

✅ **Fixed Encoding Issues**
- Windows console Unicode support
- Replaced emoji with text markers
- Better error messages
- UTF-8 encoding fixes

✅ **Improved Results Display**
- Detailed metrics (rows, columns, completion %)
- Interactive data preview
- Download functionality
- File metadata display

## 🤝 Contributing

This is a private project, but improvements are welcome:
1. Test new features thoroughly
2. Document changes clearly
3. Follow existing code style
4. Update README when adding features

## 📜 License

This project is private and proprietary. All rights reserved.

## 🆘 Support

For issues or questions:
1. Check the error log in Settings tab
2. Review DASHBOARD_README.md for detailed docs
3. Verify all requirements are installed
4. Check system status in Settings

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [pdf2image Guide](https://github.com/Belval/pdf2image)

---

**Made with ❤️ using Python, Streamlit, and Google Gemini AI**

*Last Updated: October 2024*
