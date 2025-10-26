"""
Configuration file for Workflow Procesare App
Contains all environment variables and path configurations
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Try to import Streamlit for secrets management (for Streamlit Cloud)
try:
    import streamlit as st
    _streamlit_available = True
except ImportError:
    _streamlit_available = False

def get_env_var(key, default=None):
    """
    Get environment variable from Streamlit secrets (if deployed) 
    or from .env file (if local)
    """
    if _streamlit_available:
        try:
            # Try to get from Streamlit secrets first
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass
    
    # Fall back to environment variable (from .env or system)
    return os.getenv(key, default)

class Config:
    """Configuration class for the Workflow Procesare application"""
    
    # ===========================================
    # DYNAMIC PATH CONFIGURATION
    # ===========================================
    
    # Get the directory where this config.py file is located
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Base directories - dynamic paths relative to config.py location
    BASE_PATH = get_env_var("BASE_PATH", os.path.join(CURRENT_DIR, "Data-IN-OUT"))
    PROJECT_PATH = get_env_var("PROJECT_PATH", CURRENT_DIR)
    
    # Step 1 - PDF to TXT
    PDF_INPUT_DIR = get_env_var("PDF_INPUT_DIR", os.path.join(BASE_PATH, "01. Gemini OCR PDF to TXT", "IN"))
    PDF_OUTPUT_DIR = get_env_var("PDF_OUTPUT_DIR", os.path.join(BASE_PATH, "01. Gemini OCR PDF to TXT", "OUT"))
    
    # Step 2 - TXT to XLSX
    TXT_INPUT_DIR = get_env_var("TXT_INPUT_DIR", os.path.join(BASE_PATH, "01. Gemini OCR PDF to TXT", "OUT"))
    XLSX_OUTPUT_DIR = get_env_var("XLSX_OUTPUT_DIR", os.path.join(BASE_PATH, "02. Structurare TXT to XLSX"))
    
    # Step 3 - PDF Copy
    EXCEL_PATH = get_env_var("EXCEL_PATH", os.path.join(BASE_PATH, "02. Structurare TXT to XLSX", "2.structured_extract.xlsx"))
    PDF_COPY_BASE_DIR = get_env_var("PDF_COPY_BASE_DIR", os.path.join(BASE_PATH, "03. PDF_Copy doc suport"))
    
    # Step 4 - Date Validation
    DATE_VALIDATION_INPUT = get_env_var("DATE_VALIDATION_INPUT", os.path.join(BASE_PATH, "02. Structurare TXT to XLSX", "2.structured_extract.xlsx"))
    DATE_VALIDATION_OUTPUT = get_env_var("DATE_VALIDATION_OUTPUT", os.path.join(BASE_PATH, "04. Date si validare XLSX"))
    
    # Step 5 - Monthly Expansion
    MONTHLY_INPUT = get_env_var("MONTHLY_INPUT", os.path.join(BASE_PATH, "04. Date si validare XLSX", "4.transformed_data.xlsx"))
    MONTHLY_OUTPUT = get_env_var("MONTHLY_OUTPUT", os.path.join(BASE_PATH, "05. Monthly Split Logic"))
    
    # ===========================================
    # API CONFIGURATION
    # ===========================================
    
    # Google Gemini API
    GEMINI_API_KEY = get_env_var("GEMINI_API_KEY", "your_gemini_api_key_here")
    GEMINI_MODEL = get_env_var("GEMINI_MODEL", "gemini-2.0-flash")
    
    # API Processing Settings
    API_BATCH_SIZE = int(get_env_var("API_BATCH_SIZE", "10"))
    API_DELAY_SECONDS = int(get_env_var("API_DELAY_SECONDS", "2"))
    API_MAX_RETRIES = int(get_env_var("API_MAX_RETRIES", "3"))
    
    # ===========================================
    # PROCESSING CONFIGURATION
    # ===========================================
    
    # File Processing
    MAX_WORKERS = int(get_env_var("MAX_WORKERS", "8"))
    DEBUG_MODE = get_env_var("DEBUG_MODE", "False").lower() == "true"
    ENABLE_CACHE = get_env_var("ENABLE_CACHE", "True").lower() == "true"
    
    # Date Processing
    DATE_FORMAT = get_env_var("DATE_FORMAT", "%d/%m/%Y")
    FALLBACK_TO_INVOICE_MONTH = get_env_var("FALLBACK_TO_INVOICE_MONTH", "True").lower() == "true"
    VAT_TOLERANCE = float(get_env_var("VAT_TOLERANCE", "0.001"))
    
    # ===========================================
    # OUTPUT CONFIGURATION
    # ===========================================
    
    # Excel Output
    EXCEL_ENGINE = get_env_var("EXCEL_ENGINE", "openpyxl")
    INCLUDE_HYPERLINKS = get_env_var("INCLUDE_HYPERLINKS", "True").lower() == "true"
    AUTO_COLUMN_WIDTH = get_env_var("AUTO_COLUMN_WIDTH", "True").lower() == "true"
    
    # File Naming
    OUTPUT_PREFIX = get_env_var("OUTPUT_PREFIX", "structured_extract")
    TRANSFORMED_PREFIX = get_env_var("TRANSFORMED_PREFIX", "transformed_data")
    EXPANDED_PREFIX = get_env_var("EXPANDED_PREFIX", "expanded_monthly_rows")
    
    # ===========================================
    # HELPER METHODS
    # ===========================================
    
    @classmethod
    def get_pdf_path(cls, pdf_name):
        """Get full path for a PDF file"""
        return os.path.join(cls.PDF_INPUT_DIR, pdf_name)
    
    @classmethod
    def get_txt_path(cls, txt_name):
        """Get full path for a TXT file"""
        return os.path.join(cls.PDF_OUTPUT_DIR, txt_name)
    
    @classmethod
    def get_excel_path(cls, step=2):
        """Get Excel file path for different steps"""
        if step == 2:
            return os.path.join(cls.XLSX_OUTPUT_DIR, f"{cls.OUTPUT_PREFIX}.xlsx")
        elif step == 4:
            return os.path.join(cls.DATE_VALIDATION_OUTPUT, f"4.{cls.TRANSFORMED_PREFIX}.xlsx")
        elif step == 5:
            return os.path.join(cls.MONTHLY_OUTPUT, f"5.{cls.EXPANDED_PREFIX}.xlsx")
        else:
            return cls.EXCEL_PATH
    
    @classmethod
    def create_directories(cls):
        """Create all necessary directories"""
        directories = [
            cls.PDF_INPUT_DIR,
            cls.PDF_OUTPUT_DIR,
            cls.XLSX_OUTPUT_DIR,
            cls.PDF_COPY_BASE_DIR,
            cls.DATE_VALIDATION_OUTPUT,
            cls.MONTHLY_OUTPUT
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def debug_paths(cls):
        """Debug method to print all calculated paths"""
        print("=" * 60)
        print("DYNAMIC PATH CONFIGURATION DEBUG")
        print("=" * 60)
        print(f"Current Directory: {cls.CURRENT_DIR}")
        print(f"Base Path: {cls.BASE_PATH}")
        print(f"Project Path: {cls.PROJECT_PATH}")
        print("-" * 40)
        print(f"PDF Input: {cls.PDF_INPUT_DIR}")
        print(f"PDF Output: {cls.PDF_OUTPUT_DIR}")
        print(f"XLSX Output: {cls.XLSX_OUTPUT_DIR}")
        print(f"PDF Copy Base: {cls.PDF_COPY_BASE_DIR}")
        print(f"Date Validation Output: {cls.DATE_VALIDATION_OUTPUT}")
        print(f"Monthly Output: {cls.MONTHLY_OUTPUT}")
        print("=" * 60)
    
    @classmethod
    def validate_config(cls):
        """Validate configuration and check if API key is set"""
        if cls.GEMINI_API_KEY == "your_gemini_api_key_here":
            raise EnvironmentError("❌ GEMINI_API_KEY not set. Please update your .env file.")
        
        # Create directories
        cls.create_directories()
        
        return True

# Create global config instance
config = Config()

# Validate configuration on import
try:
    config.validate_config()
except EnvironmentError as e:
    print(f"Configuration Error: {e}")
    print("Please create a .env file with your GEMINI_API_KEY")
