from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PDFMinerLoader
from flask import Flask

# app = Flask(__name__)

loader = PDFMinerLoader("./Data/2023 MBF Author Tool Kit.pdf")
docs = loader.load()

text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=2000,
    chunk_overlap=200
)
texts = text_splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings()

db = FAISS.from_documents(texts, embeddings)

llm = Ollama(model="llama3")

chain = RetrievalQA.from_chain_type(
    llm,
    retriever=db.as_retriever()
)

while 1:
        # Input question and pass to llm
        question = input("Enter Prompt (CTRL + C to stop): ")
        result = chain.invoke({"query": question})
        print(f"Response : {result['result']}\n")
        
# @app.route('/')
# def index():
#     return result['result']

# if __name__ == "__main__":
#     app.run(debug=True)