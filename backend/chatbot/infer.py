from retriever import retrieve_chunks
from generator import generate_response

def get_response_rag(user_input):
    print("🔍 Récupération des documents pertinents...")
    context_chunks = retrieve_chunks(user_input, k=3)  # Just 3 chunks is enough now

    print("📚 Chunks extraits du PDF :")
    for i, chunk in enumerate(context_chunks, 1):
        print(f"  [{i}] {chunk[:100]}...")

    context = "\n\n".join(context_chunks)

    print("🧠 Envoi à Mistral via Ollama...")
    response = generate_response(user_input, context)
    print("✅ Réponse obtenue.\n")

    return response
