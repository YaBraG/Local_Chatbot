import os
import sys
import platform
import subprocess

# Paths for data and the combined text file
data_path = "./Data"
combined_txt_file = "combined_text.txt"

# Setup environment based on the operating system
def setup_environment():
    python_dir = os.path.dirname(sys.executable)
    current_os = platform.system()

    # Add necessary directories to PATH for Windows or Linux/macOS
    if current_os == 'Windows':
        print("I AM IN THE WINDOWS ENV")
        add_directory_to_path(python_dir)
        add_directory_to_path(os.path.join(python_dir, 'Scripts'))
    elif current_os in ['Linux', 'Darwin']:
        print("I AM IN THE LINUX ENV")
        add_directory_to_path(python_dir)
        add_directory_to_path(os.path.join(python_dir, 'bin'))

def add_directory_to_path(directory):
    """ Adds a directory to the system PATH if not already present. """
    if directory not in os.environ['PATH']:
        os.environ['PATH'] = directory + os.pathsep + os.environ['PATH']
        # print(f"Added '{directory}' to PATH.")

# Install requirements if not already installed
def install_requirements():
    """ Installs dependencies from requirements.txt. """
    if os.path.exists("requirements.txt"):
        subprocess.check_call([sys.executable, "-m", "pip3", "install", "-r", "requirements.txt"])
    else:
        print("requirements.txt not found.")
        sys.exit(1)

# # Setup environment and install requirements if needed
# setup_environment() 

# # Set up the LLM and retrieval chain
# install_requirements()  

import fitz  # PyMuPDF
import torch
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
# PDF-to-TXT conversion using PyMuPDF
def extract_plain_text_with_fitz(pdf_path):
    """ Extracts plain text from a PDF file using PyMuPDF. """
    pdf_document = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        full_text += page.get_text("text")  # type: ignore # Extract text
    pdf_document.close()
    return full_text

def convert_pdf_to_txt(pdf_path, output_folder):
    """ Converts a single PDF to a TXT file. """
    text = extract_plain_text_with_fitz(pdf_path)
    output_filename = os.path.join(output_folder, os.path.basename(pdf_path).replace('.pdf', '.txt'))
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(text)
    return os.path.basename(pdf_path)

def convert_pdfs_in_folder(pdf_folder, output_folder):
    """ Converts all PDFs in the specified folder to TXT. """
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        # print(f"Converting {pdf_file}...")
        convert_pdf_to_txt(pdf_path, output_folder)

def combine_txt_files(txt_folder_path, output_file):
    """ Combines all TXT files in the folder into one output file. """
    txt_files = [f for f in os.listdir(txt_folder_path) if f.endswith(".txt") and f != combined_txt_file]
    with open(output_file, "w", encoding="utf-8") as outfile:
        for txt_file in txt_files:
            with open(os.path.join(txt_folder_path, txt_file), "r", encoding="utf-8") as infile:
                outfile.write(infile.read() + "\n")

    # Remove individual txt files after combining, except the combined one
    for txt_file in txt_files:
        os.remove(os.path.join(txt_folder_path, txt_file))

# Split and load documents
class Document:
    """ Represents a document with content and metadata. """
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata or {}

def load_and_split_documents(combined_file_path):
    """ Loads and splits the combined document into smaller chunks. """
    with open(combined_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    docs = [Document(content)]
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000000, chunk_overlap=200)
    return text_splitter.split_documents(docs) # type: ignore

# Setup LangChain with FAISS and LLM (Ollama)
def setup_llm_retrieval():
    """ Sets up the LLM retrieval system with FAISS and HuggingFace embeddings. """
    
    # Device selection: use GPU if available, else use CPU
    device = "cuda" if torch.cuda.is_available() and platform.system() != 'Windows' else "cpu"  # Avoid GPU on Windows

    # Model name for HuggingFace (ensure this model is available on HuggingFace Hub)
    model_name = "distilbert-base-uncased"  # Example model name, change it if needed

    # Setup embeddings with HuggingFaceEmbeddings and model_name
    embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={"device": device})

    # Convert PDFs and combine text files
    convert_pdfs_in_folder(data_path, data_path)
    combine_txt_files(data_path, os.path.join(data_path, combined_txt_file))

    # Load and split the combined text file
    docs = load_and_split_documents(os.path.join(data_path, combined_txt_file))

    # Use FAISS to index documents
    db = FAISS.from_documents(docs, embeddings)

    # Set up the LLM using Ollama
    llm = Ollama(model="llama3")
    return RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

# Chat Interface to interact with the system
def interactive_chat(chain, prompt):
    # """ Interactive chat loop to answer user questions. """
    # chat_history = []
    system_prompt = (
        "You are an informative chatbot dedicated to providing detailed information "
        "about the authors participating in the Miami Book Fair. Answer questions "
        "accurately and concisely."
    )
    # chat_history.append(f"System: {system_prompt}")

    # while True:
    try:
        # chat_history.append(f"User: {question}")
        result = chain.invoke({
            "query": prompt,
            # "chat_history": "\n".join(chat_history[-5:]),
            "system_message": system_prompt
        })
        # chat_history.append(f"Bot: {result['result']}")
        response = result['result']
        # print(f"INSIDE LIB RESPONCE: {response}\n")
        
        return response
    except KeyboardInterrupt:
        return "Exiting chat..."
            # break

 

# Start the interactive chat
chain = setup_llm_retrieval()

print("LLM INITIALIZED...")

# # Main function to start the execution
def ask_llm(prompt):
    return interactive_chat(chain, prompt)


