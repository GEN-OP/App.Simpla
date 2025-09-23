#Step 2 - Text to excel conversion using Gemini API
import os
import json
import re
import time
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("❌ GEMINI_API_KEY not set in .env file.")

genai.configure(api_key=API_KEY)

def extract_invoice_details(text, filename):
    """
    Extract invoice details using Gemini API
    
    Args:
        text (str): The invoice text content
        filename (str): Name of the original file
        
    Returns:
        dict: Structured invoice data with confidence scores
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
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
        "currency": "PHP",
        "currency_confidence": 10,
        "vat_amount": "134.56",
        "vat_amount_confidence": 9
    }}

    Important rules:
    1. Maintain the EXACT format shown above
    2. If a field is not found, use null for the value and 0 for its confidence score
    3. For invoice_date, keep the original format found in the document
    4. For currency, use the 3-letter code (USD, EUR, PHP, etc.)
    5. For items_details, search in document, if there are multiple items, return them as a list of strings. 
    6. For items_details, search in document and extract especially any dates, intervals, or periods mentioned in the item descriptions, such as rental periods, service months, if exists.
    7. For items_details, 
    TEXT:
    {text}
    """
    
    try:
        response = model.generate_content(prompt)
        # Try to parse the response as JSON
        try:
            # Find JSON in the response text (looking for content between curly braces)
            json_text = response.text
            if "{" in json_text and "}" in json_text:
                start = json_text.find("{")
                end = json_text.rfind("}") + 1
                json_text = json_text[start:end]
            
            # Parse the JSON
            invoice_details = json.loads(json_text)
            invoice_details['pdf_name'] = filename.replace('.txt', '')
            return invoice_details
        except json.JSONDecodeError:
            print(f"❌ Could not parse JSON from response for {filename}")
            print(f"Response text: {response.text[:500]}...")
            return {'pdf_name': filename.replace('.txt', ''), 'error': 'JSON parsing error'}
    except Exception as e:
        print(f"❌ API call failed for {filename}: {e}")
        return {'pdf_name': filename.replace('.txt', ''), 'error': str(e)}

def validate_invoice(invoice_data):
    """
    Validate extracted invoice data and flag potential issues
    
    Args:
        invoice_data (dict): The extracted invoice data
        
    Returns:
        list: List of validation issues
    """
    issues = []
    
    # Check invoice number format (usually alphanumeric)
    if not invoice_data.get('invoice_number'):
        issues.append("Missing invoice number")
    
    # Validate date format
    date_val = invoice_data.get('invoice_date')
    if date_val and not any(re.match(pattern, str(date_val)) for pattern in [
        r'\d{1,2}/\d{1,2}/\d{2,4}',  # DD/MM/YYYY
        r'\d{1,2}-\d{1,2}-\d{2,4}',  # DD-MM-YYYY
        r'\d{4}-\d{1,2}-\d{1,2}'     # YYYY-MM-DD
    ]):
        issues.append(f"Unusual date format: {date_val}")
    
    # Validate total amount is numeric
    try:
        float(str(invoice_data.get('total_amount', '0')).replace(',', ''))
    except ValueError:
        issues.append(f"Non-numeric total amount: {invoice_data.get('total_amount')}")
    
    # Verify totals match
    try:
        total = float(str(invoice_data.get('total_amount', '0')).replace(',', ''))
        subtotal = float(str(invoice_data.get('total_without_vat', '0')).replace(',', ''))
        vat = float(str(invoice_data.get('vat_amount', '0')).replace(',', ''))
        
        if abs((subtotal + vat) - total) > 1:  # Allow for rounding differences up to 1 unit
            issues.append(f"Total mismatch: {total} ≠ {subtotal} + {vat}")
    except (ValueError, TypeError):
        issues.append("Could not verify totals calculation")
    
    return issues

def clean_invoice_data(invoice_data):
    """
    Clean and standardize extracted data
    
    Args:
        invoice_data (dict): The extracted invoice data
        
    Returns:
        dict: Cleaned invoice data
    """
    # Create a copy to avoid modifying the original
    cleaned = invoice_data.copy()
    
    # Standardize currency format
    if cleaned.get('currency'):
        cleaned['currency'] = str(cleaned['currency']).upper()
        
    # Convert numeric values
    for field in ['total_amount', 'total_without_vat', 'vat_amount']:
        if cleaned.get(field):
            # Remove any currency symbols and commas
            clean_value = re.sub(r'[^\d.]', '', str(cleaned[field]))
            try:
                cleaned[field] = float(clean_value)
            except ValueError:
                pass
    
    return cleaned

def calculate_quality_score(invoice_data):
    """
    Calculate an overall quality score based on confidence scores
    
    Args:
        invoice_data (dict): The extracted invoice data
        
    Returns:
        float: Quality score between 0 and 100
    """
    # Fields to consider for quality score
    confidence_fields = [
        'invoice_number_confidence', 
        'invoice_date_confidence',
        'vendor_name_confidence', 
        'items_details_confidence',
        'total_amount_confidence', 
        'total_without_vat_confidence',
        'currency_confidence', 
        'vat_amount_confidence'
    ]
    
    # Get confidence scores for available fields
    scores = []
    for field in confidence_fields:
        if field in invoice_data and invoice_data[field] is not None:
            scores.append(float(invoice_data[field]))
    
    # If no scores available, return 0
    if not scores:
        return 0
    
    # Calculate average and scale to 0-100
    avg_score = sum(scores) / len(scores)
    return (avg_score / 10) * 100

def process_txt_to_excel(input_dir, output_dir, batch_size=5, delay_seconds=1):
    """
    Process all text files in directory to structured Excel
    
    Args:
        input_dir (str): Directory containing text files
        output_dir (str): Directory to save output Excel file
        batch_size (int): Number of files to process in each batch
        delay_seconds (int): Delay between batches to avoid API rate limits
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of text files
    txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    print(f"Found {len(txt_files)} text files to process")
    
    # Process files
    all_data = []
    for i in range(0, len(txt_files), batch_size):
        batch = txt_files[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(txt_files) + batch_size - 1)//batch_size}")
        
        for txt_file in batch:
            print(f"  Processing {txt_file}...")
            file_path = os.path.join(input_dir, txt_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Extract invoice details
                invoice_details = extract_invoice_details(text, txt_file)
                
                # Clean data
                cleaned_data = clean_invoice_data(invoice_details)
                
                # Validate data
                validation_issues = validate_invoice(cleaned_data)
                cleaned_data['validation_issues'] = '; '.join(validation_issues) if validation_issues else "No issues"
                
                # Calculate quality score
                cleaned_data['quality_score'] = calculate_quality_score(cleaned_data)
                
                all_data.append(cleaned_data)
                
            except Exception as e:
                print(f"❌ Error processing {txt_file}: {e}")
                all_data.append({
                    'pdf_name': txt_file.replace('.txt', ''), 
                    'error': str(e),
                    'validation_issues': 'Processing error',
                    'quality_score': 0
                })
        
        # Delay between batches to avoid API rate limits
        if i + batch_size < len(txt_files):
            print(f"Waiting {delay_seconds} seconds before next batch...")
            time.sleep(delay_seconds)
    
    # Create DataFrame and save to Excel
    output_file = os.path.join(output_dir, "2.structured_extract.xlsx")
    
    # Organize columns in a logical order
    columns = [
        'pdf_name', 'invoice_number', 'invoice_date', 'vendor_name',
        'currency', 'total_amount', 'total_without_vat', 'vat_amount',
        'items_details', 'quality_score', 'validation_issues'
    ]
    
    # Add confidence score columns
    confidence_columns = [col for col in all_data[0].keys() if col.endswith('_confidence')]
    columns.extend([col for col in confidence_columns if col not in columns])
    
    # Add any remaining columns
    all_columns = set()
    for item in all_data:
        all_columns.update(item.keys())
    
    columns.extend([col for col in all_columns if col not in columns])
    
    # Create DataFrame with organized columns
    df = pd.DataFrame(all_data)


    # Reorder columns (only include columns that exist in the DataFrame)
    existing_columns = [col for col in columns if col in df.columns]
    df = df[existing_columns]
    # Add full path hyperlink to original PDF
    pdf_base_path = r"C:\Users\george.nadrag\00. Coduri structurate\01. Gemini OCR PDF to TXT\IN"
    df['path'] = df['pdf_name'].apply(
        lambda name: f'=HYPERLINK("{os.path.join(pdf_base_path, name.replace("_ocr", "") + ".pdf")}", "{name.replace("_ocr", "")}.pdf")'
    )

    # Insert 'path' and 'considered' as first two columns
    df.insert(0, 'path', df.pop('path'))
    df.insert(1, 'considered', '')

    
    # Save to Excel
    df.to_excel(output_file, index=False)
    print(f"✅ Excel file created: {output_file}")
    
    # Create a summary
    print("\nSummary:")
    print(f"Total invoices processed: {len(all_data)}")
    print(f"Invoices with validation issues: {sum(1 for d in all_data if d.get('validation_issues') != 'No issues')}")
    print(f"Average quality score: {sum(d.get('quality_score', 0) for d in all_data) / len(all_data):.2f}")
    
    return output_file

# Main execution
if __name__ == "__main__":
    input_dir = r"C:\Users\george.nadrag\00. Coduri structurate\01. Gemini OCR PDF to TXT\OUT"
    output_dir = r"C:\Users\george.nadrag\00. Coduri structurate\02. Structurare TXT to XLSX"
    
    print("Starting invoice extraction process...")
    output_file = process_txt_to_excel(input_dir, output_dir)
    print(f"Process completed. Output file: {output_file}")