from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
from pdf2image import convert_from_path

# 🌱 Load environment variables from .env
load_dotenv()

# 🔐 Get API key securely from environment
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("❌ GEMINI_API_KEY not set in .env file.")

genai.configure(api_key=API_KEY)

# 📄 Convert PDF to images
def convert_pdf_to_images(pdf_path):
    print(f"📄 Converting PDF to images: {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return []
    return convert_from_path(pdf_path)

# 🧠 Perform OCR on a single image using Gemini 1.5 Flash
def ocr_image(image, page_number):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Extract ALL text visible in this invoice image (page {page_number}).
    Include every line of text exactly as it appears.
    Capture all product descriptions, quantities, prices and especially dates and date intervals.
    Preserve the table structure as much as possible.
"""
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        print(f"❌ OCR failed on page {page_number}: {e}")
        return ""

# 🚀 OCR for a single PDF
def ocr_pdf(pdf_path, output_txt_path):
    images = convert_pdf_to_images(pdf_path)
    if not images:
        print("❌ No images to process.")
        return

    for idx, img in enumerate(images):
        print(f"🔍 Processing page {idx + 1}/{len(images)}...")
        page_text = ocr_image(img, idx + 1)
        with open(output_txt_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n--- Page {idx + 1} ---\n{page_text}")
        print(f"✅ Page {idx + 1} processed and saved to {output_txt_path}")

# 📂 Batch OCR for all PDFs in input folder
def batch_ocr(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("❗ No PDF files found in input directory.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        base_name = os.path.splitext(pdf_file)[0]
        output_file = os.path.join(output_dir, f"{base_name}_ocr.txt")

        print(f"\n📘 Starting OCR for: {pdf_file}")
        ocr_pdf(pdf_path, output_file)
        print(f"✅ Completed OCR for: {pdf_file}\nSaved to: {output_file}")

# 🧪 Main entry
if __name__ == "__main__":
    input_dir = r"C:\Users\george.nadrag\00. Coduri structurate\01. Gemini OCR PDF to TXT\IN"
    output_dir = r"C:\Users\george.nadrag\00. Coduri structurate\01. Gemini OCR PDF to TXT\OUT"
    batch_ocr(input_dir, output_dir)
