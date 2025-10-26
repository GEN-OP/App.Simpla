"""
AI-Powered PDF Invoice Processor - Enhanced Streamlit Dashboard
==============================================================

A modern, professional dashboard for processing PDF invoices using AI.
Integrates existing workflow scripts with dedicated tabs for each processing step.
k
Deployment Instructions:
- Local: streamlit run app_streamlit.py
- Cloud: Push to GitHub and deploy via Streamlit Cloud
- Ensure .env file with GEMINI_API_KEY is configured
"""

import streamlit as st
import os
import sys
import pandas as pd
import tempfile
import shutil
import re
from pathlib import Path
import time
from datetime import datetime

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our existing modules
from config import config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize session state for error logging and status tracking
if 'error_log' not in st.session_state:
    st.session_state.error_log = []
if 'last_processing_status' not in st.session_state:
    st.session_state.last_processing_status = "Ready"
if 'processing_start_time' not in st.session_state:
    st.session_state.processing_start_time = None
if 'processing_end_time' not in st.session_state:
    st.session_state.processing_end_time = None

# Page configuration
st.set_page_config(
    page_title="AI PDF Invoice Processor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for modern design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 1.25rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.25);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 50%, rgba(255,255,255,0.1) 100%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        font-size: 0.8rem;
        opacity: 0.9;
        margin: 0.3rem 0 0 0;
        font-weight: 500;
    }
    
    /* Status Styles */
    .status-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #28a745;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
        font-weight: 500;
    }
    
    .status-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #dc3545;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
        font-weight: 500;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #ffc107;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2);
        font-weight: 500;
    }
    
    .status-info {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #17a2b8;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(23, 162, 184, 0.2);
        font-weight: 500;
    }
    
    /* Workflow Steps */
    .workflow-step {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.25rem;
        border-radius: 15px;
        margin: 0.75rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .workflow-step:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
    }
    
    .workflow-step-number {
        position: absolute;
        top: -10px;
        left: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
    }
    
    .workflow-step h3 {
        margin: 0.5rem 0 0.5rem 0;
        color: #2c3e50;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .workflow-step p {
        margin: 0;
        color: #495057;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 12px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 12px;
        padding: 15px 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        border: 2px solid rgba(255,255,255,0.2);
        transform: translateY(-2px);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Error Log */
    .error-log {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 15px;
        padding: 1.5rem;
        max-height: 500px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        box-shadow: inset 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .error-entry {
        margin: 1rem 0;
        padding: 1.2rem;
        border-radius: 12px;
        transition: all 0.3s ease;
        border-left: 5px solid;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .error-entry:hover {
        transform: translateX(8px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    .error-entry.ERROR {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        border-left-color: #dc3545;
    }
    
    .error-entry.WARNING {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        border-left-color: #ffc107;
    }
    
    .error-entry.INFO {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        border-left-color: #17a2b8;
    }
    
    .error-entry.SUCCESS {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        border-left-color: #28a745;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* File Uploader */
    .stFileUploader > div {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 2rem;
        border: 3px dashed #007bff;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .stFileUploader > div:hover {
        border-color: #0056b3;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        transform: scale(1.02);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Custom Scrollbar */
    .error-log::-webkit-scrollbar {
        width: 10px;
    }
    
    .error-log::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 5px;
    }
    
    .error-log::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 5px;
    }
    
    .error-log::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.25rem;
        border-radius: 15px;
        margin: 0.75rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 2px solid #dee2e6;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        border-color: #667eea;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.4rem;
    }
    
    .feature-description {
        color: #495057;
        line-height: 1.5;
        font-size: 0.85rem;
    }
    
    /* Step Cards */
    .step-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 2px solid #dee2e6;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .step-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        border-color: #667eea;
    }
    
    .step-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .step-number {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
    }
    
    .step-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .step-description {
        color: #495057;
        line-height: 1.5;
        margin-bottom: 0;
        font-size: 0.9rem;
    }
    
    .step-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
    }
    
    .step-status.ready {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
    }
    
    .step-status.processing {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
    }
    
    .step-status.completed {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
    }
    
    .step-status.error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

def log_error(error_message, error_type="ERROR"):
    """Log error to session state"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.error_log.append({
        "timestamp": timestamp,
        "type": error_type,
        "message": error_message
    })
    # Keep only last 50 errors
    if len(st.session_state.error_log) > 50:
        st.session_state.error_log = st.session_state.error_log[-50:]

def log_status(status_message, status_type="INFO"):
    """Log status message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.error_log.append({
        "timestamp": timestamp,
        "type": status_type,
        "message": status_message
    })
    st.session_state.last_processing_status = status_message

def get_system_status():
    """Get comprehensive system status"""
    status = {
        "environment": "Unknown",
        "api_key": "Unknown",
        "directories": "Unknown",
        "poppler": "Unknown",
        "last_error": None,
        "processing_time": None
    }
    
    # Check environment
    env_ok, env_message = check_environment()
    status["environment"] = "✅ OK" if env_ok else "❌ Error"
    
    # Check API key
    if config.GEMINI_API_KEY and config.GEMINI_API_KEY != "your_gemini_api_key_here":
        status["api_key"] = "✅ Configured"
    else:
        status["api_key"] = "❌ Missing"
    
    # Check directories
    dirs_ok = all(os.path.exists(d) for d in [
        config.PDF_INPUT_DIR, config.PDF_OUTPUT_DIR, 
        config.XLSX_OUTPUT_DIR, config.DATE_VALIDATION_OUTPUT
    ])
    status["directories"] = "✅ OK" if dirs_ok else "❌ Missing"
    
    # Check Poppler
    try:
        import subprocess
        result = subprocess.run(['pdftoppm', '-h'], capture_output=True, text=True)
        status["poppler"] = "✅ Installed" if result.returncode == 0 else "❌ Missing"
    except:
        status["poppler"] = "❌ Missing"
    
    # Get last error
    if st.session_state.error_log:
        last_error = st.session_state.error_log[-1]
        if last_error["type"] in ["ERROR", "WARNING"]:
            status["last_error"] = f"{last_error['timestamp']}: {last_error['message']}"
    
    # Calculate processing time
    if st.session_state.processing_start_time and st.session_state.processing_end_time:
        duration = st.session_state.processing_end_time - st.session_state.processing_start_time
        status["processing_time"] = f"{duration.total_seconds():.1f}s"
    
    return status

def check_environment():
    """Check if environment is properly configured"""
    try:
        # Check API key
        api_key = config.GEMINI_API_KEY
        if not api_key or api_key == "your_gemini_api_key_here":
            return False, "GEMINI_API_KEY not configured"
        
        # Check directories
        required_dirs = [
            config.PDF_INPUT_DIR, config.PDF_OUTPUT_DIR,
            config.XLSX_OUTPUT_DIR, config.DATE_VALIDATION_OUTPUT
        ]
        
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                return False, f"Directory missing: {dir_path}"
        
        return True, "Environment OK"
    except Exception as e:
        return False, f"Environment check failed: {str(e)}"

def run_pdf_to_txt(uploaded_files, progress_bar, status_placeholder):
    """Run PDF to TXT conversion with uploaded files - Cloud compatible"""
    try:
        # Using PyMuPDF instead of pdf2image for Streamlit Cloud (no Poppler needed)
        import fitz  # PyMuPDF
        import io
        from PIL import Image
        import google.generativeai as genai
        from pathlib import Path
        import tempfile
        
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # Create temporary directory for uploaded files
        temp_dir = Path(tempfile.gettempdir()) / "streamlit_pdf_uploads"
        temp_dir.mkdir(exist_ok=True)
        
        total_files = len(uploaded_files)
        processed = 0
        
        for uploaded_file in uploaded_files:
            log_status(f"Processing: {uploaded_file.name}", "INFO")
            status_placeholder.info(f"🔄 Processing: {uploaded_file.name}")
            
            # Save uploaded file to temporary location
            temp_pdf_path = temp_dir / uploaded_file.name
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Open PDF with PyMuPDF (works everywhere, no Poppler needed)
                doc = fitz.open(str(temp_pdf_path))
                total_pages = len(doc)
                
                # Process each page with Gemini
                full_text = ""
                for page_num in range(total_pages):
                    log_status(f"Processing page {page_num+1}/{total_pages} of {uploaded_file.name}", "INFO")
                    
                    # Render page to image using PyMuPDF
                    page = doc[page_num]
                    pix = page.get_pixmap(dpi=150)  # 150 DPI for good quality
                    
                    # Convert to PIL Image
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Convert image to bytes for Gemini
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Use Gemini to extract text
                    model = genai.GenerativeModel(config.GEMINI_MODEL)
                    response = model.generate_content([
                        "Extract all text from this invoice image. Include all numbers, dates, amounts, and text. Be precise and complete.",
                        {
                            "mime_type": "image/png",
                            "data": img_byte_arr
                        }
                    ])
                    
                    if response.text:
                        full_text += f"\n--- Page {page_num+1} ---\n{response.text}\n"
                
                # Close PDF document
                doc.close()
                
                # Save extracted text
                base_name = os.path.splitext(uploaded_file.name)[0]
                output_file = os.path.join(config.PDF_OUTPUT_DIR, f"{base_name}_ocr.txt")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(full_text)
                
                processed += 1
                log_status(f"Successfully processed: {uploaded_file.name}", "SUCCESS")
                status_placeholder.success(f"✅ Completed: {uploaded_file.name}")
                
            finally:
                # Clean up temporary file
                try:
                    os.remove(temp_pdf_path)
                except Exception as cleanup_error:
                    log_error(f"Could not delete temporary file: {cleanup_error}", "WARNING")
                    status_placeholder.warning(f"⚠️ Could not delete temporary file: {cleanup_error}")
        
        # Clean up temporary directory
        try:
            if temp_dir.exists() and not any(temp_dir.iterdir()):
                temp_dir.rmdir()
        except Exception:
            pass
        
        return True, f"Successfully processed {processed}/{total_files} PDF files"
        
    except Exception as e:
        log_error(f"PDF to TXT conversion failed: {str(e)}", "ERROR")
        return False, f"PDF to TXT conversion failed: {str(e)}"

def run_txt_to_xlsx():
    """Run TXT to XLSX conversion"""
    try:
        import subprocess
        result = subprocess.run([sys.executable, "2.Txt_to_XLSX.py"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            log_status("TXT to XLSX conversion completed successfully", "SUCCESS")
            return True, "TXT to XLSX conversion completed successfully"
        else:
            log_error(f"TXT to XLSX conversion failed: {result.stderr}", "ERROR")
            return False, f"TXT to XLSX conversion failed: {result.stderr}"
    except Exception as e:
        log_error(f"TXT to XLSX conversion failed: {str(e)}", "ERROR")
        return False, f"TXT to XLSX conversion failed: {str(e)}"

def run_xlsx_validation():
    """Run XLSX validation and date processing"""
    try:
        import subprocess
        result = subprocess.run([sys.executable, "4.XLSX_validation_dates.py"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            log_status("XLSX validation completed successfully", "SUCCESS")
            return True, "XLSX validation completed successfully"
        else:
            log_error(f"XLSX validation failed: {result.stderr}", "ERROR")
            return False, f"XLSX validation failed: {result.stderr}"
    except Exception as e:
        log_error(f"XLSX validation failed: {str(e)}", "ERROR")
        return False, f"XLSX validation failed: {str(e)}"

def display_results():
    """Display processing results with enhanced visualization"""
    st.markdown("## 📊 Processing Results")
    
    # Check for output files
    output_files = []
    
    # Check XLSX output
    xlsx_file = os.path.join(config.XLSX_OUTPUT_DIR, "2.structured_extract.xlsx")
    if os.path.exists(xlsx_file):
        output_files.append(("📝 Structured Data (Step 2)", xlsx_file, "success"))
    
    # Check validation output
    validation_file = os.path.join(config.DATE_VALIDATION_OUTPUT, "4.transformed_data.xlsx")
    if os.path.exists(validation_file):
        output_files.append(("✅ Validated Data (Step 3)", validation_file, "info"))
    
    if output_files:
        for title, file_path, status_type in output_files:
            # Display title with styling
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1rem; border-radius: 10px; margin: 1rem 0; color: white;">
                <h3 style="margin: 0; color: white;">{title}</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">
                    File: {os.path.basename(file_path)} | 
                    Size: {os.path.getsize(file_path) / 1024:.1f} KB
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                df = pd.read_excel(file_path)
                
                # Display summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Total Rows", len(df))
                with col2:
                    st.metric("📋 Columns", len(df.columns))
                with col3:
                    # Count non-empty cells
                    non_empty = df.notna().sum().sum()
                    st.metric("✓ Filled Cells", f"{non_empty:,}")
                with col4:
                    # Calculate completion percentage
                    total_cells = len(df) * len(df.columns)
                    completion = (non_empty / total_cells * 100) if total_cells > 0 else 0
                    st.metric("📈 Completion", f"{completion:.1f}%")
                
                # Display dataframe with better styling
                st.markdown("#### 📄 Data Preview")
                st.dataframe(
                    df, 
                    use_container_width=True, 
                    height=400,
                    hide_index=False
                )
                
                # Download and action buttons
                col1, col2, col3 = st.columns([2, 2, 3])
                with col1:
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label=f"📥 Download {title.split('(')[0].strip()}",
                            data=f.read(),
                            file_name=os.path.basename(file_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                
                with col2:
                    if st.button(f"🔄 Refresh Data", key=f"refresh_{file_path}", use_container_width=True):
                        st.rerun()
                
                with col3:
                    st.info(f"📅 Last modified: {datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')}")
                
                st.markdown("---")
                
            except Exception as e:
                st.error(f"❌ Error reading {file_path}: {str(e)}")
                log_error(f"Error reading Excel file: {str(e)}", "ERROR")
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); 
                    padding: 2rem; border-radius: 15px; text-align: center; margin: 2rem 0;
                    border-left: 5px solid #ffc107;">
            <h3 style="color: #856404; margin: 0 0 1rem 0;">⚠️ No Results Available</h3>
            <p style="color: #856404; margin: 0; font-size: 1.1rem;">
                Please run the processing workflow first to generate results.
            </p>
            <p style="color: #856404; margin: 1rem 0 0 0; opacity: 0.8;">
                Go to the workflow tabs above to process your PDF invoices.
            </p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI PDF Invoice Processor</h1>
        <p>Transform PDF invoices into structured data with AI-powered OCR and validation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔧 System Status")
        
        # Get system status
        status = get_system_status()
        
        # Display status metrics
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{status['environment']}</div>
                <div class="metric-label">Environment</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{status['api_key']}</div>
                <div class="metric-label">API Key</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{status['directories']}</div>
                <div class="metric-label">Directories</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{status['poppler']}</div>
                <div class="metric-label">Poppler</div>
            </div>
            """, unsafe_allow_html=True)
        
        # File counts
        st.markdown("## 📁 File Counts")
        
        # Count files in each directory
        pdf_input_count = len([f for f in os.listdir(config.PDF_INPUT_DIR) if f.endswith('.pdf')]) if os.path.exists(config.PDF_INPUT_DIR) else 0
        txt_output_count = len([f for f in os.listdir(config.PDF_OUTPUT_DIR) if f.endswith('.txt')]) if os.path.exists(config.PDF_OUTPUT_DIR) else 0
        xlsx_count = len([f for f in os.listdir(config.XLSX_OUTPUT_DIR) if f.endswith('.xlsx')]) if os.path.exists(config.XLSX_OUTPUT_DIR) else 0
        
        st.metric("📄 PDF Input", pdf_input_count)
        st.metric("📝 TXT Output", txt_output_count)
        st.metric("📊 XLSX Files", xlsx_count)
        
        # Quick actions
        st.markdown("## ⚡ Quick Actions")
        
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()
        
        if st.button("🗑️ Clear Data", use_container_width=True):
            # Clear output directories
            for dir_path in [config.PDF_OUTPUT_DIR, config.XLSX_OUTPUT_DIR, config.DATE_VALIDATION_OUTPUT]:
                if os.path.exists(dir_path):
                    for file in os.listdir(dir_path):
                        os.remove(os.path.join(dir_path, file))
            st.rerun()
        
        if st.button("📋 Clear Error Log", use_container_width=True):
            st.session_state.error_log = []
            st.rerun()
    
    # Main content with tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Home", 
        "1️⃣ PDF → TXT", 
        "2️⃣ TXT → XLSX", 
        "3️⃣ XLSX Validation", 
        "📊 Results", 
        "⚙️ Settings"
    ])
    
    with tab1:
        st.markdown("## 🚀 Welcome to AI PDF Invoice Processor")
        
        # Features overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">PDF Upload</div>
                <div class="feature-description">Upload single or multiple PDF invoices for processing</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">AI OCR</div>
                <div class="feature-description">Advanced AI-powered text extraction using Google Gemini</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Data Validation</div>
                <div class="feature-description">Automatic data structuring and validation with date processing</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Workflow steps
        st.markdown("## 🔄 Processing Workflow")
        
        st.markdown("""
        <div class="workflow-step">
            <div class="workflow-step-number">1</div>
            <h3>📄 PDF to Text Conversion</h3>
            <p>Upload PDF invoices and convert them to text using AI-powered OCR technology. Each page is processed individually for maximum accuracy.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="workflow-step">
            <div class="workflow-step-number">2</div>
            <h3>📝 Text to Excel Structuring</h3>
            <p>Transform extracted text into structured Excel format with proper columns and data organization for easy analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="workflow-step">
            <div class="workflow-step-number">3</div>
            <h3>✅ Data Validation & Processing</h3>
            <p>Validate and process the structured data, including date formatting and data quality checks for final output.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Current status
        st.markdown("## 📈 Current Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{st.session_state.last_processing_status}</div>
                <div class="metric-label">Last Status</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            processing_time = "N/A"
            if st.session_state.processing_start_time and st.session_state.processing_end_time:
                duration = st.session_state.processing_end_time - st.session_state.processing_start_time
                processing_time = f"{duration.total_seconds():.1f}s"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{processing_time}</div>
                <div class="metric-label">Processing Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            error_count = len([log for log in st.session_state.error_log if log["type"] == "ERROR"])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{error_count}</div>
                <div class="metric-label">Errors</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("## 1️⃣ PDF to Text Conversion")
        
        st.markdown("""
        <div class="step-card">
            <div class="step-number">1</div>
            <div class="step-title">Upload PDF Invoices</div>
            <div class="step-description">Select one or more PDF invoice files to process. The system will extract text from each page using AI-powered OCR.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload PDF invoice files for text extraction"
        )
        
        if uploaded_files:
            st.success(f"📁 {len(uploaded_files)} file(s) selected for processing")
            
            # Process button
            if st.button("🚀 Start PDF Processing", type="primary", use_container_width=True):
                st.session_state.processing_start_time = datetime.now()
                
                # Progress bar
                progress_bar = st.progress(0)
                status_placeholder = st.empty()
                
                # Process files
                success, message = run_pdf_to_txt(uploaded_files, progress_bar, status_placeholder)
                
                st.session_state.processing_end_time = datetime.now()
                
                if success:
                    progress_bar.progress(100)
                    st.success(f"✅ {message}")
                    log_status("PDF processing completed successfully", "SUCCESS")
                else:
                    st.error(f"❌ {message}")
                    log_error(f"PDF processing failed: {message}", "ERROR")
        else:
            st.info("👆 Please upload PDF files to begin processing")
    
    with tab3:
        st.markdown("## 2️⃣ Text to Excel Structuring")
        
        st.markdown("""
        <div class="step-card">
            <div class="step-number">2</div>
            <div class="step-title">Convert Text to Structured Excel</div>
            <div class="step-description">Transform extracted text files into structured Excel format with proper columns and data organization.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if TXT files exist
        txt_files = []
        if os.path.exists(config.PDF_OUTPUT_DIR):
            txt_files = [f for f in os.listdir(config.PDF_OUTPUT_DIR) if f.endswith('.txt')]
        
        if txt_files:
            st.success(f"📝 Found {len(txt_files)} text file(s) ready for processing")
            
            # Process button
            if st.button("🔄 Start TXT to XLSX Conversion", type="primary", use_container_width=True):
                st.session_state.processing_start_time = datetime.now()
                
                # Progress bar
                progress_bar = st.progress(0)
                status_placeholder = st.empty()
                
                status_placeholder.info("🔄 Converting text files to Excel format...")
                progress_bar.progress(50)
                
                # Process files
                success, message = run_txt_to_xlsx()
                
                st.session_state.processing_end_time = datetime.now()
                
                if success:
                    progress_bar.progress(100)
                    st.success(f"✅ {message}")
                    log_status("TXT to XLSX conversion completed successfully", "SUCCESS")
                else:
                    st.error(f"❌ {message}")
                    log_error(f"TXT to XLSX conversion failed: {message}", "ERROR")
        else:
            st.warning("⚠️ No text files found. Please complete PDF processing first.")
    
    with tab4:
        st.markdown("## 3️⃣ XLSX Validation & Date Processing")
        
        st.markdown("""
        <div class="step-card">
            <div class="step-number">3</div>
            <div class="step-title">Validate and Process Data</div>
            <div class="step-description">Validate the structured Excel data, process dates, and perform final data quality checks.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if XLSX files exist
        xlsx_files = []
        if os.path.exists(config.XLSX_OUTPUT_DIR):
            xlsx_files = [f for f in os.listdir(config.XLSX_OUTPUT_DIR) if f.endswith('.xlsx')]
        
        if xlsx_files:
            st.success(f"📊 Found {len(xlsx_files)} Excel file(s) ready for validation")
            
            # Process button
            if st.button("✅ Start Data Validation", type="primary", use_container_width=True):
                st.session_state.processing_start_time = datetime.now()
                
                # Progress bar
                progress_bar = st.progress(0)
                status_placeholder = st.empty()
                
                status_placeholder.info("🔄 Validating and processing data...")
                progress_bar.progress(50)
                
                # Process files
                success, message = run_xlsx_validation()
                
                st.session_state.processing_end_time = datetime.now()
                
                if success:
                    progress_bar.progress(100)
                    st.success(f"✅ {message}")
                    log_status("Data validation completed successfully", "SUCCESS")
                else:
                    st.error(f"❌ {message}")
                    log_error(f"Data validation failed: {message}", "ERROR")
        else:
            st.warning("⚠️ No Excel files found. Please complete TXT to XLSX conversion first.")
    
    with tab5:
        display_results()
    
    with tab6:
        st.markdown("## ⚙️ Settings & System Status")
        
        # System Status Overview
        st.markdown("### 🔧 System Status Overview")
        
        status = get_system_status()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{status['environment']}</div>
                <div class="metric-label">Environment</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{status['api_key']}</div>
                <div class="metric-label">API Key</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{status['directories']}</div>
                <div class="metric-label">Directories</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{status['poppler']}</div>
                <div class="metric-label">Poppler</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Error Log & Status
        st.markdown("### 📋 Error Log & Status")
        
        # Filter options
        col1, col2 = st.columns([3, 1])
        with col1:
            log_filter = st.selectbox("Filter by type:", ["All", "ERROR", "WARNING", "INFO", "SUCCESS"])
        with col2:
            if st.button("🗑️ Clear Log", use_container_width=True):
                st.session_state.error_log = []
                st.rerun()
        
        # Display filtered logs
        filtered_logs = st.session_state.error_log
        if log_filter != "All":
            filtered_logs = [log for log in st.session_state.error_log if log["type"] == log_filter]
        
        if filtered_logs:
            st.markdown('<div class="error-log">', unsafe_allow_html=True)
            for log in reversed(filtered_logs[-20:]):  # Show last 20 entries
                st.markdown(f"""
                <div class="error-entry {log['type']}">
                    <strong>[{log['timestamp']}] {log['type']}:</strong> {log['message']}
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No log entries found.")
        
        # Configuration
        st.markdown("### ⚙️ Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**API Configuration:**")
            st.text(f"Model: {config.GEMINI_MODEL}")
            st.text(f"API Key: {'Configured' if config.GEMINI_API_KEY and config.GEMINI_API_KEY != 'your_gemini_api_key_here' else 'Not configured'}")
        
        with col2:
            st.markdown("**Processing Settings:**")
            st.text(f"PDF Input: {config.PDF_INPUT_DIR}")
            st.text(f"TXT Output: {config.PDF_OUTPUT_DIR}")
            st.text(f"XLSX Output: {config.XLSX_OUTPUT_DIR}")
            st.text(f"Validation Output: {config.DATE_VALIDATION_OUTPUT}")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Status", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All Data", use_container_width=True):
                # Clear output directories
                for dir_path in [config.PDF_OUTPUT_DIR, config.XLSX_OUTPUT_DIR, config.DATE_VALIDATION_OUTPUT]:
                    if os.path.exists(dir_path):
                        for file in os.listdir(dir_path):
                            os.remove(os.path.join(dir_path, file))
                st.rerun()
        
        with col3:
            if st.button("🧪 Test Poppler", use_container_width=True):
                try:
                    import subprocess
                    result = subprocess.run(['pdftoppm', '-h'], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("✅ Poppler is working correctly")
                    else:
                        st.error("❌ Poppler test failed")
                except Exception as e:
                    st.error(f"❌ Poppler test failed: {str(e)}")
        
        # Directory Status
        st.markdown("### 📁 Directory Status")
        
        directories = [
            ("PDF Input", config.PDF_INPUT_DIR),
            ("TXT Output", config.PDF_OUTPUT_DIR),
            ("XLSX Output", config.XLSX_OUTPUT_DIR),
            ("Validation Output", config.DATE_VALIDATION_OUTPUT)
        ]
        
        for name, path in directories:
            exists = os.path.exists(path)
            file_count = len(os.listdir(path)) if exists else 0
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.text(f"{name}: {path}")
            with col2:
                status_icon = "✅" if exists else "❌"
                st.text(f"{status_icon} {file_count} files")
            with col3:
                if exists:
                    st.text("Ready")
                else:
                    st.text("Missing")
        
        # Deployment Information
        st.markdown("### 🚀 Deployment Information")
        
        st.markdown("""
        **Local Development:**
        ```bash
        streamlit run app_streamlit.py
        ```
        
        **Streamlit Cloud Deployment:**
        1. Push code to GitHub repository
        2. Connect repository to Streamlit Cloud
        3. Set environment variables (GEMINI_API_KEY)
        4. Deploy application
        
        **Environment Variables Required:**
        - `GEMINI_API_KEY`: Your Google Gemini API key
        """)

if __name__ == "__main__":
    main()