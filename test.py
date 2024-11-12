import os
import sys
import platform
import subprocess
import time
import fitz  # PyMuPDF

data_path = "./Data"
combined_txt_path = os.path.join(data_path, "combined_text.txt")
converted_log_file = "converted_pdfs.txt"

# Function to add directory to PATH
def add_directory_to_path(directory):
    if directory not in os.environ['PATH']:
        os.environ['PATH'] = directory + os.pathsep + os.environ['PATH']
        print(f"Directory '{directory}' added to PATH.")
    else:
        print(f"Directory '{directory}' is already in PATH.")

    if platform.system() == 'Windows':
        subprocess.run(['setx', 'PATH', os.environ['PATH']], check=True)

# Setup environment based on the operating system
def setup_environment():
    python_dir = os.path.dirname(sys.executable)
    current_os = platform.system()

    if current_os == 'Windows':
        add_directory_to_path(python_dir)
        add_directory_to_path(os.path.join(python_dir, 'Scripts'))
    elif current_os in ['Linux', 'Darwin']:
        add_directory_to_path(python_dir)
        add_directory_to_path(os.path.join(python_dir, 'bin'))

        shell_profile = os.path.expanduser("~/.bashrc" if current_os == 'Linux' else "~/.zshrc")
        with open(shell_profile, 'a') as file:
            file.write(f'\n# Added by Python script\nexport PATH="{python_dir}:${{PATH}}"\n')
        print(f"To make changes permanent, run: source {shell_profile}")

# Install requirements based on a setup.py file
def install_requirements():
    if not os.path.exists("requirements.txt"):
        print("requirements.txt not found, exiting.")
        sys.exit(1)

    try:
        subprocess.check_call([sys.executable, "setup.py"])
    except subprocess.CalledProcessError as e:
        print(f"Error running setup.py: {e}")
        sys.exit(1)

# Clear screen for a clean output
def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

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
    return output_filename

def convert_all_pdfs_in_folder(pdf_folder, output_folder, combined_output_file, log_file=converted_log_file):
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            converted_pdfs = set(file.read().splitlines())
    else:
        converted_pdfs = set()

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    newly_converted = []

    with open(combined_output_file, "w", encoding="utf-8") as combined_file:
        for pdf_file in pdf_files:
            if pdf_file not in converted_pdfs:
                pdf_path = os.path.join(pdf_folder, pdf_file)
                print(f"Converting {pdf_file}...")
                txt_path = convert_pdf_to_txt(pdf_path, output_folder)
                with open(txt_path, "r", encoding="utf-8") as txt_file:
                    combined_file.write(txt_file.read() + "\n\n")
                newly_converted.append(pdf_file)
                with open(log_file, "a") as log_file_obj:
                    log_file_obj.write(pdf_file + "\n")

# Chatbot System Prompt Integration
from langchain.text_splitter import CharacterTextSplitter

class Document:
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata or {}

def load_and_split_combined_text(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print("Combined text file is empty or missing.")
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    doc = Document(content)
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=2000, chunk_overlap=200)
    return text_splitter.split_documents([doc])

def setup_llm_retrieval():
    from langchain_community.llms import Ollama
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain.chains import RetrievalQA

    embeddings = HuggingFaceEmbeddings()

    # Load and split documents; check for empty docs
    docs = load_and_split_combined_text(combined_txt_path)
    if not docs:
        print("No documents available for embedding. Exiting.")
        sys.exit(1)

    db = FAISS.from_documents(docs, embeddings)

    llm = Ollama(model="llama3", clean_up_tokenization_spaces=True)  # Explicitly set for tokenization warning
    return RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

# Chat Interface with System Prompt
def interactive_chat(chain):
    chat_history_file = "chat_history.txt"

    # Define system prompt for guiding the LLM
    system_prompt = (
        "You are an informative chatbot dedicated to providing detailed information "
        "about the authors participating in the Miami Book Fair. Answer questions "
        "accurately, focusing on the authors' biographies, books, genres, achievements, "
        "and scheduled events or sessions."
    )

    if os.path.exists(chat_history_file):
        with open(chat_history_file, "r", encoding="utf-8") as file:
            chat_history = file.read().splitlines()
    else:
        chat_history = [f"System: {system_prompt}"]

    while True:
        try:
            question = input("Enter Prompt (CTRL + C to stop): ")
            chat_history.append(f"User: {question}")

            result = chain.invoke({
                "query": question,
                "chat_history": "\n".join(chat_history[-1024:]),  # Limit to last 1024 characters
                "system_message": system_prompt
            })

            response = result['result'].replace("Based on the provided context, ", "")
            chat_history.append(f"Bot: {response}")

            with open(chat_history_file, "w", encoding="utf-8") as file:
                file.write("\n".join(chat_history[-1024:]))  # Truncate history if too long

            print(f"Response: {response}\n")
        except KeyboardInterrupt:
            print("\nExiting chat...")
            break

# Main Execution Flow
def main():
    start = time.process_time()

    # Convert PDFs to combined TXT file if necessary
    convert_all_pdfs_in_folder(data_path, data_path, combined_txt_path)

    # Setup environment and install dependencies
    setup_environment()
    install_requirements()

    # Clear screen before starting
    clear_screen()

    # Set up the LLM and retrieval chain
    chain = setup_llm_retrieval()

    # Print processing time
    print("Processing time:", time.process_time() - start)

    # Start the interactive chat
    interactive_chat(chain)

if __name__ == "__main__":
    main()
