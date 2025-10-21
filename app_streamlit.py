"""
AI-Powered PDF Invoice Processor - Streamlit Dashboard
=====================================================

A clean, professional dashboard for processing PDF invoices using AI.
Integrates existing workflow scripts: 1.PDF_to_Txt.py → 2.Txt_to_XLSX.py → 4.XLSX_validation_dates.py

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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #28a745;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
        background-color: #f8d7da;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #dc3545;
    }
    .status-warning {
        color: #856404;
        font-weight: bold;
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #ffc107;
    }
    .status-info {
        color: #0c5460;
        font-weight: bold;
        background-color: #d1ecf1;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #17a2b8;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .workflow-step {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .step-number {
        background: #007bff;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
    }
    .error-log {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        max-height: 300px;
        overflow-y: auto;
    }
    .success-badge {
        background: #28a745;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .error-badge {
        background: #dc3545;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .warning-badge {
        background: #ffc107;
        color: #212529;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
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
            return False, "GEMINI_API_KEY not configured in .env file"
        
        # Check if directories exist
        if not os.path.exists(config.PDF_INPUT_DIR):
            os.makedirs(config.PDF_INPUT_DIR, exist_ok=True)
        if not os.path.exists(config.PDF_OUTPUT_DIR):
            os.makedirs(config.PDF_OUTPUT_DIR, exist_ok=True)
        if not os.path.exists(config.XLSX_OUTPUT_DIR):
            os.makedirs(config.XLSX_OUTPUT_DIR, exist_ok=True)
        if not os.path.exists(config.DATE_VALIDATION_OUTPUT):
            os.makedirs(config.DATE_VALIDATION_OUTPUT, exist_ok=True)
        
        return True, "Environment configured correctly"
    except Exception as e:
        return False, f"Configuration error: {str(e)}"

def run_pdf_to_txt(uploaded_files, progress_bar, status_placeholder):
    """Run PDF to TXT conversion (Step 1) - handles uploaded files for cloud deployment"""
    try:
        # Import here to avoid issues if not needed
        from pdf2image import convert_from_path
        import google.generativeai as genai
        from pathlib import Path
        import tempfile
        
        # Configure API
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # Create temporary directory for uploaded files
        temp_dir = Path(tempfile.gettempdir()) / "streamlit_pdf_uploads"
        temp_dir.mkdir(exist_ok=True)
        
        total_files = len(uploaded_files)
        processed = 0
        
        for uploaded_file in uploaded_files:
            log_status(f"Processing: {uploaded_file.name}", "INFO")
            status_placeholder.info(f"🔄 Processing: {uploaded_file.name}")
            
            # Save uploaded file to temporary directory
            temp_pdf_path = temp_dir / uploaded_file.name
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Convert PDF to images using temporary file
                images = convert_from_path(str(temp_pdf_path))
                
                if not images:
                    log_error(f"No images extracted from {uploaded_file.name}", "WARNING")
                    status_placeholder.warning(f"⚠️ No images extracted from {uploaded_file.name}")
                    continue
                
                # Process each page
                base_name = os.path.splitext(uploaded_file.name)[0]
                output_file = os.path.join(config.PDF_OUTPUT_DIR, f"{base_name}_ocr.txt")
                
                with open(output_file, "w", encoding="utf-8") as f:
                    for idx, img in enumerate(images):
                        try:
                            model = genai.GenerativeModel(config.GEMINI_MODEL)
                            prompt = f"""
                            Extract ALL text visible in this invoice image (page {idx + 1}).
                            Include every line of text exactly as it appears.
                            Capture all product descriptions, quantities, prices and especially dates and date intervals.
                            Preserve the table structure as much as possible.
                            """
                            response = model.generate_content([prompt, img])
                            f.write(f"\n\n--- Page {idx + 1} ---\n{response.text}")
                        except Exception as e:
                            log_error(f"OCR failed on page {idx + 1} of {uploaded_file.name}: {str(e)}", "ERROR")
                            f.write(f"\n\n--- Page {idx + 1} ---\n[OCR Error: {str(e)}]")
                
                processed += 1
                progress_bar.progress(processed / total_files)
                log_status(f"Completed: {uploaded_file.name}", "SUCCESS")
                status_placeholder.success(f"✅ Completed: {uploaded_file.name}")
                
            except Exception as e:
                log_error(f"Failed to process {uploaded_file.name}: {str(e)}", "ERROR")
                status_placeholder.error(f"❌ Failed to process {uploaded_file.name}: {str(e)}")
            finally:
                # Clean up temporary file
                try:
                    os.remove(temp_pdf_path)
                except Exception as cleanup_error:
                    log_error(f"Could not delete temporary file: {cleanup_error}", "WARNING")
                    status_placeholder.warning(f"⚠️ Could not delete temporary file: {cleanup_error}")
        
        # Clean up temporary directory if empty
        try:
            if temp_dir.exists() and not any(temp_dir.iterdir()):
                temp_dir.rmdir()
        except Exception:
            pass  # Ignore cleanup errors for temp directory
        
        return True, f"Successfully processed {processed}/{total_files} PDF files"
        
    except Exception as e:
        return False, f"PDF to TXT conversion failed: {str(e)}"

def run_txt_to_xlsx(progress_bar, status_placeholder):
    """Run TXT to XLSX conversion (Step 2)"""
    try:
        # Import here to avoid issues if not needed
        import google.generativeai as genai
        import json
        import re
        
        # Configure API
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        status_placeholder.info("🔄 Converting text files to structured Excel...")
        
        # Get all text files
        txt_files = [f for f in os.listdir(config.PDF_OUTPUT_DIR) if f.endswith('_ocr.txt')]
        
        if not txt_files:
            return False, "No OCR text files found"
        
        # Process each text file
        all_invoices = []
        processed = 0
        
        for txt_file in txt_files:
            txt_path = os.path.join(config.PDF_OUTPUT_DIR, txt_file)
            
            with open(txt_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Extract invoice details using Gemini
            model = genai.GenerativeModel(config.GEMINI_MODEL)
            prompt = f"""
            Extract the following invoice details from the text below. Return ONLY a valid JSON object.
            For each field, include a confidence score from 1-10 where 10 means you're absolutely certain and 1 means you're very uncertain.
            
            {{
                "invoice_number": "XXX123",
                "invoice_number_confidence": 9,
                "invoice_date": "DD/MM/YYYY",
                "invoice_date_confidence": 8,
                "vendor_name": "Company Name",
                "vendor_name_confidence": 10,
                "items_details": [
                    "Exact full item description as written on the invoice",
                    "Ensure multi-word descriptions are fully captured"
                ],
                "items_details_confidence": 7,
                "total_amount": "1234.56",
                "total_amount_confidence": 9,
                "total_without_vat": "1100.00",
                "total_without_vat_confidence": 8,
                "vat_amount": "134.56",
                "vat_amount_confidence": 9,
                "currency": "LEI",
                "currency_confidence": 10,
                "payment_due_date": "DD/MM/YYYY",
                "payment_due_date_confidence": 7,
                "vendor_address": "Full vendor address",
                "vendor_address_confidence": 6,
                "customer_name": "Customer name if visible",
                "customer_name_confidence": 5,
                "customer_address": "Customer address if visible",
                "customer_address_confidence": 4,
                "notes": "Any additional notes or observations",
                "notes_confidence": 3
            }}
            
            Text to analyze:
            {text_content}
            """
            
            try:
                response = model.generate_content(prompt)
                invoice_data = json.loads(response.text)
                invoice_data['source_file'] = txt_file
                all_invoices.append(invoice_data)
            except Exception as e:
                # Create a basic entry if parsing fails
                all_invoices.append({
                    'source_file': txt_file,
                    'invoice_number': 'ERROR',
                    'invoice_date': '',
                    'vendor_name': 'ERROR',
                    'total_amount': '0',
                    'error': str(e)
                })
            
            processed += 1
            progress_bar.progress(processed / len(txt_files))
        
        # Convert to DataFrame and save
        df = pd.DataFrame(all_invoices)
        output_path = os.path.join(config.XLSX_OUTPUT_DIR, "2.structured_extract.xlsx")
        df.to_excel(output_path, index=False)
        
        return True, f"Successfully processed {processed} text files to Excel"
        
    except Exception as e:
        return False, f"TXT to XLSX conversion failed: {str(e)}"

def run_date_validation(progress_bar, status_placeholder):
    """Run date validation and extraction (Step 4)"""
    try:
        # Import here to avoid issues if not needed
        import google.generativeai as genai
        from dateutil.relativedelta import relativedelta
        
        # Configure API
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        status_placeholder.info("🔄 Extracting service dates and validating data...")
        
        # Read the Excel file
        input_excel = os.path.join(config.XLSX_OUTPUT_DIR, "2.structured_extract.xlsx")
        if not os.path.exists(input_excel):
            return False, "Structured Excel file not found. Run Step 2 first."
        
        df = pd.read_excel(input_excel)
        
        if df.empty:
            return False, "No data found in Excel file"
        
        # Process each row
        processed = 0
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            # Simple date extraction logic (simplified version)
            if pd.notna(row.get('items_details')):
                # Extract dates from items details
                items = str(row['items_details'])
                # Look for date patterns
                date_patterns = [
                    r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
                    r'(\d{1,2}\s+\w+\s+\d{2,4})',
                ]
                
                dates_found = []
                for pattern in date_patterns:
                    matches = re.findall(pattern, items)
                    dates_found.extend(matches)
                
                # Add extracted dates to the row
                df.at[idx, 'extracted_dates'] = ', '.join(dates_found) if dates_found else 'No dates found'
            else:
                df.at[idx, 'extracted_dates'] = 'No items details'
            
            processed += 1
            progress_bar.progress(processed / total_rows)
        
        # Save the processed data
        output_path = os.path.join(config.DATE_VALIDATION_OUTPUT, "4.transformed_data.xlsx")
        df.to_excel(output_path, index=False)
        
        return True, f"Successfully processed {processed} rows with date extraction"
        
    except Exception as e:
        return False, f"Date validation failed: {str(e)}"

def get_file_counts():
    """Get counts of files in each directory"""
    counts = {}
    directories = {
        'PDF Input': config.PDF_INPUT_DIR,
        'OCR Text': config.PDF_OUTPUT_DIR,
        'Structured Excel': config.XLSX_OUTPUT_DIR,
        'Date Validated': config.DATE_VALIDATION_OUTPUT
    }
    
    for name, path in directories.items():
        if os.path.exists(path):
            if name == 'PDF Input':
                counts[name] = len([f for f in os.listdir(path) if f.endswith('.pdf')])
            elif name == 'OCR Text':
                counts[name] = len([f for f in os.listdir(path) if f.endswith('_ocr.txt')])
            elif name == 'Structured Excel':
                counts[name] = len([f for f in os.listdir(path) if f.endswith('.xlsx')])
            elif name == 'Date Validated':
                counts[name] = len([f for f in os.listdir(path) if f.endswith('.xlsx')])
        else:
            counts[name] = 0
    
    return counts

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI PDF Invoice Processor</h1>', unsafe_allow_html=True)
    
    # Check environment
    env_ok, env_message = check_environment()
    if not env_ok:
        st.error(f"❌ {env_message}")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Dashboard")
        
        # System status
        status = get_system_status()
        st.markdown("### 🔧 System Status")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Environment:** {status['environment']}")
            st.markdown(f"**API Key:** {status['api_key']}")
        with col2:
            st.markdown(f"**Directories:** {status['directories']}")
            st.markdown(f"**Poppler:** {status['poppler']}")
        
        if status['last_error']:
            st.markdown(f"**Last Error:** {status['last_error']}")
        
        if status['processing_time']:
            st.markdown(f"**Last Processing:** {status['processing_time']}")
        
        st.divider()
        
        # File counts with better styling
        st.markdown("### 📁 File Counts")
        counts = get_file_counts()
        for name, count in counts.items():
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{count}</div>
                <div class="metric-label">{name}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Quick actions
        st.header("⚡ Quick Actions")
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()
        
        if st.button("🗑️ Clear All Data", use_container_width=True):
            if st.session_state.get('confirm_clear', False):
                # Clear all directories
                for path in [config.PDF_INPUT_DIR, config.PDF_OUTPUT_DIR, 
                           config.XLSX_OUTPUT_DIR, config.DATE_VALIDATION_OUTPUT]:
                    if os.path.exists(path):
                        for file in os.listdir(path):
                            os.remove(os.path.join(path, file))
                log_status("All data cleared", "SUCCESS")
                st.success("All data cleared!")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm clearing all data")
        
        if st.button("📋 Clear Error Log", use_container_width=True):
            st.session_state.error_log = []
            st.success("Error log cleared!")
            st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📄 Run OCR", "📊 Results", "⚙️ Settings"])
    
    with tab1:
        st.header("Welcome to AI PDF Invoice Processor")
        
        # Workflow visualization
        st.markdown("### 🔄 Processing Workflow")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="workflow-step">
                <span class="step-number">1</span>
                <strong>Upload PDFs</strong><br>
                Drag & drop invoice files
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="workflow-step">
                <span class="step-number">2</span>
                <strong>OCR Processing</strong><br>
                Extract text with AI
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="workflow-step">
                <span class="step-number">3</span>
                <strong>Data Structure</strong><br>
                Convert to Excel format
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="workflow-step">
                <span class="step-number">4</span>
                <strong>Date Validation</strong><br>
                Extract service periods
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Key Features
            - **🤖 AI-Powered OCR** - High accuracy text extraction
            - **📊 Smart Data Structure** - Organized Excel output
            - **📅 Date Intelligence** - Service period extraction
            - **☁️ Cloud Ready** - Works locally and on Streamlit Cloud
            - **🔄 Real-time Processing** - Live progress tracking
            - **📋 Error Logging** - Comprehensive status monitoring
            """)
        
        with col2:
            # Current processing status
            st.markdown("### 📈 Current Status")
            
            # Last processing status
            status_badge = "success-badge" if "Completed" in st.session_state.last_processing_status else "warning-badge"
            st.markdown(f"""
            <div class="{status_badge}">
                {st.session_state.last_processing_status}
            </div>
            """, unsafe_allow_html=True)
            
            # Quick stats
            col2a, col2b = st.columns(2)
            with col2a:
                st.metric("📄 PDF Files", counts['PDF Input'])
                st.metric("📝 Text Files", counts['OCR Text'])
            with col2b:
                st.metric("📊 Excel Files", counts['Structured Excel'])
                st.metric("✅ Validated", counts['Date Validated'])
            
            # System health
            st.markdown("### 🔧 System Health")
            if status['environment'] == "✅ OK" and status['api_key'] == "✅ Configured":
                st.success("🟢 All systems operational")
            else:
                st.error("🔴 System issues detected - check Settings tab")
    
    with tab2:
        st.header("📄 Process PDF Invoices")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Choose PDF files to process",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more PDF invoice files"
        )
        
        if uploaded_files:
            st.success(f"📁 {len(uploaded_files)} file(s) selected")
            
            # Show file details
            with st.expander("📋 File Details"):
                for file in uploaded_files:
                    st.write(f"• {file.name} ({file.size:,} bytes)")
            
            # Process button
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("💾 Save Files", type="primary"):
                    # Save uploaded files to input directory
                    saved_count = 0
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(config.PDF_INPUT_DIR, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        saved_count += 1
                    st.success(f"✅ Saved {saved_count} files to input directory")
                    st.rerun()
            
            with col2:
                if st.button("🔄 Process All", type="secondary"):
                    # Start timing
                    st.session_state.processing_start_time = datetime.now()
                    log_status("Starting full workflow processing", "INFO")
                    
                    # Run the full workflow
                    progress_bar = st.progress(0)
                    status_placeholder = st.empty()
                    
                    # Step 1: PDF to TXT
                    status_placeholder.info("🔄 Step 1: Converting PDFs to text...")
                    success1, message1 = run_pdf_to_txt(uploaded_files, progress_bar, status_placeholder)
                    
                    if success1:
                        # Step 2: TXT to XLSX
                        status_placeholder.info("🔄 Step 2: Converting text to structured Excel...")
                        progress_bar.progress(0.5)
                        success2, message2 = run_txt_to_xlsx(progress_bar, status_placeholder)
                        
                        if success2:
                            # Step 3: Date validation
                            status_placeholder.info("🔄 Step 3: Extracting and validating dates...")
                            progress_bar.progress(0.8)
                            success3, message3 = run_date_validation(progress_bar, status_placeholder)
                            
                            if success3:
                                progress_bar.progress(1.0)
                                st.session_state.processing_end_time = datetime.now()
                                log_status("All processing completed successfully", "SUCCESS")
                                status_placeholder.success("🎉 All processing completed successfully!")
                                st.balloons()
                            else:
                                st.session_state.processing_end_time = datetime.now()
                                log_error(f"Step 3 failed: {message3}", "ERROR")
                                status_placeholder.error(f"❌ Step 3 failed: {message3}")
                        else:
                            st.session_state.processing_end_time = datetime.now()
                            log_error(f"Step 2 failed: {message2}", "ERROR")
                            status_placeholder.error(f"❌ Step 2 failed: {message2}")
                    else:
                        st.session_state.processing_end_time = datetime.now()
                        log_error(f"Step 1 failed: {message1}", "ERROR")
                        status_placeholder.error(f"❌ Step 1 failed: {message1}")
    
    with tab3:
        st.header("📊 Results & Data")
        
        # Show available Excel files
        excel_files = []
        for directory in [config.XLSX_OUTPUT_DIR, config.DATE_VALIDATION_OUTPUT]:
            if os.path.exists(directory):
                excel_files.extend([os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.xlsx')])
        
        if excel_files:
            st.subheader("📈 Available Reports")
            
            for excel_file in excel_files:
                filename = os.path.basename(excel_file)
                st.write(f"**{filename}**")
                
                try:
                    df = pd.read_excel(excel_file)
                    st.dataframe(df, use_container_width=True)
                    
                    # Download button
                    with open(excel_file, 'rb') as f:
                        st.download_button(
                            label=f"📥 Download {filename}",
                            data=f.read(),
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    st.divider()
                except Exception as e:
                    st.error(f"Error reading {filename}: {str(e)}")
        else:
            st.info("No Excel files found. Process some PDFs first!")
    
    with tab4:
        st.header("⚙️ Settings & System Monitor")
        
        # System Status Overview
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
                <div class="metric-value">{status['poppler']}</div>
                <div class="metric-label">Poppler</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{status['directories']}</div>
                <div class="metric-label">Directories</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Error Log and Status
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Error Log & Status")
            
            if st.session_state.error_log:
                # Filter options
                filter_type = st.selectbox("Filter by type:", ["All", "ERROR", "WARNING", "INFO", "SUCCESS"])
                
                # Display filtered logs
                filtered_logs = st.session_state.error_log
                if filter_type != "All":
                    filtered_logs = [log for log in st.session_state.error_log if log["type"] == filter_type]
                
                # Show logs in a scrollable container
                log_content = ""
                for log in reversed(filtered_logs[-20:]):  # Show last 20 entries
                    badge_class = f"{log['type'].lower()}-badge" if log['type'] in ["ERROR", "WARNING", "SUCCESS"] else "info-badge"
                    log_content += f"""
                    <div style="margin: 0.5rem 0; padding: 0.5rem; border-left: 3px solid {'#dc3545' if log['type'] == 'ERROR' else '#ffc107' if log['type'] == 'WARNING' else '#28a745' if log['type'] == 'SUCCESS' else '#17a2b8'}; background: #f8f9fa;">
                        <span class="{badge_class}">{log['type']}</span>
                        <span style="color: #6c757d; font-size: 0.8rem;">{log['timestamp']}</span><br>
                        <span style="font-family: monospace;">{log['message']}</span>
                    </div>
                    """
                
                st.markdown(f"""
                <div class="error-log">
                    {log_content if log_content else "No logs to display"}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No error logs yet. Start processing some PDFs to see activity here.")
        
        with col2:
            st.subheader("🔧 Configuration")
            
            # Current settings
            st.markdown("**API Settings:**")
            st.code(f"""
Model: {config.GEMINI_MODEL}
Batch Size: {config.API_BATCH_SIZE}
Delay: {config.API_DELAY_SECONDS}s
Max Retries: {config.API_MAX_RETRIES}
Debug: {config.DEBUG_MODE}
            """)
            
            st.markdown("**Processing Settings:**")
            st.code(f"""
Max Workers: {config.MAX_WORKERS}
Date Format: {config.DATE_FORMAT}
VAT Tolerance: {config.VAT_TOLERANCE}
            """)
            
            # Quick actions
            st.markdown("**Quick Actions:**")
            if st.button("🔄 Refresh Status", use_container_width=True):
                st.rerun()
            
            if st.button("📋 Clear Logs", use_container_width=True):
                st.session_state.error_log = []
                st.success("Logs cleared!")
                st.rerun()
            
            if st.button("🔍 Test Poppler", use_container_width=True):
                try:
                    import subprocess
                    result = subprocess.run(['pdftoppm', '-v'], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("✅ Poppler working!")
                    else:
                        st.error("❌ Poppler not working")
                except:
                    st.error("❌ Poppler not found")
        
        st.divider()
        
        # Directory Status
        st.subheader("📁 Directory Status")
        
        directories = {
            "PDF Input": config.PDF_INPUT_DIR,
            "PDF Output": config.PDF_OUTPUT_DIR,
            "Excel Output": config.XLSX_OUTPUT_DIR,
            "Date Validation": config.DATE_VALIDATION_OUTPUT
        }
        
        for name, path in directories.items():
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
                    st.success("OK")
                else:
                    st.error("Missing")
        
        st.divider()
        
        # Deployment Info
        st.subheader("🚀 Deployment Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Local Development:**
            ```bash
            streamlit run app_streamlit.py
            ```
            
            **Requirements:**
            - Python 3.8+
            - All dependencies installed
            - Valid Gemini API key
            - Poppler installed
            """)
        
        with col2:
            st.markdown("""
            **Streamlit Cloud:**
            1. Push code to GitHub
            2. Connect to Streamlit Cloud
            3. Set `GEMINI_API_KEY` environment variable
            4. Deploy!
            
            **Cloud Features:**
            - ✅ Handles uploaded files in memory
            - ✅ Temporary file management
            - ✅ Automatic cleanup
            """)

if __name__ == "__main__":
    main()
