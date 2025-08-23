import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

FAISS_INDEX_PATH = "chatbot/faiss_index.bin"  # Path to the FAISS index
DOC_STORE_PATH = "chatbot/chunks_store.npy"  # Path to the document chunks
EMBEDDING_MODEL_NAME = "paraphrase-MiniLM-L6-v2"  # Model for embedding generation

# Load the embedding model
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Load the FAISS index and document chunks
faiss_index = faiss.read_index(FAISS_INDEX_PATH)
document_chunks = np.load(DOC_STORE_PATH, allow_pickle=True)

def retrieve_chunks(query, k=5, max_chunk_length=300):
    """
    Retrieve the most relevant document chunks from the FAISS index based on a query.
    
    Args:
    - query (str): The user input query.
    - k (int): Number of relevant chunks to retrieve.
    - max_chunk_length (int): Maximum length of each chunk to avoid too long context.
    
    Returns:
    - list: List of the most relevant chunks.
    """
    query_vec = embedding_model.encode([query])  # Get the embedding for the query
    _, I = faiss_index.search(np.array(query_vec), k)  # Perform the similarity search

    relevant_chunks = []
    for i in I[0]:  # Loop through the retrieved indices
        chunk = document_chunks[i]
        
        # If the chunk is too long, truncate it to the max length
        if len(chunk) > max_chunk_length:
            chunk = chunk[:max_chunk_length]  # Truncate the chunk
        
        relevant_chunks.append(chunk)

    return relevant_chunks
