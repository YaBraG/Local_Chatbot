import os
import sys
import platform
import subprocess
import time
import fitz  # PyMuPDF

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
        text = page.get_text("text")
        full_text += text
    pdf_document.close()
    return full_text

def convert_pdf_to_txt(pdf_path, output_folder):
    text = extract_plain_text_with_fitz(pdf_path)
    output_filename = os.path.join(output_folder, os.path.basename(pdf_path).replace('.pdf', '.txt'))
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(text)
    return os.path.basename(pdf_path)  # Return the name of the converted PDF

def convert_all_pdfs_in_folder(pdf_folder, output_folder, converted_log_file="converted_pdfs.txt"):
    if os.path.exists(converted_log_file):
        with open(converted_log_file, "r") as file:
            converted_pdfs = set(file.read().splitlines())
    else:
        converted_pdfs = set()

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    newly_converted = []

    for pdf_file in pdf_files:
        if pdf_file not in converted_pdfs:
            pdf_path = os.path.join(pdf_folder, pdf_file)
            print(f"Converting {pdf_file}...")
            convert_pdf_to_txt(pdf_path, output_folder)
            newly_converted.append(pdf_file)
            with open(converted_log_file, "a") as log_file:
                log_file.write(pdf_file + "\n")

    if newly_converted:
        print(f"Converted {len(newly_converted)} new PDFs.")
    else:
        print("No new PDFs to convert.")

# Chatbot System Prompt Integration
from langchain.text_splitter import CharacterTextSplitter

class Document:
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata or {}

def load_and_split_documents(txt_folder_path):
    txt_files = [f for f in os.listdir(txt_folder_path) if f.endswith(".txt")]
    docs = []
    for txt_file in txt_files:
        with open(os.path.join(txt_folder_path, txt_file), 'r', encoding='utf-8') as file:
            content = file.read()
            docs.append(Document(content))

    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=2000, chunk_overlap=200)
    return text_splitter.split_documents(docs)

def setup_llm_retrieval():
    from langchain_community.llms import Ollama
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain.chains import RetrievalQA

    embeddings = HuggingFaceEmbeddings()
    docs = load_and_split_documents("./Data")
    db = FAISS.from_documents(docs, embeddings)

    llm = Ollama(model="llama3")
    return RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

# Chat Interface with System Prompt
def interactive_chat(chain):
    chat_history = []

    # Define system prompt for guiding the LLM
    system_prompt = (
        "You are an informative chatbot dedicated to providing detailed information "
        "about the authors participating in the Miami Book Fair. Answer questions "
        "accurately, focusing on the authors' biographies, books, genres, achievements, "
        "and scheduled events or sessions. Avoid prefacing responses with phrases like "
        "'Based on the provided context.' Be concise yet comprehensive in your responses."
    )
    chat_history.append(f"System: {system_prompt}")

    while True:
        try:
            # Convert PDFs to TXT files if necessary
            convert_all_pdfs_in_folder("./Data", "./Data")
            question = input("Enter Prompt (CTRL + C to stop): ")
            chat_history.append(f"User: {question}")

            # Pass the system prompt alongside the user query and chat history to the chain
            result = chain.invoke({
                "query": question,
                "chat_history": "\n".join(chat_history),
                "system_message": system_prompt  # Pass the prompt directly here
            })
            chat_history.append(f"Bot: {result['result']}")

            # Print the response, stripping any unwanted phrases
            response = result['result'].replace("Based on the provided context, ", "")
            print(f"Response: {response}\n")
        except KeyboardInterrupt:
            print("\nExiting chat...")
            break

# Main Execution Flow
def main():
    start = time.process_time()

    # Convert PDFs to TXT files if necessary
    convert_all_pdfs_in_folder("./Data", "./Data")

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
