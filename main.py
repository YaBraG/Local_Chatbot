import os
import sys
import platform
import subprocess
import time
import fitz  # PyMuPDF

data_path = "./Data"
combined_txt_file = "combined_text.txt"

# Specify the directory path where `ollama` is installed
ollama_dir = r"C:\path\to\ollama"  # Update this with the actual path

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
        add_directory_to_path(ollama_dir)  # Add ollama to PATH
    elif current_os in ['Linux', 'Darwin']:
        add_directory_to_path(python_dir)
        add_directory_to_path(os.path.join(python_dir, 'bin'))
        add_directory_to_path(ollama_dir)  # Add ollama to PATH

# Install requirements if not already installed
def install_requirements():
    if os.path.exists("requirements.txt"):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            sys.exit(1)
    else:
        print("requirements.txt not found, exiting.")
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
    return os.path.basename(pdf_path)  # Return the name of the converted PDF

def convert_pdfs_in_folder(pdf_folder, output_folder):
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
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

# Chatbot System Prompt Integration
from langchain.text_splitter import CharacterTextSplitter

class Document:
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata or {}

def load_and_split_documents(combined_file_path):
    with open(combined_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    docs = [Document(content)]
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=100000, chunk_overlap=200)
    return text_splitter.split_documents(docs)  # type: ignore

def setup_llm_retrieval():
    from langchain_community.llms import Ollama
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain.chains import RetrievalQA

    embeddings = HuggingFaceEmbeddings()

    # Convert PDFs in the folder and combine all txt files into one
    convert_pdfs_in_folder(data_path, data_path)
    combine_txt_files(data_path, os.path.join(data_path, combined_txt_file))

    # Load and split documents from the combined text file
    docs = load_and_split_documents(os.path.join(data_path, combined_txt_file))
    db = FAISS.from_documents(docs, embeddings)

    # Pull the model using Ollama
    llm = Ollama(model="llama3")
    return RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

# Chat Interface with System Prompt
def interactive_chat(chain):
    chat_history = []

    # Define system prompt for guiding the LLM
    system_prompt = (
        "You are not allowed to say that you are referring to the context."
        "You are an informative chatbot dedicated to providing detailed information "
        "about the authors participating in the Miami Book Fair. Answer questions "
        "accurately, focusing on the authors' biographies, books, genres, achievements, "
        "and scheduled events or sessions. Be concise yet comprehensive in your responses."
    )
    chat_history.append(f"System: {system_prompt}")

    while True:
        try:
            question = input("Enter Prompt (CTRL + C to stop): ")
            chat_history.append(f"User: {question}")

            # Pass the system prompt alongside the user query and chat history to the chain
            result = chain.invoke({
                "query": question,
                "chat_history": "\n".join(chat_history[-5:]),  # Keep only the last 5 interactions
                "system_message": system_prompt  # Pass the prompt directly here
            })
            chat_history.append(f"Bot: {result['result']}")

            # Print the response
            response = result['result']
            print(f"Response: {response}\n")
        except KeyboardInterrupt:
            print("\nExiting chat...")
            break

# Main Execution Flow
def main():
    start = time.process_time()

    # Setup environment and install dependencies if not installed
    setup_environment()
    install_requirements()

    # Set up the LLM and retrieval chain
    chain = setup_llm_retrieval()

    # Clear screen before starting
    clear_screen()
    
    # Print processing time
    print("Processing time:", time.process_time() - start)

    # Start the interactive chat
    interactive_chat(chain)

if __name__ == "__main__":
    main()
