from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb

#Part A
reader = PdfReader("syllabus.pdf")
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

#Part B
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)
chunks = text_splitter.split_text(full_text)

#PART C : Printing to crosscheck the chunks created
print(f"Total chunks created: {len(chunks)}")
print("---")

for chunk in chunks[:3]:
    print(chunk)
    print("\n--- NEXT CHUNK ---\n")

#Introducing chromadb (the vector database to store the chunks created from the syllabus.pdf file)
persistent_client = chromadb.PersistentClient(path="chroma_db")
collection = persistent_client.get_or_create_collection("syllabus")

chunk_ids = [f"chunk_{i}" for i in range(len(chunks))]


collection.add(
    documents=chunks,
    metadatas=[{"source": "syllabus.pdf"}] * len(chunks),
    ids=chunk_ids
)

print("Successfully saved to Chroma!")