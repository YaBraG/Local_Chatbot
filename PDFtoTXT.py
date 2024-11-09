import os
import fitz  # PyMuPDF

def extract_plain_text_with_fitz(pdf_path):
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    full_text = ""
    
    # Loop through all the pages
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text("text")  # Extract plain text (without font details)
        full_text += text
    
    pdf_document.close()
    return full_text

def convert_all_pdfs_in_folder(folder_path):
    # List all PDF files in the folder
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        text = extract_plain_text_with_fitz(pdf_path)
        
        # Save text to a .txt file with the same name as the PDF
        txt_file_name = os.path.splitext(pdf_file)[0] + ".txt"
        txt_path = os.path.join(folder_path, txt_file_name)
        
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)
        print(f"Converted {pdf_file} to {txt_file_name}")

# Usage
folder_path = "./Data"
convert_all_pdfs_in_folder(folder_path)