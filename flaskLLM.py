import os
import platform
import torch
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

# Paths for data and the combined text file
data_path = "./Data"
combined_txt_file = "combined_text.txt"

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

    # Load and split the combined text file
    docs = load_and_split_documents(os.path.join(data_path, combined_txt_file))

    # Use FAISS to index documents
    db = FAISS.from_documents(docs, embeddings)

    # Set up the LLM using Ollama
    llm = Ollama(model="llama3")
    return RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

# Chat Interface to interact with the system
def interactive_chat(chain, prompt):
    chat_history = []
    system_prompt = (
        "You are an informative chatbot dedicated to providing detailed information "
        "about the authors participating in the Miami Book Fair. Answer questions "
        "accurately and concisely."
    )
    chat_history.append(f"System: {system_prompt}")

    # while True:
    try:
        # chat_history.append(f"User: {question}")
        result = chain.invoke({
            "query": prompt,
            "chat_history": "\n".join(chat_history[-5:]),
            "system_message": system_prompt
        })
        chat_history.append(f"Bot: {result['result']}")
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


