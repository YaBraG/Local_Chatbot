import fitz  # this is PyMuPDF

# Open a sample PDF
pdf_document = fitz.open("sample.pdf")
text = ""

# Extract text from the first page
page = pdf_document.load_page(0)
text = page.get_text("text")

print(text)
