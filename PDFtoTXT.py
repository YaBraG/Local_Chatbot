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

# Usage
pdf_path = "./Data/1-110-ONLINE_VS09.pdf"
text = extract_plain_text_with_fitz(pdf_path)
with open("output_plain_fitz.txt", "w", encoding="utf-8") as file:
    file.write(text)
