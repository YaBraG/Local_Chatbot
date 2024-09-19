from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
print("\033c")

# Initialize the SentenceTransformer embeddings
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize Chroma vector store with the embeddings
vector_store = Chroma(embedding_model=embedding_model)

# Load or add your documents into the vector store
# For demonstration, let's say we have some sample texts
sample_texts = [
    "LangChain is a framework for developing applications powered by language models.",
    "Chatbots can assist in a variety of tasks, including customer support.",
    "Using embeddings, we can find semantically similar texts."
]

# Adding sample texts to the vector store
for text in sample_texts:
    vector_store.add_documents([text])

# Create a RetrievalQA chain with the ChatOllama model
chat_model = ChatOllama()
retrieval_qa = RetrievalQA(
    retriever=vector_store.as_retriever(),
    llm=chat_model
)

# Function to interact with the chatbot
def chat_with_bot(user_input):
    response = retrieval_qa.run(user_input)
    return response

# Main loop for chatting
if __name__ == "__main__":
    print("Chatbot is ready! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        response = chat_with_bot(user_input)
        print(f"Bot: {response}")
