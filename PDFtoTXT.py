import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import os

def extract_text_from_pdf(pdf_path, output_text_file):
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    text = ""

    # Extract text from each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text("text")  # Extract text from the PDF page

        # Convert page to image (to detect any text in images)
        images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1)

        # Apply OCR to the images
        for image in images:
            text += pytesseract.image_to_string(image)

    # Write the extracted text to the output text file
    with open(output_text_file, 'w', encoding='utf-8') as f:
        f.write(text)

# Example usage
pdf_path = "./Data/1-110-ONLINE_VS09.pdf"
output_text_file = "output_text.txt"
extract_text_from_pdf(pdf_path, output_text_file)
