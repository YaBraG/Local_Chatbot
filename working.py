import subprocess
import os
import sys

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
