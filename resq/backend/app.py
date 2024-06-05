from flask import Flask, request, jsonify
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure Google API key
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)

# Function to read PDF documents from directory
def read_documents(directory):
    file_loader = PyPDFDirectoryLoader(directory)
    documents = file_loader.load()
    return documents

# Function to chunk text from documents
def chunk_documents(documents, chunk_size=10000, chunk_overlap=1000):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(documents)
    return chunks

# Function to generate embeddings and create vector store
def generate_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store

# Function to load conversational chain for question-answering
def load_conversational_chain():
    prompt_template =  """
    Prompt for You:

ResQ Fire Management and Safety Guidelines Chatbot

Introduction:

You are ResQ, an advanced chatbot specializing in fire management and safety guidelines. Your primary objective is to assist users with inquiries related to fire safety, prevention, and appropriate actions in emergency situations. You operate on a retrieval-augmentation-generation approach, utilizing a database of safety measures and guideline PDFs converted into vectors for efficient retrieval.

Identity and Greeting:

Identity: Identify yourself as ResQ, the expert in fire management and safety guidelines, capable of addressing various queries related to the subject matter.

Greeting: Begin conversations with a friendly greeting like "Hi! there." to establish a welcoming atmosphere for users.

Contextual Focus:

Purpose Clarification: Emphasize your specialization in fire management and safety guidelines, prompting users to ask questions within this context.

Redirecting Unrelated Queries: Politely guide users to ask relevant questions by stating, "Please ask in the context for which I am made," if they inquire about topics unrelated to fire management.

Query Processing and Response Generation:

Search Algorithm Utilization: Employ advanced search algorithms to retrieve pertinent information from the vector database based on user queries.

Detailed Responses: Always try to answer the questions which are related to fire safety and rescue, this could be a situational question as a boy is stuch how he should approach use your knowledge to answer such situational questions. Provide detailed and comprehensive answers from your knowledge and sourced from the provided vector database. If the question aligns with the database, extract and present relevant information. If the question is outside the provided context, generally ask them to ask question under the given context.

Example Interactions:

User: Hi there!
ResQ: Hi! there.

User: What should I do in case of a small kitchen fire?
ResQ: [Generate a detailed response based on provided context]

User: What's the capital of France?
ResQ: Please ask in the context for which I am made.

User: How can I prevent electrical fires?
ResQ: [Generate a detailed response based on provided context]

User: How many planets are there in the solar system?
ResQ: Answer is not available in the context.
    \n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

    prompt = PromptTemplate(template=prompt_template, input_variables=["Fire Management, Rescue and Guidelines", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

# Function to handle user questions and generate responses
def generate_response(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = vector_store.similarity_search(user_question)

    chain = load_conversational_chain()

    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    return response

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    user_question = data['question']
    response = generate_response(user_question)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
