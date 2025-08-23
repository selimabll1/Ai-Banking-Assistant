import os
import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# === PARAMÈTRES ===
PDF_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "atb_documents")  # Correct folder name for PDFs
CHUNK_SIZE = 500  # Max size of each chunk
EMBEDDING_MODEL_NAME = "paraphrase-MiniLM-L6-v2"
FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index.bin")  # Path to save the FAISS index
DOC_STORE_PATH = os.path.join(os.path.dirname(__file__), "chunks_store.npy")  # Path to save document chunks

# Initialize SentenceTransformer for embedding generation
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
index = faiss.IndexFlatL2(384)  # Initialize FAISS index, 384 dimensions for MiniLM embeddings

document_chunks = []

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def split_into_chunks(text, size=CHUNK_SIZE):
    """Split the document text into smaller chunks."""
    return [text[i:i+size] for i in range(0, len(text), size)]

def process_pdfs(folder_path):
    """Process all PDFs in the folder to extract chunks and update the FAISS index."""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            path = os.path.join(folder_path, filename)
            # Skip PDF if it has already been processed
            if filename in [f.split("/")[-1] for f in document_chunks]:  
                continue

            print(f"📄 Loading: {filename}")
            full_text = extract_text_from_pdf(path)
            chunks = split_into_chunks(full_text)
            
            # Generate embeddings for chunks
            embeddings = np.array(embedding_model.encode(chunks))  
            
            # Ensure embeddings are in the correct shape (2D array)
            print(f"Embeddings shape before reshaping: {embeddings.shape}")
            
            if embeddings.ndim == 1:
                embeddings = embeddings.reshape(-1, 384)  # Assuming embedding size is 384
            
            print(f"Embeddings shape after reshaping: {embeddings.shape}")

            # Add embeddings to FAISS index
            index.add(embeddings)
            document_chunks.extend(chunks)  # Store chunks for later use
            print(f"✅ {len(chunks)} chunks added")


# === START PROCESSING ===
process_pdfs(PDF_FOLDER)

# Save the FAISS index and document chunks
faiss.write_index(index, FAISS_INDEX_PATH)
np.save(DOC_STORE_PATH, document_chunks)
print("💾 Index and documents saved.")  # Output confirmation
