from pymongo import MongoClient
import datetime
from RAG import pdf, extract_pdf_text, wikipedia, fetch_wikipedia_page, store_document
from langchain_core.prompts import ChatPromptTemplate
import transformers
import torch
import numpy as np
from huggingface_hub import InferenceClient
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import fitz
import os
from pypdf import PdfReader
import ascii_magic
import concurrent.futures
import time

app = FastAPI()

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

llm = InferenceClient(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    token="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",
)

class QueryRequest(BaseModel):
    user_prompt: str
    question: str
    wikipedia_title: str

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
    return []

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

@app.post("/view_history")
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

@app.post("/generate_answer")
def start(query: QueryRequest):
    user_prompt = query.user_prompt
    question = query.question
    if question.lower() in ['exit', 'quit']:
        return
    response = generate_answer(user_prompt, question)
    return {response}

def get_history(user_prompt):
    history = get_conversation_history(user_prompt)
    for entry in history:
        print(f"{entry['timestamp']} - You: {entry['user_input']} | {user_prompt}: {entry['model_response']}") 


def fetch_wikipedia_page(title):
    base_url = "https://en.wikipedia.org/wiki/"
    url = base_url + title.replace(" ", "_")

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.find('div', {'class': 'mw-content-ltr mw-parser-output'})
        paragraphs = content.find_all('p')
        page_text = "\n".join([para.get_text() for para in paragraphs])
        return page_text.strip()
    else:
        return None

def convert_image_to_ascii(image_data):
    image_path = "temp_image.png"
    with open(image_path, 'wb') as f:
        f.write(image_data)

    output = ascii_magic.from_image(image_path)
    return output

def run_with_timeout(func, *args, timeout):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")

def extract_pdf_text(file_path):
    try:
        text = ""
        reader = PdfReader(file_path)
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            text_here = page.extract_text()
            for j, image in enumerate(page.images):
                image_data = image.data
                ascii_art = convert_image_to_ascii(image_data)
                text += f"\n\nImage {text_here} \n{ascii_art}\n"

    except NotImplementedError as e:
        text = ""
        reader = PdfReader(file_path)
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
    except ValueError as e:
        text = ""
        reader = PdfReader(file_path)
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()

    return text

def store_document(title, content, source):
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client.rag_database

    embedding = model.encode(content)

    document = {
        "title": title,
        "content": content,
        "source": source,
        "date_added": datetime.datetime.utcnow(),
        "embedding": embedding.tolist()
    }
    db.documents.insert_one(document)
    client.close()

@app.post("/search_wiki")
def wikipedia(query:QueryRequest):
    wikipedia_title = query.wikipedia_title
    wikipedia_content = fetch_wikipedia_page(wikipedia_title)
    print(wikipedia_content)
    if wikipedia_content:
        store_document(wikipedia_title, wikipedia_content, 'Wikipedia')
    else:
        raise HTTPException(status_code=404, detail="Wikipedia page not found")

@app.post("/search_pdf")
def pdf(file: UploadFile = File(...)):
    pdf_file_path = f"temp_files/{file.filename}"
    with open(pdf_file_path, "wb") as buffer:
        buffer.write(file.file.read())
    pdf_content = run_with_timeout(extract_pdf_text, pdf_file_path, timeout=60)
    if pdf_content:
        store_document('PDF Document', pdf_content, 'PDF')
    else:
        raise HTTPException(status_code=400, detail="PDF extraction failed")