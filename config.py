"""
Configuration file for Workflow Procesare App
Contains all environment variables and path configurations
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Workflow Procesare application"""
    
    # ===========================================
    # DYNAMIC PATH CONFIGURATION
    # ===========================================
    
    # Get the directory where this config.py file is located
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Base directories - dynamic paths relative to config.py location
    BASE_PATH = os.getenv("BASE_PATH", os.path.join(CURRENT_DIR, "Data-IN-OUT"))
    PROJECT_PATH = os.getenv("PROJECT_PATH", CURRENT_DIR)
    
    # Step 1 - PDF to TXT
    PDF_INPUT_DIR = os.getenv("PDF_INPUT_DIR", os.path.join(BASE_PATH, "01. Gemini OCR PDF to TXT", "IN"))
    PDF_OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", os.path.join(BASE_PATH, "01. Gemini OCR PDF to TXT", "OUT"))
    
    # Step 2 - TXT to XLSX
    TXT_INPUT_DIR = os.getenv("TXT_INPUT_DIR", os.path.join(BASE_PATH, "01. Gemini OCR PDF to TXT", "OUT"))
    XLSX_OUTPUT_DIR = os.getenv("XLSX_OUTPUT_DIR", os.path.join(BASE_PATH, "02. Structurare TXT to XLSX"))
    
    # Step 3 - PDF Copy
    EXCEL_PATH = os.getenv("EXCEL_PATH", os.path.join(BASE_PATH, "02. Structurare TXT to XLSX", "2.structured_extract.xlsx"))
    PDF_COPY_BASE_DIR = os.getenv("PDF_COPY_BASE_DIR", os.path.join(BASE_PATH, "03. PDF_Copy doc suport"))
    
    # Step 4 - Date Validation
    DATE_VALIDATION_INPUT = os.getenv("DATE_VALIDATION_INPUT", os.path.join(BASE_PATH, "02. Structurare TXT to XLSX", "2.structured_extract.xlsx"))
    DATE_VALIDATION_OUTPUT = os.getenv("DATE_VALIDATION_OUTPUT", os.path.join(BASE_PATH, "04. Date si validare XLSX"))
    
    # Step 5 - Monthly Expansion
    MONTHLY_INPUT = os.getenv("MONTHLY_INPUT", os.path.join(BASE_PATH, "04. Date si validare XLSX", "4.transformed_data.xlsx"))
    MONTHLY_OUTPUT = os.getenv("MONTHLY_OUTPUT", os.path.join(BASE_PATH, "05. Monthly Split Logic"))
    
    # ===========================================
    # API CONFIGURATION
    # ===========================================
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # API Processing Settings
    API_BATCH_SIZE = int(os.getenv("API_BATCH_SIZE", "10"))
    API_DELAY_SECONDS = int(os.getenv("API_DELAY_SECONDS", "2"))
    API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", "3"))
    
    # ===========================================
    # PROCESSING CONFIGURATION
    # ===========================================
    
    # File Processing
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "8"))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "True").lower() == "true"
    
    # Date Processing
    DATE_FORMAT = os.getenv("DATE_FORMAT", "%d/%m/%Y")
    FALLBACK_TO_INVOICE_MONTH = os.getenv("FALLBACK_TO_INVOICE_MONTH", "True").lower() == "true"
    VAT_TOLERANCE = float(os.getenv("VAT_TOLERANCE", "0.001"))
    
    # ===========================================
    # OUTPUT CONFIGURATION
    # ===========================================
    
    # Excel Output
    EXCEL_ENGINE = os.getenv("EXCEL_ENGINE", "openpyxl")
    INCLUDE_HYPERLINKS = os.getenv("INCLUDE_HYPERLINKS", "True").lower() == "true"
    AUTO_COLUMN_WIDTH = os.getenv("AUTO_COLUMN_WIDTH", "True").lower() == "true"
    
    # File Naming
    OUTPUT_PREFIX = os.getenv("OUTPUT_PREFIX", "structured_extract")
    TRANSFORMED_PREFIX = os.getenv("TRANSFORMED_PREFIX", "transformed_data")
    EXPANDED_PREFIX = os.getenv("EXPANDED_PREFIX", "expanded_monthly_rows")
    
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
