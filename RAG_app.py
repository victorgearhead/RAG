from pymongo import MongoClient
import datetime
from RAG import pdf, extract_pdf_text, wikipedia, fetch_wikipedia_page, store_document
from email_RAG import mail_view, fetch_emails, send_mail, send_email
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama


# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.rag_database

# Initialize LangChain and Ollama
llm = Ollama(model='llama3')

def fetch_documents(query):
    return list(db.documents.find({"content": {"$regex": query, "$options": "i"}}))

def create_custom_prompt(character_name, documents):
    
    prompt = ChatPromptTemplate.from_messages([
        ("system",f"You are {character_name}."), 
        ("user", "{input}")])
    
    # if documents:
    #     temp=""
    #     for doc in documents:
    #         temp += f"Title: {doc['title']}\nContent: {doc['content']}\n\n"
    
    #     prompt = ChatPromptTemplate.from_messages([
    #         ("system",f"You are {character_name}. Return this to user {temp}"), 
    #         ("user", "{input}")])

    return prompt

def save_conversation(character_name, user_input, model_response):
    conversation = {
        "character_name": character_name,
        "user_input": user_input,
        "model_response": model_response,
        "timestamp": datetime.datetime.utcnow()
    }
    db.conversations.insert_one(conversation)

def get_conversation_history(character_name, limit=10):
    return list(db.conversations.find({"character_name": character_name}).sort("timestamp", -1).limit(limit))

def generate_answer(character_name, question):
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

def get_history(character_name):
    history = get_conversation_history(character_name)
    for entry in history:
        print(f"{entry['timestamp']} - You: {entry['user_input']} | {character_name}: {entry['model_response']}")

character_name = 'Jarvis'
question = 'Hi'

start(character_name, question)

# Close the MongoDB connection
client.close()
