from pymongo import MongoClient
import datetime
from RAG import pdf, extract_pdf_text, wikipedia, fetch_wikipedia_page, store_document
from email_RAG import mail_view, fetch_emails, send_mail, send_email
from langchain_core.prompts import ChatPromptTemplate
import transformers
import torch
import numpy as np
from huggingface_hub import InferenceClient
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

llm = InferenceClient(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    token="",
)

def fetch_documents(query):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.rag_database

    query_embedding = model.encode(query)
    documents = db.documents.find()

    similarities = []
    for doc in documents:
        if 'embedding' in doc:
            doc_embedding = np.array(doc['embedding'])
            similarity = np.dot(query_embedding, doc_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding))
            similarities.append((doc, similarity))
    if similarities:
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_documents = similarities[:10]
        client.close()
        return [doc[0] for doc in top_documents]
    return

def create_custom_prompt(user_prompt, documents):
    
    prompt = f"{user_prompt}"
    
    if documents:
        temp=""
        for doc in documents:
            temp += f"Title: {doc['title']}\nContent: {doc['content']}\n\n"
    
        prompt =f"{user_prompt}, Return this to user {temp}"

    return prompt

def save_conversation(user_prompt, user_input, model_response):
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client.rag_database

    conversation = {
        "user_prompt": user_prompt,
        "user_input": user_input,
        "model_response": model_response,
        "timestamp": datetime.datetime.utcnow()
    }
    db.conversations.insert_one(conversation)
    
    client.close()

def get_conversation_history(user_prompt, limit=10):
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client.rag_database

    history = list(db.conversations.find({"user_prompt": user_prompt}).sort("timestamp", -1).limit(limit))
    
    client.close()
    return history

def generate_answer(user_prompt, question):

    documents = fetch_documents(question)
    custom_prompt = create_custom_prompt(user_prompt, documents)
    response = ""
    for message in llm.chat_completion(
        messages=[{"role": "system", "content": f"{custom_prompt}"},
                  {"role":"user", "content":f"{question}"}],
        max_tokens=500,
        stream=True,
    ):
        response += message.choices[0].delta.content
    save_conversation(user_prompt, question, response)
    return custom_prompt

def start(user_prompt, question):
    if question.lower() in ['exit', 'quit']:
        return
    response = generate_answer(user_prompt, question)
    print(response)

def get_history(user_prompt):
    history = get_conversation_history(user_prompt)
    for entry in history:
        print(f"{entry['timestamp']} - You: {entry['user_input']} | {user_prompt}: {entry['model_response']}")


start('You talk like Captain Jack Sparrow', 'Talk to me about 3rd chapter from Atomic Habits book by James Clear')   