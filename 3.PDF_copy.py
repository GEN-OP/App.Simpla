"""
Step 3 - Copy PDFs to appropriate folders based on 'considered' flag
Only performs file copy. No Excel output.
"""
import os
import shutil
import pandas as pd
import concurrent.futures
from tqdm import tqdm
from config import config

# Paths
excel_path = config.EXCEL_PATH
pdf_dir = config.PDF_INPUT_DIR
out_base = config.PDF_COPY_BASE_DIR

# Create output folders
considered_dir = os.path.join(out_base, "Considered")
not_considered_dir = os.path.join(out_base, "Not Considered")
os.makedirs(considered_dir, exist_ok=True)
os.makedirs(not_considered_dir, exist_ok=True)

def copy_pdf(row):
    pdf_name = str(row['pdf_name']).replace('_ocr', '') + ".pdf"
    src = os.path.join(pdf_dir, pdf_name)
    dst = considered_dir if row.get("considered") == 1 else not_considered_dir

    result = {
        'pdf_name': row['pdf_name'],
        'success': False,
        'error': None
    }

    if not os.path.exists(dst):
        os.makedirs(dst)

    if os.path.exists(src):
        target_path = os.path.join(dst, pdf_name)
        try:
            shutil.copy2(src, target_path)
            result['success'] = True
        except Exception as e:
            result['error'] = str(e)
    else:
        result['error'] = f"PDF not found: {src}"

    return result

def main():
    print(f"🔄 Starting Step 3 - Copying PDFs to appropriate folders")

    try:
        df = pd.read_excel(excel_path)
        print(f"✅ Loaded Excel with {len(df)} records")
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_row = {executor.submit(copy_pdf, row): idx for idx, row in df.iterrows()}
        for future in tqdm(concurrent.futures.as_completed(future_to_row), total=len(future_to_row), desc="Copying PDFs"):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

    success_count = sum(1 for r in results if r['success'])
    error_count = sum(1 for r in results if not r['success'])

    print(f"\n📊 Summary:")
    print(f"  - Total files processed: {len(results)}")
    print(f"  - Successfully copied: {success_count}")
    print(f"  - Errors: {error_count}")

if __name__ == "__main__":
    main()
