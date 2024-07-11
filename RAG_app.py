from pymongo import MongoClient
import datetime
from RAG import pdf, extract_pdf_text, wikipedia, fetch_wikipedia_page, store_document
from email_RAG import mail_view, fetch_emails, send_mail, send_email
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama


def fetch_documents(query):

    client = MongoClient('mongodb://localhost:27017/')
    db = client.rag_database

    docs = list(db.documents.find({"content": {"$regex": query, "$options": "i"}}))
    
    client.close()

    return docs

def create_custom_prompt(character_name, documents):
    
    prompt = ChatPromptTemplate.from_messages([
        ("system",f"You are {character_name}."), 
        ("user", "{input}")])
    
    if documents:
        temp=""
        for doc in documents:
            temp += f"Title: {doc['title']}\nContent: {doc['content']}\n\n"
    
        prompt = ChatPromptTemplate.from_messages([
            ("system",f"You are {character_name}. Return this to user {temp}"), 
            ("user", "{input}")])

    return prompt

def save_conversation(character_name, user_input, model_response):
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client.rag_database

    conversation = {
        "character_name": character_name,
        "user_input": user_input,
        "model_response": model_response,
        "timestamp": datetime.datetime.utcnow()
    }
    db.conversations.insert_one(conversation)
    
    client.close()

def get_conversation_history(character_name, limit=10):
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client.rag_database

    history = list(db.conversations.find({"character_name": character_name}).sort("timestamp", -1).limit(limit))
    
    client.close()
    return history

def generate_answer(character_name, question):

    llm = Ollama(model='llama3')
    documents = fetch_documents(question)
    custom_prompt = create_custom_prompt(character_name, documents)
    chain = custom_prompt | llm
    response = chain.invoke({"input": f"{question}"})
    save_conversation(character_name, question, response)
    return response

def start(character_name, question):
    while True:
        if question.lower() in ['exit', 'quit']:
            break
        response = generate_answer(character_name, question)
        print(f"{response}")
        break

def get_history(character_name):
    history = get_conversation_history(character_name)
    for entry in history:
        print(f"{entry['timestamp']} - You: {entry['user_input']} | {character_name}: {entry['model_response']}")