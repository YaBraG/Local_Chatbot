from os import path
from glob import glob
from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Clear screen leaving just current sesion on display
print("\033c")

# Cause I want to
text = [10, 70, 117, 99, 107, 32, 89, 111, 117]

# Initialize the Llama 3 model
llm = ChatOllama(model = "llama3",temperature=0.8)

# Create an embedding model
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
# try nomic 

# Load PDF
file_path = ("Data\\")
loader = PyPDFLoader(
    file_path = file_path,
    extract_images = True
    )
docs = loader.load()

# Create Chroma vector store
vector_store = Chroma.from_documents(docs,embedding=embeddings)

# Load the QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_store.as_retriever(),
)
# Clear screen to only display Prompt and Response
print("\033c")

# Program will keep runing until user force stop
try:
    while 1:
        # Input question and pass to llm
        question = input("Enter Prompt (CTRL + C to stop): ")
        response = qa_chain.invoke({"query": question})
        print(f"Response : {response['result']}\n")

# Error handling for when user force stop
except KeyboardInterrupt:
    # Cause I want to
    print ("".join([chr(item) for item in text]))
    
# Chatbot doesn't recognize previous response, meaning that there is no record of conversation happening. -Look into it
