import os
import fitz

# Paths for data and the combined text file
data_path = "./Data"
combined_txt_file = "combined_text.txt"

# PDF-to-TXT Conversion Functions
def extract_plain_text_with_fitz(pdf_path):
    pdf_document = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text("text")  # type: ignore
        full_text += text
    pdf_document.close()
    return full_text

def convert_pdf_to_txt(pdf_path, output_folder):
    text = extract_plain_text_with_fitz(pdf_path)
    output_filename = os.path.join(output_folder, os.path.basename(pdf_path).replace('.pdf', '.txt'))
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(text)
    return os.path.basename(pdf_path)  # Return the name of the converted PDF

def convert_pdfs_in_folder(pdf_folder, output_folder):
    if not os.path.isdir(pdf_folder):
        print(f"Directory {pdf_folder} does not exist. Please check the path.")
        return

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found for conversion.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"Converting {pdf_file}...")
        convert_pdf_to_txt(pdf_path, output_folder)

def combine_txt_files(txt_folder_path, output_file):
    txt_files = [f for f in os.listdir(txt_folder_path) if f.endswith(".txt") and f != combined_txt_file]

    with open(output_file, "w", encoding="utf-8") as outfile:
        for txt_file in txt_files:
            with open(os.path.join(txt_folder_path, txt_file), "r", encoding="utf-8") as infile:
                outfile.write(infile.read() + "\n")

    # Remove individual txt files after combining, excluding the combined_txt_file
    for txt_file in txt_files:
        os.remove(os.path.join(txt_folder_path, txt_file))
        
    print("PDFs converted and text files combined successfully!")
        
        
if __name__ == "__main__":
    # Create the data path directory if it does not exist
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        
    # Convert PDFs in the folder and combine all txt files into one
    convert_pdfs_in_folder(data_path, data_path)
    combine_txt_files(data_path, os.path.join(data_path, combined_txt_file))
