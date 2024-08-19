from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PDFMinerLoader
from flask import Flask

app = Flask(__name__)

loader = PDFMinerLoader("./University Physics with Modern Physics 15th edition.pdf")
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

question = "Can you please summarize page 100 and answer the first question that appears"
result = chain.invoke({"query": question})

@app.route('/')
def index():
    return result['result']

if __name__ == "__main__":
    app.run(debug=True)