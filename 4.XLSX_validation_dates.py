"""
Step 4 - Process data and extract service dates using Gemini
"""

import os
import re
import json
import sys
import pandas as pd
import datetime
import concurrent.futures
import time
import google.generativeai as genai
from dotenv import load_dotenv
from config import config
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load API key
load_dotenv()
API_KEY = config.GEMINI_API_KEY
if not API_KEY or API_KEY == "your_gemini_api_key_here":
    raise EnvironmentError("[ERROR] GEMINI_API_KEY not set.")
genai.configure(api_key=API_KEY)

# Paths
input_excel = config.DATE_VALIDATION_INPUT
out_base = config.DATE_VALIDATION_OUTPUT
output_excel = os.path.join(out_base, "4.transformed_data.xlsx")

# Settings
BATCH_SIZE = config.API_BATCH_SIZE
API_DELAY = config.API_DELAY_SECONDS
MAX_RETRIES = config.API_MAX_RETRIES
DEBUG_MODE = False
service_dates_cache = {}

model = genai.GenerativeModel(config.GEMINI_MODEL)

def parse_invoice_date(date_str):
    if pd.isna(date_str) or date_str == "":
        return None
    try:
        return pd.to_datetime(date_str, dayfirst=True, errors='coerce')
    except:
        return None

def get_month_start_end(date):
    if date is None:
        return None, None
    month_start = date.replace(day=1)
    next_month = month_start + relativedelta(months=1)
    month_end = next_month - relativedelta(days=1)
    return month_start, month_end

def validate_date_range(start_date_str, end_date_str, invoice_date_str):
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%d/%m/%Y')
        end_date = datetime.datetime.strptime(end_date_str, '%d/%m/%Y')
        invoice_date = datetime.datetime.strptime(invoice_date_str, '%d/%m/%Y')
        if end_date < start_date:
            return False
        if (end_date - start_date).days > 366:
            return False
        six_months = relativedelta(months=6)
        return invoice_date - six_months <= start_date <= invoice_date + six_months
    except:
        return False

def extract_service_dates(items, invoice_date_str, cache_key=None):
    if cache_key and cache_key in service_dates_cache:
        return service_dates_cache[cache_key]

    invoice_date = parse_invoice_date(invoice_date_str)
    if invoice_date is None:
        return {"date_serv_start": "N/A", "date_serv_end": "N/A"}

    month_start, month_end = get_month_start_end(invoice_date)
    invoice_date_fmt = invoice_date.strftime('%d/%m/%Y')
    month_start_fmt = month_start.strftime('%d/%m/%Y')
    month_end_fmt = month_end.strftime('%d/%m/%Y')
    text = "\n".join([str(item) for item in items if item])

    prompt = f"""
Extract the start and end date of the service period mentioned in the following invoice description. Dates can be in formats like DD/MM/YYYY, DD.MM.YYYY, or even just month/year (e.g., SEPTEMBRIE 2024, sept, sept 24, Luna septembrie, Month September, nSEPT etc.).

From the invoice description, try to identify when the service likely started and ended, or in other words, what period the invoice covers.

If no date is found for both start and end, return "N/A" for both.

The invoice date is {invoice_date_fmt}. Determine the first and last day of the invoice month ({invoice_date_fmt}).
❗  If the extracted service period starts on the first day and ends on the last day of the invoice month, return:
{{
  "date_serv_start": "N/A",
  "date_serv_end": "N/A"
}}

TEXT:
{text}

Return only this JSON:
{{
  "date_serv_start": "DD/MM/YYYY" or "N/A",
  "date_serv_end": "DD/MM/YYYY" or "N/A"
}}
"""

    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(prompt)
            raw = response.text
            match = re.search(r'\{.*?"date_serv_start".*?"date_serv_end".*?\}', raw, re.DOTALL)
            if match:
                result = json.loads(match.group())
                date_pattern = r'^(\d{2}/\d{2}/\d{4}|N/A)$'
                start_date_valid = re.match(date_pattern, result['date_serv_start']) or result['date_serv_start'] == 'N/A'
                end_date_valid = re.match(date_pattern, result['date_serv_end']) or result['date_serv_end'] == 'N/A'
                if start_date_valid and end_date_valid:
                    if result['date_serv_start'] != 'N/A' and result['date_serv_end'] != 'N/A':
                        if not validate_date_range(result['date_serv_start'], result['date_serv_end'], invoice_date_fmt):
                            result = {"date_serv_start": "N/A", "date_serv_end": "N/A"}
                    if cache_key:
                        service_dates_cache[cache_key] = result
                    return result
        except:
            time.sleep(2)

    fallback = {
        "date_serv_start": month_start_fmt,
        "date_serv_end": month_end_fmt
    }
    if cache_key:
        service_dates_cache[cache_key] = fallback
    return fallback

def is_vat_valid(total, net, vat):
    try:
        if any(pd.isna(x) for x in [total, net, vat]):
            return False
        return abs((net + vat) - total) <= 0.001 * total
    except:
        return False

def process_invoice_batch(batch_rows):
    results = []
    for row in batch_rows:
        row_copy = row.copy()
        if row.get("considered") == 1:
            items_str = str(row.get('items_details', []))
            invoice_date = str(row.get('invoice_date', ''))
            cache_key = f"{items_str}_{invoice_date}"
            dates = extract_service_dates(row.get('items_details', []), row.get('invoice_date'), cache_key)
            row_copy['date_serv_start'] = dates.get('date_serv_start', "N/A")
            row_copy['date_serv_end'] = dates.get('date_serv_end', "N/A")
        else:
            row_copy['date_serv_start'] = "N/A"
            row_copy['date_serv_end'] = "N/A"
        row_copy['vat_valid'] = is_vat_valid(
            row.get('total_amount'),
            row.get('total_without_vat'),
            row.get('vat_amount')
        )
        results.append(row_copy)
    return results

def main():
    print(f"[INFO] Starting Step 4 - Processing data and extracting service dates")
    try:
        df = pd.read_excel(input_excel)
        print(f"[SUCCESS] Loaded Excel with {len(df)} records")
    except Exception as e:
        print(f"[ERROR] Error loading Excel file: {e}")
        return

    df['path'] = df.apply(
        lambda row: row['path'] if isinstance(row.get('path'), str) and row['path'].startswith('=HYPERLINK')
        else f'=HYPERLINK("{config.PDF_INPUT_DIR}/{row["pdf_name"].replace("_ocr", "")}.pdf", "{row["pdf_name"].replace("_ocr", "")}.pdf")',
        axis=1
    )

    rows = df.to_dict('records')
    batches = [rows[i:i+BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]
    print(f"[INFO] Split data into {len(batches)} batches")

    all_results = []
    with tqdm(total=len(batches), desc="Processing batches") as pbar:
        for i, batch in enumerate(batches):
            with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
                sub_batches = [[row] for row in batch]
                futures = [executor.submit(process_invoice_batch, sb) for sb in sub_batches]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        all_results.extend(future.result())
                    except Exception as e:
                        print(f"[ERROR] Error processing batch: {e}")
            pbar.update(1)
            if i < len(batches) - 1:
                time.sleep(API_DELAY)

    os.makedirs(out_base, exist_ok=True)
    df_out = pd.DataFrame(all_results)

    new_cols = ['date_serv_start', 'date_serv_end', 'vat_valid']
    priority_cols = ['path', 'considered', 'pdf_copied', 'pdf_error']
    rest_cols = [col for col in df_out.columns if col not in new_cols and col not in priority_cols]
    ordered_cols = [col for col in priority_cols + new_cols + rest_cols if col in df_out.columns]
    df_out = df_out[ordered_cols]

    try:
        df_out.to_excel(output_excel, index=False)
        print(f"[SUCCESS] Step 4 done. Output saved to: {output_excel}")
    except Exception as e:
        print(f"[ERROR] Error saving Excel file: {e}")

    print(f"[INFO] API Cache statistics:")
    print(f"  - Total cache entries: {len(service_dates_cache)}")
    print(f"[INFO] Processing statistics:")
    print(f"  - Total invoices processed: {len(all_results)}")
    print(f"  - Invoices with valid dates: {sum(1 for r in all_results if r.get('date_serv_start') != 'N/A')}")
    print(f"  - Invoices with valid VAT: {sum(1 for r in all_results if r.get('vat_valid', False))}")

if __name__ == "__main__":
    main()
