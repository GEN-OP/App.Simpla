"""
Test script to verify configuration is working correctly
"""

from config import config

def test_configuration():
    """Test if configuration is loaded correctly"""
    print("🔧 Testing Configuration...")
    print("=" * 50)
    
    # Test API Key
    api_key_configured = bool(config.GEMINI_API_KEY and config.GEMINI_API_KEY != "your_gemini_api_key_here")
    print(f"✅ API Key configured: {api_key_configured}")
    
    # Test Paths
    paths = {
        "PDF Input": config.PDF_INPUT_DIR,
        "PDF Output": config.PDF_OUTPUT_DIR,
        "TXT Input": config.TXT_INPUT_DIR,
        "XLSX Output": config.XLSX_OUTPUT_DIR,
        "Excel Path": config.EXCEL_PATH,
        "PDF Copy Base": config.PDF_COPY_BASE_DIR,
        "Date Validation Input": config.DATE_VALIDATION_INPUT,
        "Date Validation Output": config.DATE_VALIDATION_OUTPUT,
        "Monthly Input": config.MONTHLY_INPUT,
        "Monthly Output": config.MONTHLY_OUTPUT
    }
    
    print("\n📁 Path Configuration:")
    for name, path in paths.items():
        print(f"  {name}: {path}")
    
    # Test API Settings
    print(f"\n⚙️ API Settings:")
    print(f"  Model: {config.GEMINI_MODEL}")
    print(f"  Batch Size: {config.API_BATCH_SIZE}")
    print(f"  Delay: {config.API_DELAY_SECONDS}s")
    print(f"  Max Retries: {config.API_MAX_RETRIES}")
    
    # Test Processing Settings
    print(f"\n🔧 Processing Settings:")
    print(f"  Max Workers: {config.MAX_WORKERS}")
    print(f"  Debug Mode: {config.DEBUG_MODE}")
    print(f"  Enable Cache: {config.ENABLE_CACHE}")
    
    print("\n" + "=" * 50)
    if api_key_configured:
        print("✅ Configuration test PASSED!")
        print("🚀 Ready to run the workflow scripts!")
    else:
        print("❌ Configuration test FAILED!")
        print("🔑 Please set your GEMINI_API_KEY in the .env file")
    
    return api_key_configured

if __name__ == "__main__":
    test_configuration()
