from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()
os.environ['GOOGLE_API_KEY'] = "AIzaSyC9qPWj-QckNC2z1-SYJJhf8rdUZOae4lk"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
            else:
                print(f"Warning: No text found on page {page} of {pdf}")
    if not text:
        raise ValueError("No text was extracted from the PDFs.")
    return text



def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    if not chunks:
        raise ValueError("No text chunks were created from the input text.")
    print(f"Created {len(chunks)} chunks.")
    return chunks



def get_vector_store(text_chunks):
    if not text_chunks:
        raise ValueError("No text chunks to process.")

   
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma.from_texts(text_chunks, embedding=embeddings, persist_directory="chroma_index")
    
   
    collection = vector_store.get()
    if not collection or len(collection['ids']) == 0:
        raise ValueError("No valid embeddings generated or stored. Please check the input text or model.")
    
   
    vector_store.persist()




def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details.
    If the answer is not in the provided context, say, "answer is not available in the context."
    Context:\n {context}\n
    Question:\n{question}\n
    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain


@app.route("/process", methods=["POST"])
def process_pdfs():
    files = request.files.getlist("pdfs[]")
    raw_text = get_pdf_text(files)
    text_chunks = get_text_chunks(raw_text)
    get_vector_store(text_chunks)
    return jsonify({"status": "Success", "message": "PDFs processed and vector store updated"})


@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    user_question = data.get("question")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = Chroma(persist_directory="chroma_index", embedding_function=embeddings)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    return jsonify({"reply": response["output_text"]})


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
