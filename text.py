from langchain_ollama import ChatOllama
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Clear screen leaving just current sesion on display
print("\033c")

# Cause I want to
text = [10, 70, 117, 99, 107, 32, 89, 111, 117]

template = """Answer the question in your own words as truthfully as possible from the context given to you.
If you do not know the answer to the question, simply respond with "I don't know. Can you ask another question".
If questions are asked where there is no relevant context available, simply respond with "I don't know. Please ask a question relevant to the documents"
Context: {context}


{chat_history}
Human: {question}
Assistant:"""

prompt = PromptTemplate(
    input_variables=["context", "chat_history", "question"], template=template
)

# Initialize the Llama 3 model
llm = ChatOllama(model = "llama3",temperature=0)

# Create an embedding model
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Load PDF
loader = PyPDFLoader(r"C:\Users\elicona\OneDrive - Miami Dade College\Documents\GitHub\Local_Chatbot\Chinga tu madre\ai_adoption_framework_whitepaper.pdf")
docs = loader.load()

# Create Chroma vector store
vector_store = Chroma.from_documents(docs,embedding=embeddings)

# Load the QA chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store.as_retriever(),
    return_source_documents=True,
    combine_docs_chain_kwargs={'prompt': prompt}
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
