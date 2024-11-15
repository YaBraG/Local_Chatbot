import os
import sys
import warnings
from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter

# Paths for data and combined text file
data_path = "./Data"
combined_txt_file = "combined_text.txt"

# Suppress FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

class Document:
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata or {}

def load_and_split_documents(combined_file_path):
    try:
        with open(combined_file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: {combined_file_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading {combined_file_path}: {e}")
        sys.exit(1)

    docs = [Document(content)]
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000000, chunk_overlap=200)
    return text_splitter.split_documents(docs)  # type: ignore

def setup_llm_retrieval():
    # Initialize embeddings with clean_up_tokenization_spaces explicitly set
    embeddings = HuggingFaceEmbeddings()

    # Load and split documents from the combined text file
    docs = load_and_split_documents(os.path.join(data_path, combined_txt_file))
    db = FAISS.from_documents(docs, embeddings)

    # Pull the model using Ollama
    llm = OllamaLLM(model="llama3.1:8b")
    return RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

# Chat Interface with System Prompt
def interactive_chat(chain):
    chat_history = []

    # Define system prompt for guiding the LLM
    system_prompt = (
        "You are not allowed to say that you are referring to the context. "
        "You are an informative chatbot dedicated to providing detailed information "
        "about the authors participating in the Miami Book Fair. Answer questions "
        "accurately, focusing on the authors' biographies, books, genres, achievements, "
        "and scheduled events or sessions. Be concise yet comprehensive in your responses."
    )
    chat_history.append(f"System: {system_prompt}")

    while True:
        try:
            question = input("Enter Prompt (CTRL + C to stop): ")
            chat_history.append(f"User: {question}")

            # Pass the system prompt alongside the user query and chat history to the chain
            result = chain.invoke({
                "query": question,
                "chat_history": "\n".join(chat_history[-5:]),  # Keep only the last 5 interactions
                "system_message": system_prompt  # Pass the prompt directly here
            })
            chat_history.append(f"Bot: {result['result']}")

            # Print the response
            response = result['result']
            print(f"Response: {response}\n")
        except KeyboardInterrupt:
            print("\nExiting chat...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

# Main Execution Flow
def main():
    chain = setup_llm_retrieval()

    # Start the interactive chat
    interactive_chat(chain)

if __name__ == "__main__":
    main()
