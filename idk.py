import fitz  # PyMuPDF
import os
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def extract_text_from_pdfs(folder_path):
    text_data = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            pdf_document = fitz.open(file_path)
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            text_data[filename] = text
    return text_data

def answer_question(question, pdf_folder_path):
    pdf_texts = extract_text_from_pdfs(pdf_folder_path)
    combined_text = "\n\n".join(pdf_texts.values())
    
    response = chain.run({
        "question": question,
        "pdf_text": combined_text
    })
    return response

# Initialize Ollama LLM
ollama_llm = Ollama()

# Define a prompt template
prompt_template = PromptTemplate(
    input_variables=["question", "pdf_text"],
    template="You are a helpful assistant. Based on the provided PDF text, answer the following question: {question}\n\nPDF Text:\n{pdf_text}"
)

# Create a chain
chain = LLMChain(
    llm=ollama_llm,
    prompt_template=prompt_template
)

if __name__ == "__main__":
    folder_path = r'C:\Users\elicona\OneDrive - Miami Dade College\Documents\GitHub\Local_Chatbot\Data'
    question = input("Ask your question: ")
    answer = answer_question(question, folder_path)
    print("Answer:", answer)
