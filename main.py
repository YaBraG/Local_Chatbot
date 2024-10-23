import os
import sys
import platform
import subprocess

def add_directory_to_path(directory):
    # Add the directory to the current session's PATH
    if directory not in os.environ['PATH']:
        os.environ['PATH'] = directory + os.pathsep + os.environ['PATH']
        print(f"Directory '{directory}' added to PATH.")
    else:
        print(f"Directory '{directory}' is already in PATH.")

    # Add permanently for Windows
    if platform.system() == 'Windows':
        subprocess.run(['setx', 'PATH', os.environ['PATH']], check=True)

def setup_environment():
    python_dir = os.path.dirname(sys.executable)
    current_os = platform.system()

    # Add Python directories to PATH based on OS
    if current_os == 'Windows':
        add_directory_to_path(python_dir)
        add_directory_to_path(os.path.join(python_dir, 'Scripts'))
    elif current_os in ['Linux', 'Darwin']:  # Darwin is macOS
        add_directory_to_path(python_dir)
        add_directory_to_path(os.path.join(python_dir, 'bin'))

        # Update .bashrc/.zshrc for permanent change
        shell_profile = os.path.expanduser("~/.bashrc" if current_os == 'Linux' else "~/.zshrc")
        with open(shell_profile, 'a') as file:
            file.write(f'\n# Added by Python script\nexport PATH="{python_dir}:${{PATH}}"\n')
        print(f"To make changes permanent, run: source {shell_profile}")

def install_requirements():
    # Exit if requirements.txt is missing
    if not os.path.exists("requirements.txt"):
        print("requirements.txt not found, exiting.")
        sys.exit(1)

    # Run setup.py to install dependencies
    try:
        subprocess.check_call([sys.executable, "setup.py"])
    except subprocess.CalledProcessError as e:
        print(f"Error running setup.py: {e}")
        sys.exit(1)

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def load_and_split_documents(pdf_folder_path):
    from langchain_community.document_loaders import PDFMinerLoader
    from langchain_text_splitters import CharacterTextSplitter

    # Load PDFs into documents
    pdf_files = [f for f in os.listdir(pdf_folder_path) if f.endswith(".pdf")]
    docs = []
    for pdf_file in pdf_files:
        loader = PDFMinerLoader(os.path.join(pdf_folder_path, pdf_file))
        docs.extend(loader.load())

    # Split documents into chunks
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=2000, chunk_overlap=200)
    return text_splitter.split_documents(docs)

def setup_llm_retrieval():
    from langchain_community.llms import Ollama
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain.chains import RetrievalQA

    # Initialize embeddings and FAISS index
    embeddings = HuggingFaceEmbeddings()
    docs = load_and_split_documents("./Data")
    db = FAISS.from_documents(docs, embeddings)

    # Set up LLM and RetrievalQA chain
    llm = Ollama(model="llama3")
    return RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

def interactive_chat(chain):
    chat_history = []

    # Infinite loop for interaction
    while True:
        try:
            question = input("Enter Prompt (CTRL + C to stop): ")
            chat_history.append(f"User: {question}")

            # Invoke chain with question and chat history
            result = chain.invoke({"query": question, "chat_history": "\n".join(chat_history)})
            chat_history.append(f"Bot: {result['result']}")

            print(f"Response: {result['result']}\n")
        except KeyboardInterrupt:
            print("\nExiting chat...")
            break

def main():
    # Setup environment and install dependencies
    setup_environment()
    install_requirements()

    # Clear screen before starting
    clear_screen()

    # Set up the LLM and retrieval chain
    chain = setup_llm_retrieval()

    # Start the interactive chat
    interactive_chat(chain)

if __name__ == "__main__":
    main()
