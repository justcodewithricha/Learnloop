import chromadb
import ollama

persistent_client = chromadb.PersistentClient(path="chroma_db")
collection = persistent_client.get_or_create_collection("syllabus")

my_question = "What is information security?"

results = collection.query(
    query_texts=[my_question], 
    n_results=1  # Number of top results to return
)

retrieved_text = results["documents"][0][0]

prompt = f"""
You are an expert tutor. Using ONLY the syllabus text below, generate a medium-difficulty quiz question about Information Security.

Syllabus Text:
{retrieved_text}
"""

print("Asking Qwen...")
response = ollama.chat(model='qwen', messages=[
  {
    'role': 'user',
    'content': prompt,
  },
])

print("\n--- AI QUIZ QUESTION ---")
print(response['message']['content'])