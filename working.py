import os
import sys
import platform
import subprocess
import time
from PDFtoTXT import convert_all_pdfs_in_folder  # Import the PDF-to-TXT conversion function

def add_directory_to_path(directory):
    if directory not in os.environ['PATH']:
        os.environ['PATH'] = directory + os.pathsep + os.environ['PATH']
        print(f"Directory '{directory}' added to PATH.")
    else:
        print(f"Directory '{directory}' is already in PATH.")

    if platform.system() == 'Windows':
        subprocess.run(['setx', 'PATH', os.environ['PATH']], check=True)

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

def install_requirements():
    if not os.path.exists("requirements.txt"):
        print("requirements.txt not found, exiting.")
        sys.exit(1)

    try:
        subprocess.check_call([sys.executable, "setup.py"])
    except subprocess.CalledProcessError as e:
        print(f"Error running setup.py: {e}")
        sys.exit(1)

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

from langchain.text_splitter import CharacterTextSplitter

class Document:
    def __init__(self, content, metadata=None):
        self.page_content = content  # Store content in 'page_content' attribute
        self.metadata = metadata or {}  # Add an empty dictionary for 'metadata'

def load_and_split_documents(txt_folder_path):
    txt_files = [f for f in os.listdir(txt_folder_path) if f.endswith(".txt")]
    docs = []
    for txt_file in txt_files:
        with open(os.path.join(txt_folder_path, txt_file), 'r', encoding='utf-8') as file:
            content = file.read()
            docs.append(Document(content))  # Wrap content in Document with metadata

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

def interactive_chat(chain):
    chat_history = []
    
    # Add a system prompt to guide the LLM
    system_prompt = (
        "You are an informative chatbot dedicated to providing detailed information "
        "to the authors participating in the Miami Book Fair. Answer questions "
        "accurately, focusing on the authors' biographies, books, genres, achievements, "
        "and scheduled events or sessions. Be concise yet comprehensive in your responses."
        "Avoid sounding like you are guessing. You are an assistant that accurately answers"
        "to authors questions."
    )
    chat_history.append(f"System: {system_prompt}")

    while True:
        try:
            question = input("Enter Prompt (CTRL + C to stop): ")
            chat_history.append(f"User: {question}")

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

def main():
    # Start time measurement for performance tracking
    start = time.process_time()
    
    # Convert PDFs to TXT files
    convert_all_pdfs_in_folder("./Data")  # Run PDF-to-TXT conversion on all PDFs in the folder

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
