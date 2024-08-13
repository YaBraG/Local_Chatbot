from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain_ollama import ChatOllama
from langchain.docstore.document import Document

llm = Ollama(model="llama3")
llm = ChatOllama(model = "llama3",temperature=0,#other parameters...
                )
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

documents = [
    Document(page_content="./ai_adoption_framework_whitepaper.pdf",metadata={"id":0})
]

vector_store = Chroma.from_documents(documents,embedding=embeddings)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever()
)

queries = input("Enter Prompt: ")


response = qa_chain.run(queries)
print(f"Query: {queries}\nResponse : {response}\n")

# message = [("system","You are a helpful assistant that translates English to French. Translate the user sentence."),("human","I love the pink")]
# ai_msg = llm.invoke(message)
# print(ai_msg)
