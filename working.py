import subprocess
import os
import sys
import platform

def add_python_to_path():
    # Get the current Python executable's path
    python_path = sys.executable
    python_dir = os.path.dirname(python_path)

    # Check the operating system
    current_os = platform.system()

    if current_os == 'Windows':
        # Add Python and Scripts directories to PATH for Windows
        new_path = f"{python_dir};{python_dir}\\Scripts"

        # Update PATH for the current session
        os.environ['PATH'] = new_path + ';' + os.environ['PATH']

        # Update PATH permanently using setx
        subprocess.run(['setx', 'PATH', os.environ['PATH']])

        print("Python has been added to the PATH for Windows.")
    
    elif current_os in ['Linux', 'Darwin']:  # Darwin is for macOS
        # Add Python and bin directories to PATH for Linux/macOS
        new_path = f"{python_dir}:{python_dir}/bin"

        # Update PATH for the current session
        os.environ['PATH'] = new_path + ':' + os.environ['PATH']

        # Provide instructions to add the path permanently
        shell_profile = os.path.expanduser("~/.bashrc" if current_os == 'Linux' else "~/.zshrc")
        
        with open(shell_profile, 'a') as file:
            file.write(f'\n# Added by Python script\nexport PATH="{new_path}:$PATH"\n')

        print(f"Python has been added to the PATH for {current_os}.")
        print(f"To make the changes permanent, restart your terminal or run:\nsource {shell_profile}")
    
    else:
        print(f"Unsupported OS: {current_os}. Cannot modify PATH.")

# Run the function
add_python_to_path()

def add_directory_to_path2(directory):
    # Add the directory to the current session's PATH
    os.environ['PATH'] = directory + ';' + os.environ['PATH']

    # Permanently add the directory to the PATH for Windows
    subprocess.run(['setx', 'PATH', os.environ['PATH']])

def same():
    # The directory from the warning
    scripts_dir = r'C:\Users\elicona\AppData\Roaming\Python\Python311\Scripts'

    # Check if the directory is already in PATH
    if scripts_dir not in os.environ['PATH']:
        add_directory_to_path2(scripts_dir)
        print(f"The directory '{scripts_dir}' has been added to PATH.")
    else:
        print(f"The directory '{scripts_dir}' is already in PATH.")

same()

# Exit if requirements.txt is missing
if not os.path.exists("requirements.txt"):
    print("requirements.txt not found, exiting.")
    exit()

# Run setup.py to install dependencies
subprocess.check_call([sys.executable, "setup.py"])

# Import necessary modules
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PDFMinerLoader

# Clear screen
print("\033c")

# Path to PDF files
pdf_folder_path = "./Data"

# List all PDF files in the folder
pdf_files = [f for f in os.listdir(pdf_folder_path) if f.endswith(".pdf")]

# Load PDFs into documents
docs = []
for pdf_file in pdf_files:
    loader = PDFMinerLoader(os.path.join(pdf_folder_path, pdf_file))
    docs.extend(loader.load())

# Split documents into chunks
text_splitter = CharacterTextSplitter(
    separator="\n", 
    chunk_size=2000, 
    chunk_overlap=200)
texts = text_splitter.split_documents(docs)

# Initialize embeddings and FAISS index
embeddings = HuggingFaceEmbeddings()
db = FAISS.from_documents(texts, embeddings)

# Set up LLM and RetrievalQA chain
llm = Ollama(model="llama3")
chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

# Clear screen
print("\033c")

# Track chat history
chat_history = []

# Infinite loop for interaction
while True:
    # Get user input
    question = input("Enter Prompt (CTRL + C to stop): ")
    
    # Add user question to chat history
    chat_history.append(f"User: {question}")
    
    # Invoke chain with question and chat history
    result = chain.invoke({
        "query": question,
        "chat_history": "\n".join(chat_history)
    })
    
    # Add response to chat history
    chat_history.append(f"Bot: {result['result']}")
    
    # Print response
    print(f"Response : {result['result']}\n")
