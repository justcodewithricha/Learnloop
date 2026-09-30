import os
import chromadb
import ollama
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Connect to our local vector database
persistent_client = chromadb.PersistentClient(path="chroma_db")
collection = persistent_client.get_or_create_collection("syllabus")


def ingest_pdf(pdf_path):
    """
    Reads a PDF, breaks it into chunks, saves it to ChromaDB, 
    and asks Qwen to extract the main topics.
    """
    print(f"Ingesting {pdf_path}...")
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    # Chunk the text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(full_text)

    # To keep things clean for our prototype, let's empty the database before adding a new syllabus
    # (If collection is not empty, this deletes old data)
    existing_items = collection.get()
    if existing_items['ids']:
        collection.delete(ids=existing_items['ids'])

    # Save to Chroma
    chunk_ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(
        documents=chunks,
        metadatas=[{"source": os.path.basename(pdf_path)}] * len(chunks),
        ids=chunk_ids
    )

    # Use Qwen to extract topics from the first chunk (usually the intro/table of contents)
    prompt = f"""
    Based on the following text from a syllabus, extract 3 to 4 core topics or units.
    Return ONLY a comma-separated list of topics, nothing else. Example format: "Cryptography, Network Security, Access Control"
    
    Text: {chunks[0]}
    """
    print("Asking Qwen to extract topics...")
    response = ollama.chat(model='qwen', messages=[{'role': 'user', 'content': prompt}])
    
    # Clean up Qwen's response into a Python list
    topics_raw = response['message']['content']
    topics = [t.strip("-* \n") for t in topics_raw.split(',')]
    
    return topics


def generate_quiz(topic_name):
    """
    Searches ChromaDB for the requested topic, and asks Qwen 
    to generate a multiple-choice question using that text.
    """
    print(f"Generating quiz for topic: {topic_name}...")
    
    # 1. Retrieve the 2 most relevant chunks from Chroma
    results = collection.query(
        query_texts=[topic_name], 
        n_results=2
    )
    retrieved_text = "\n\n".join(results["documents"][0])
    
    # 2. Ask Qwen to write a question
    prompt = f"""
    You are an expert tutor. Using ONLY the syllabus text below, generate a medium-difficulty multiple-choice question about the topic: '{topic_name}'.
    Include 4 options (A, B, C, D) and briefly explain which one is correct at the very end.
    
    Syllabus Text:
    {retrieved_text}
    """
    
    response = ollama.chat(model='qwen', messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']
