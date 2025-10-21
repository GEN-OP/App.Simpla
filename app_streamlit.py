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
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

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

def run_pdf_to_txt(pdf_files, progress_bar, status_placeholder):
    """Run PDF to TXT conversion (Step 1)"""
    try:
        # Import here to avoid issues if not needed
        from pdf2image import convert_from_path
        import google.generativeai as genai
        
        # Configure API
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        total_files = len(pdf_files)
        processed = 0
        
        for pdf_file in pdf_files:
            status_placeholder.info(f"🔄 Processing: {pdf_file}")
            
            # Convert PDF to images
            pdf_path = os.path.join(config.PDF_INPUT_DIR, pdf_file)
            images = convert_from_path(pdf_path)
            
            if not images:
                status_placeholder.warning(f"⚠️ No images extracted from {pdf_file}")
                continue
            
            # Process each page
            base_name = os.path.splitext(pdf_file)[0]
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
                        f.write(f"\n\n--- Page {idx + 1} ---\n[OCR Error: {str(e)}]")
            
            processed += 1
            progress_bar.progress(processed / total_files)
            status_placeholder.success(f"✅ Completed: {pdf_file}")
        
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
        
        # File counts
        counts = get_file_counts()
        for name, count in counts.items():
            st.metric(name, count)
        
        st.divider()
        
        # Quick actions
        st.header("⚡ Quick Actions")
        if st.button("🔄 Refresh Counts"):
            st.rerun()
        
        if st.button("🗑️ Clear All Data"):
            if st.session_state.get('confirm_clear', False):
                # Clear all directories
                for path in [config.PDF_INPUT_DIR, config.PDF_OUTPUT_DIR, 
                           config.XLSX_OUTPUT_DIR, config.DATE_VALIDATION_OUTPUT]:
                    if os.path.exists(path):
                        for file in os.listdir(path):
                            os.remove(os.path.join(path, file))
                st.success("All data cleared!")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm clearing all data")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📄 Run OCR", "📊 Results", "⚙️ Settings"])
    
    with tab1:
        st.header("Welcome to AI PDF Invoice Processor")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 What This Does
            - **Upload PDF invoices** and process them automatically
            - **Extract text** using Google Gemini AI OCR
            - **Structure data** into organized Excel spreadsheets
            - **Validate dates** and extract service periods
            - **Generate reports** for accounting and analysis
            
            ### 🚀 Quick Start
            1. Go to **"Run OCR"** tab
            2. Upload your PDF invoices
            3. Click **"Process All"** to run the full workflow
            4. View results in **"Results"** tab
            """)
        
        with col2:
            # Status overview
            st.markdown("### 📈 Current Status")
            
            col2a, col2b = st.columns(2)
            with col2a:
                st.metric("PDF Files", counts['PDF Input'])
                st.metric("Text Files", counts['OCR Text'])
            with col2b:
                st.metric("Excel Files", counts['Structured Excel'])
                st.metric("Validated Files", counts['Date Validated'])
            
            # Environment status
            st.markdown("### ✅ Environment")
            st.success("API Key: Configured")
            st.success("Directories: Ready")
    
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
                    # Run the full workflow
                    progress_bar = st.progress(0)
                    status_placeholder = st.empty()
                    
                    # Step 1: PDF to TXT
                    status_placeholder.info("🔄 Step 1: Converting PDFs to text...")
                    pdf_files = [f.name for f in uploaded_files]
                    success1, message1 = run_pdf_to_txt(pdf_files, progress_bar, status_placeholder)
                    
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
                                status_placeholder.success("🎉 All processing completed successfully!")
                                st.balloons()
                            else:
                                status_placeholder.error(f"❌ Step 3 failed: {message3}")
                        else:
                            status_placeholder.error(f"❌ Step 2 failed: {message2}")
                    else:
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
        st.header("⚙️ Settings & Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔧 Current Configuration")
            st.json({
                "API Model": config.GEMINI_MODEL,
                "Batch Size": config.API_BATCH_SIZE,
                "API Delay": f"{config.API_DELAY_SECONDS}s",
                "Max Retries": config.API_MAX_RETRIES,
                "Debug Mode": config.DEBUG_MODE
            })
        
        with col2:
            st.subheader("📁 Directory Paths")
            st.json({
                "PDF Input": config.PDF_INPUT_DIR,
                "PDF Output": config.PDF_OUTPUT_DIR,
                "Excel Output": config.XLSX_OUTPUT_DIR,
                "Date Validation": config.DATE_VALIDATION_OUTPUT
            })
        
        st.subheader("🚀 Deployment Instructions")
        st.markdown("""
        ### Local Development
        ```bash
        streamlit run app_streamlit.py
        ```
        
        ### Streamlit Cloud Deployment
        1. Push your code to GitHub
        2. Connect your GitHub repo to Streamlit Cloud
        3. Set environment variables in Streamlit Cloud:
           - `GEMINI_API_KEY`: Your Google Gemini API key
        4. Deploy!
        
        ### Requirements
        - Python 3.8+
        - All dependencies in `requirements.txt`
        - Valid Gemini API key in `.env` file
        """)

if __name__ == "__main__":
    main()
