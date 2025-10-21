# 🤖 AI PDF Invoice Processor - Streamlit Dashboard

> A modern, professional web dashboard for processing PDF invoices using Google Gemini AI

## ✨ What's New in v2.0

🎨 **Enhanced UI/UX**
- Modern gradient design with professional styling
- Optimized typography for better readability
- Improved contrast throughout (no more white on white text)
- Responsive layout with clean spacing

🔧 **Better Processing**
- Separate tabs for each workflow step
- Real-time progress tracking
- Enhanced error logging and recovery
- Cloud-ready file handling

📊 **Improved Results Display**
- Interactive Excel data preview
- Detailed metrics and statistics
- Download functionality
- File metadata and timestamps

🐛 **Bug Fixes**
- Fixed Windows console Unicode encoding errors
- Improved error messages (replaced emoji with text)
- Better temporary file cleanup
- Enhanced Poppler integration

## 🚀 Quick Start

### Option 1: Using the Batch Script (Windows) ⚡
```bash
# Double-click or run from command line:
run_dashboard.bat
```

This will:
1. ✅ Activate the virtual environment
2. ✅ Check dependencies
3. ✅ Launch the Streamlit dashboard
4. ✅ Open browser automatically

### Option 2: Manual Launch 💻
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Run the dashboard
streamlit run app_streamlit.py
```

The dashboard will open at: `http://localhost:8501`

## 📋 Prerequisites

### Required Software
- ✅ **Python 3.11+** - [Download](https://www.python.org/downloads/)
- ✅ **Git** (for version control) - [Download](https://git-scm.com/)

### Python Dependencies
All dependencies are in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

Get your API key: [Google AI Studio](https://makersuite.google.com/app/apikey)

### External Dependencies
**Poppler** (required for PDF processing):

**Windows:**
```bash
pip install poppler-utils
```
Or download manually: [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)

**Linux:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

## 🎯 Dashboard Overview

### 📑 Tab Structure

#### 🏠 **Home Tab**
Your dashboard homepage with:
- 🚀 **Welcome & Overview** - Introduction to features
- 📋 **Feature Cards** - PDF Upload, AI OCR, Data Validation
- 🔄 **Workflow Visualization** - Step-by-step process guide
- 📈 **Current Status** - Processing metrics and error counts

**What You See:**
- Last processing status
- Processing time
- Error count
- System health indicators

---

#### 1️⃣ **PDF → TXT Tab**
Upload and process PDF invoices:

**Features:**
- 📤 Multi-file upload support
- 🤖 AI-powered OCR using Gemini
- 📊 Real-time progress bar
- ✅ Success/failure status for each file
- 🔄 Processing status messages

**How to Use:**
1. Click "Browse files" or drag & drop PDFs
2. Review selected files
3. Click "🚀 Start PDF Processing"
4. Monitor progress in real-time
5. Check status messages

**Output:** Text files in `Data-IN-OUT/01. Gemini OCR PDF to TXT/OUT/`

---

#### 2️⃣ **TXT → XLSX Tab**
Convert extracted text to structured Excel:

**Features:**
- 📝 Automatic field detection
- 🎯 Intelligent data extraction
- 📊 Quality scoring
- ✅ Data validation
- 🔄 Batch processing

**How to Use:**
1. Ensure PDF processing is complete
2. Click "🔄 Start TXT to XLSX Conversion"
3. Wait for conversion to complete
4. Check success message

**Output:** Structured Excel in `Data-IN-OUT/02. Structurare TXT to XLSX/`

---

#### 3️⃣ **XLSX Validation Tab**
Validate and extract service dates:

**Features:**
- 📅 Smart date extraction
- ✅ VAT validation
- 🔍 Data quality checks
- 📊 Field completeness
- 🔄 Batch validation

**How to Use:**
1. Ensure TXT→XLSX conversion is done
2. Click "✅ Start Data Validation"
3. Monitor validation progress
4. Review validation results

**Output:** Validated data in `Data-IN-OUT/04. Date si validare XLSX/`

---

#### 📊 **Results Tab**
View and download processed data:

**Features:**
- 📄 **Interactive Data Preview** - Full Excel table view
- 📊 **Summary Metrics:**
  - Total rows
  - Column count
  - Filled cells
  - Completion percentage
- 📥 **Download Functionality** - Export Excel files
- 🔄 **Refresh Data** - Update view
- 📅 **File Metadata** - Size, timestamp, location

**What You See:**
- 📝 **Structured Data (Step 2)** - Extracted invoice data
- ✅ **Validated Data (Step 3)** - Data with dates and validation

**How to Use:**
1. Complete workflow steps
2. Navigate to Results tab
3. Review data in interactive tables
4. Click "📥 Download" to export
5. Use "🔄 Refresh" to update

---

#### ⚙️ **Settings Tab**
System configuration and diagnostics:

**System Status Overview:**
- 🟢 Environment status
- 🔑 API key configuration
- 📁 Directory availability
- 🛠️ Poppler installation

**Error Log & Status:**
- 📋 Filterable error log (ERROR, WARNING, INFO, SUCCESS)
- ⏰ Timestamped entries
- 🎨 Color-coded messages
- 🔄 Last 20 entries displayed
- 🗑️ Clear log functionality

**Configuration Display:**
- 🤖 AI model settings
- 🔑 API configuration
- 📁 Directory paths
- ⚙️ Processing settings

**Quick Actions:**
- 🔄 Refresh system status
- 🗑️ Clear all processed data
- 🧪 Test Poppler installation

**Directory Status:**
- 📥 PDF Input (file count)
- 📤 TXT Output (file count)
- 📊 XLSX Output (file count)
- ✅ Validation Output (file count)

**Deployment Information:**
- 💻 Local development instructions
- ☁️ Streamlit Cloud deployment guide
- 🔐 Environment variable setup

---

## 📊 Workflow Process

```
┌─────────────────────────────────────────────────────────┐
│                     1. PDF Upload                       │
│  Upload single or multiple PDF invoice files           │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              2. AI OCR Processing                       │
│  Gemini extracts text from each PDF page               │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│           3. Text to Excel Conversion                   │
│  AI structures data into Excel with confidence scores   │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│          4. Data Validation & Dating                    │
│  Extract service dates and validate VAT                 │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              5. Results & Export                        │
│  View data, download Excel, review metrics             │
└─────────────────────────────────────────────────────────┘
```

## 🎨 UI/UX Features

### Modern Design Elements
- 🌈 **Gradient Headers** - Eye-catching purple/blue gradients
- 💳 **Metric Cards** - Animated cards with hover effects
- 📋 **Step Cards** - Clear workflow visualization
- 🎯 **Status Indicators** - Color-coded success/error/warning
- 📊 **Interactive Tables** - Sortable, filterable data views

### Typography
- ✅ Optimized text sizes (comfortable reading)
- ✅ High contrast (dark text on light backgrounds)
- ✅ Consistent spacing and padding
- ✅ Professional font (Inter family)
- ✅ Responsive layout

### Color Scheme
- **Primary:** Purple gradient (#667eea → #764ba2)
- **Success:** Green (#28a745)
- **Error:** Red (#dc3545)
- **Warning:** Yellow (#ffc107)
- **Info:** Blue (#17a2b8)
- **Text:** Dark gray (#2c3e50)
- **Background:** Light gray (#f8f9fa → #e9ecef)

## 🔧 Configuration

### System Status Indicators

| Indicator | Meaning |
|-----------|---------|
| ✅ OK | Component working correctly |
| ❌ Error | Component has issues |
| ⚠️ Warning | Component needs attention |
| 🔄 Processing | Operation in progress |

### Error Log Types

| Type | Color | Meaning |
|------|-------|---------|
| `SUCCESS` | Green | Operation completed successfully |
| `INFO` | Blue | Informational message |
| `WARNING` | Yellow | Non-critical issue |
| `ERROR` | Red | Critical error occurred |

## 🐛 Troubleshooting

### Common Issues & Solutions

#### Issue: "Streamlit not recognized"
```bash
# Solution: Activate virtual environment first
.\.venv\Scripts\activate
streamlit run app_streamlit.py
```

#### Issue: "Poppler not found"
```bash
# Solution: Install Poppler
pip install poppler-utils

# Or test in Settings tab
Click "🧪 Test Poppler" button
```

#### Issue: "API key not configured"
```bash
# Solution: Create/check .env file
echo GEMINI_API_KEY=your_key_here > .env

# Verify in Settings tab → System Status
```

#### Issue: "Processing failed"
**Steps to diagnose:**
1. Go to Settings tab
2. Check System Status (all should be ✅)
3. Review Error Log for details
4. Filter by "ERROR" to see issues
5. Check if PDF is corrupted
6. Verify internet connection

#### Issue: "Unicode encoding error"
**Fixed in current version!**
- All emoji replaced with text markers
- Windows console encoding handled automatically
- UTF-8 support enabled

#### Issue: "White text on white background"
**Fixed in current version!**
- Background changed to light gray (#f8f9fa)
- Text color changed to dark (#2c3e50)
- High contrast throughout

## 📚 Tips & Best Practices

### ✅ DO:
- **Check System Status** before processing (Settings tab)
- **Upload clear PDFs** - Good scans work best
- **Monitor Error Log** - Check for issues during processing
- **Download results regularly** - Don't lose processed data
- **Keep .env secure** - Never commit to Git

### ❌ DON'T:
- **Don't upload corrupted PDFs** - Check file integrity first
- **Don't process huge batches** - Break into smaller groups
- **Don't share API keys** - Keep credentials private
- **Don't modify during processing** - Wait for completion
- **Don't ignore errors** - Review error log promptly

### 🎯 Best Practices:
1. **Start Small** - Test with 1-2 PDFs first
2. **Check Results** - Verify data quality after each step
3. **Use Settings Tab** - Monitor system health regularly
4. **Clear Old Data** - Use "Clear Data" when needed
5. **Read Error Logs** - Understand what went wrong

## 🚀 Deployment

### Local Development

```bash
# 1. Activate environment
.\.venv\Scripts\activate

# 2. Run dashboard
streamlit run app_streamlit.py

# 3. Access in browser
http://localhost:8501
```

### Streamlit Cloud Deployment

**Step 1: Prepare Repository**
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

**Step 2: Deploy on Streamlit Cloud**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Choose `app_streamlit.py` as main file
6. Click "Deploy"

**Step 3: Configure Secrets**
In Streamlit Cloud dashboard:
1. Go to App Settings
2. Click "Secrets"
3. Add:
```toml
GEMINI_API_KEY = "your_actual_api_key_here"
```

**Step 4: Verify Deployment**
1. Check app is running
2. Test system status
3. Process a sample PDF
4. Verify results

## 📖 Usage Examples

### Example 1: Process Single PDF

1. **Navigate to "1️⃣ PDF → TXT"**
2. **Upload:** Click "Browse files" → Select PDF
3. **Process:** Click "🚀 Start PDF Processing"
4. **Wait:** Monitor progress bar
5. **Continue to "2️⃣ TXT → XLSX"**
6. **Convert:** Click "🔄 Start TXT to XLSX Conversion"
7. **Continue to "3️⃣ XLSX Validation"**
8. **Validate:** Click "✅ Start Data Validation"
9. **View Results:** Go to "📊 Results" tab
10. **Download:** Click "📥 Download" button

### Example 2: Batch Processing

1. **Prepare:** Collect multiple PDFs
2. **Upload:** Select all PDFs at once (Ctrl+Click)
3. **Process:** Follow same steps as Example 1
4. **Monitor:** Watch progress for each file
5. **Review:** Check Results tab for all files
6. **Export:** Download all processed data

### Example 3: Check System Health

1. **Go to Settings Tab** (⚙️)
2. **Check System Status:**
   - ✅ Environment
   - ✅ API Key
   - ✅ Directories
   - ✅ Poppler
3. **Review Error Log** (filter if needed)
4. **Test Poppler:** Click "🧪 Test Poppler"
5. **Clear old data if needed:** "🗑️ Clear All Data"

## 📊 Data Flow

```
PDF Files
    ↓
[Upload in Dashboard]
    ↓
Gemini AI OCR
    ↓
Text Files (.txt)
    ↓
AI Data Extraction
    ↓
Excel Files (.xlsx)
    ↓
Data Validation
    ↓
Final Excel with Dates
    ↓
[Download Results]
```

## 🔐 Security Notes

- **API Keys:** Always use `.env`, never hardcode
- **Git Ignore:** `.env` is excluded from version control
- **Cloud Secrets:** Use Streamlit secrets for deployment
- **Data Privacy:** All processing is local except API calls
- **File Cleanup:** Temporary files are automatically deleted

## 📈 Performance Tips

- **Small Batches:** Process 10-20 PDFs at a time
- **Clear Data:** Use "Clear Data" button periodically
- **Monitor RAM:** Watch system resources during processing
- **API Limits:** Respect Gemini API rate limits
- **Network:** Stable internet for API calls

## 🆘 Support

### Getting Help

1. **Check Settings Tab** - System status and error log
2. **Review Error Log** - Filter by ERROR type
3. **Test Components** - Use "Test Poppler" button
4. **Check README** - Main project documentation
5. **Review Configuration** - Verify all settings

### Common Questions

**Q: Why is processing slow?**
A: AI OCR takes time. Processing 1 page = ~5-10 seconds.

**Q: Can I process password-protected PDFs?**
A: No, PDFs must be unprotected.

**Q: What PDF formats are supported?**
A: All standard PDF formats. Best results with text-based PDFs.

**Q: How many PDFs can I process at once?**
A: Recommended: 10-20 at a time for best performance.

**Q: Where is my data stored?**
A: Locally in `Data-IN-OUT/` folders. Nothing stored in cloud.

## 📝 Version History

### v2.0 (Current)
- ✅ Complete UI/UX redesign
- ✅ Separate workflow tabs
- ✅ Enhanced results display
- ✅ Fixed encoding issues
- ✅ Improved error handling
- ✅ Cloud-ready deployment

### v1.0 (Initial)
- Basic Streamlit dashboard
- PDF processing workflow
- Simple results display
- Basic error handling

## 🎓 Learn More

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Gemini API](https://ai.google.dev/docs)
- [pdf2image Guide](https://github.com/Belval/pdf2image)
- [pandas Tutorials](https://pandas.pydata.org/docs/)

---

**Made with ❤️ using Streamlit and Google Gemini AI**

*Last Updated: October 2024*
