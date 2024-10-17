import os
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PDFMinerLoader

# Clear screen to only display Prompt and Response
print("\033c")

# Path to the folder containing PDF files
pdf_folder_path = "./Data"

# Get a list of all PDF files in the folder
pdf_files = [f for f in os.listdir(pdf_folder_path) if f.endswith(".pdf")]

# Load all PDFs in the folder
docs = []
for pdf_file in pdf_files:
    loader = PDFMinerLoader(os.path.join(pdf_folder_path, pdf_file))
    docs.extend(loader.load())  # Load and add documents to the list

# Split documents into chunks
text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=2000,
    chunk_overlap=200
)
texts = text_splitter.split_documents(docs)

# Initialize embeddings and FAISS index
embeddings = HuggingFaceEmbeddings()
db = FAISS.from_documents(texts, embeddings)

# Set up the LLM (Ollama in this case) and the RetrievalQA chain
llm = Ollama(model="llama3")
chain = RetrievalQA.from_chain_type(
    llm,
    retriever=db.as_retriever()
)

# Clear screen to only display Prompt and Response
print("\033c")

# Infinite loop for prompt and response
while True:
    # Input question and pass to the LLM
    question = input("Enter Prompt (CTRL + C to stop): ")
    result = chain.invoke({"query": question})
    print(f"Response : {result['result']}\n")
