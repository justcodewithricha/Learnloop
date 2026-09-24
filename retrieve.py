import chromadb

persistent_client = chromadb.PersistentClient(path="chroma_db")
collection = persistent_client.get_or_create_collection("syllabus")

my_question = "What is information security?"

results = collection.query(
    query_texts=[my_question], 
    n_results=1  # Number of top results to return
)

print(results["documents"])