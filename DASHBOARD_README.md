# 🤖 AI PDF Invoice Processor - Streamlit Dashboard

A clean, professional web dashboard for processing PDF invoices using AI.

## 🚀 Quick Start

### Option 1: Using the Batch File (Windows)
```bash
# Double-click run_dashboard.bat
# Or run from command line:
run_dashboard.bat
```

### Option 2: Using Command Line
```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app_streamlit.py
```

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Dependencies** installed: `pip install -r requirements.txt`
3. **Environment file** `.env` with your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```
4. **Poppler** installed for PDF processing (Windows)

## 🎯 Features

### 🏠 Home Tab
- Dashboard overview with file counts
- Quick status check
- Environment validation

### 📄 Run OCR Tab
- Upload multiple PDF invoices
- Process files through the full AI workflow:
  - Step 1: PDF → Text (OCR)
  - Step 2: Text → Structured Excel
  - Step 3: Date validation and extraction
- Real-time progress tracking
- Status messages and error handling

### 📊 Results Tab
- View processed Excel files
- Download results
- Data visualization

### ⚙️ Settings Tab
- Configuration overview
- Directory paths
- Deployment instructions

## 🔧 Configuration

The dashboard uses the same configuration as your existing scripts:
- **API settings** in `config.py`
- **Environment variables** in `.env`
- **File paths** automatically managed

## 🌐 Deployment

### Local Development
```bash
streamlit run app_streamlit.py
```

### Streamlit Cloud
1. Push your code to GitHub
2. Connect to Streamlit Cloud
3. Set environment variable: `GEMINI_API_KEY`
4. Deploy!

**Cloud-Ready Features:**
- ✅ Handles uploaded files in memory (no local file dependencies)
- ✅ Temporary file management for PDF processing
- ✅ Automatic cleanup after processing
- ✅ Works on both local and cloud environments

## 📁 File Structure
```
App.Simpla/
├── app_streamlit.py          # Main dashboard
├── run_dashboard.bat         # Windows launcher
├── DASHBOARD_README.md       # This file
├── config.py                 # Configuration
├── .env                      # API keys
├── requirements.txt          # Dependencies
└── Data-IN-OUT/             # Data directories
```

## 🎨 UI Features

- **Clean, professional design**
- **Responsive layout**
- **Real-time progress bars**
- **Status indicators**
- **File upload with drag & drop**
- **Data tables with download options**
- **Error handling and validation**

## 🔄 Workflow Integration

The dashboard seamlessly integrates your existing workflow:
1. **1.PDF_to_Txt.py** → OCR processing
2. **2.Txt_to_XLSX.py** → Data structuring
3. **4.XLSX_validation_dates.py** → Date validation

All functions are reused without modification, keeping your code simple and maintainable.

## 🚨 Troubleshooting

### Common Issues
1. **"GEMINI_API_KEY not configured"**
   - Check your `.env` file
   - Ensure the API key is valid

2. **"No module named 'streamlit'"**
   - Run: `pip install -r requirements.txt`

3. **PDF processing fails**
   - Install Poppler for Windows
   - Check PDF file format

4. **Dashboard won't start**
   - Check Python version (3.8+)
   - Verify all dependencies installed

### Getting Help
- Check the **Settings** tab for configuration details
- Review error messages in the dashboard
- Ensure all prerequisites are met

## 🎉 Success!

Once running, you'll have a professional web interface for your AI-powered PDF invoice processing workflow!
