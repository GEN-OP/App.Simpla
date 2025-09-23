import os
from config import config

# Define your folders
in_dir = config.PDF_INPUT_DIR
out_dir = config.PDF_OUTPUT_DIR

# Confirm action
confirm = input(f"⚠️ WARNING: This will delete ALL PDFs in:\n{in_dir}\nand ALL TXT files in:\n{out_dir}\n\nType 'yes' to confirm: ")

if confirm.lower() == 'yes':
    # Delete PDFs
    for f in os.listdir(in_dir):
        if f.lower().endswith(".pdf"):
            os.remove(os.path.join(in_dir, f))

    # Delete TXT files
    for f in os.listdir(out_dir):
        if f.lower().endswith(".txt"):
            os.remove(os.path.join(out_dir, f))

    print("✅ Deleted all PDFs in IN and TXT files in OUT.")
else:
    print("❌ Action cancelled.")
