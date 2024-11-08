import os
import sys
import platform
import subprocess

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

def load_and_split_documents(txt_folder_path):
    from langchain.text_splitters import CharacterTextSplitter

    txt_files = [f for f in os.listdir(txt_folder_path) if f.endswith(".txt")]
    docs = []
    for txt_file in txt_files:
        with open(os.path.join(txt_folder_path, txt_file), 'r', encoding='utf-8') as file:
            content = file.read()
            docs.append(content)

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

    while True:
        try:
            question = input("Enter Prompt (CTRL + C to stop): ")
            chat_history.append(f"User: {question}")

            result = chain.invoke({"query": question, "chat_history": "\n".join(chat_history)})
            chat_history.append(f"Bot: {result['result']}")

            print(f"Response: {result['result']}\n")
        except KeyboardInterrupt:
            print("\nExiting chat...")
            break

def main():
    setup_environment()
    install_requirements()

    clear_screen()

    chain = setup_llm_retrieval()
    interactive_chat(chain)

if __name__ == "__main__":
    main()
