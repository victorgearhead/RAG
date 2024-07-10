from pymongo import MongoClient
import datetime
import requests
from bs4 import BeautifulSoup
import fitz
import os
from pypdf import PdfReader
import ascii_magic
import concurrent.futures
import time

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

    document = {
        "title": title,
        "content": content,
        "source": source,
        "date_added": datetime.datetime.utcnow()
    }
    db.documents.insert_one(document)
    client.close()

def wikipedia(wikipedia_title):
    wikipedia_content = fetch_wikipedia_page(wikipedia_title)
    print(wikipedia_content)
    if wikipedia_content:
        store_document(wikipedia_title, wikipedia_content, 'Wikipedia')

def pdf():
    pdf_file_path = "Principles_of_Electronic_Materials_and_D.pdf"
    pdf_content = run_with_timeout(extract_pdf_text, pdf_file_path, timeout=60)
    if pdf_content:
        store_document('PDF Document', pdf_content, 'PDF')
