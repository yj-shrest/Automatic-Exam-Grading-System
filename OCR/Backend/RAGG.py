from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pypdf import PdfReader
import torch
import nltk
# nltk.download('punkt')
from nltk.tokenize import sent_tokenize
import os  # For file operations
import pickle  # For saving and loading numpy embeddings

# 1. Choose SentenceTransformer Model
model_name = 'BAAI/bge-base-en-v1.5'
model = SentenceTransformer(model_name)

# --- Helper Functions ---

def load_pdf(file_path):
    """Loads a PDF and returns a list of pages."""
    reader = PdfReader(file_path)
    text_by_page = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_by_page.append(text)
    return text_by_page

def encode_pages(pages, model):
    """Encodes the pages using the SentenceTransformer model."""
    embeddings = []
    for page in pages:
        embedding = model.encode(page, convert_to_tensor=False)  # Ensure NumPy array
        embeddings.append(embedding)  # Append embedding directly
    return embeddings

def create_faiss_index(embeddings):
    """Creates a FAISS index from the embeddings."""
    embedding_dimension = embeddings[0].shape[0]  # Get dimension from the 1D array
    index = faiss.IndexFlatL2(embedding_dimension)
    embeddings_array = np.stack(embeddings, axis=0).astype('float32')  # Use np.stack
    index.add(embeddings_array)
    return index

def retrieve_relevant_pages(query, model, index, pages, top_k=5):
    """Retrieves relevant pages."""
    query_embedding = model.encode(query, convert_to_tensor=False)  # Ensure NumPy array
    D, I = index.search(np.expand_dims(query_embedding.astype('float32'), axis=0), top_k)  # expand dims for FAISS
    relevant_pages = [pages[i] for i in I[0]]
    return relevant_pages

# --- New Functions for Server ---

def encode_and_save(file_name):
    """
    Encodes a PDF and saves the embeddings and FAISS index to files.

    Parameters:
        file_path (str): Path to the PDF file.
        embeddings_path (str): Path to save the embeddings (pickle file).
        index_path (str): Path to save the FAISS index file.
    """
    try:
        Directory = "Database/"+file_name+"/"
        os.makedirs(Directory, exist_ok=True)
        file_path = Directory+file_name+".pdf"
        embeddings_path =Directory + file_name+"_embeddings.pkl"
        index_path = Directory + file_name+".faiss"
        pdf_pages = load_pdf(file_path)
        embeddings = encode_pages(pdf_pages, model)
        index = create_faiss_index(embeddings)

        # Save embeddings using pickle
        with open(embeddings_path, "wb") as f:
            pickle.dump(embeddings, f)

        # Save FAISS index
        faiss.write_index(index, index_path)

        print(f"Successfully encoded and saved embeddings to {embeddings_path} and index to {index_path}")

    except Exception as e:
        print(f"Error during encoding and saving: {e}")

def retrieve_pages(query, file_name, top_k=3):
    print(query)
    print(file_name)
    Directory = "Database/"+file_name+"/"
    os.makedirs(Directory, exist_ok=True)
    file_path = Directory+file_name+".pdf"
    embeddings_path =Directory + file_name+"_embeddings.pkl"
    index_path = Directory + file_name+".faiss"
    try:
        # Load embeddings
        with open(embeddings_path, "rb") as f:
            embeddings = pickle.load(f)

        # Load FAISS index
        index = faiss.read_index(index_path)

        # Load Pages:
        pdf_pages = load_pdf(file_path)

        # Error check to ensure loading completed.
        if len(pdf_pages) == 0 or len(embeddings) == 0:
            raise("Error when loading pages. Check filepaths")

        #Check if the database has changed
        if len(pdf_pages) != len(embeddings):
            raise("PDF changed: Rebuild embedding and FAISS Index")

        #Load the documents into the index
        if index.ntotal != len(embeddings):
            raise("Number of embeddings does not match the Index")


        # Ensure everything worked
        relevant_pages = retrieve_relevant_pages(query, model, index, pdf_pages, top_k)

        return relevant_pages

    except FileNotFoundError:
        print("One of the important resources (PDF or database) is not found, please ensure that the encode function was completed")
        return []
    except Exception as e:
        print(f"An error occurred during page retrieval: {e}")
        return []

if __name__ == "__main__":
    # Encode and Save
    # encode_and_save("AI_Summary")
    # Retrieve Pages
    relevant_pages = retrieve_pages("{'<OCR>': '1. What happens to the value of current when thevalue of resistance is halved if it isconnected in series with a battery.'}", "Physics_Class_12", top_k=1)
    print("Relevant Pages:")
    for page in relevant_pages:
        print(page)
    if torch.cuda.is_available():
        del model
        torch.cuda.empty_cache()  # Clear GPU memory

    print("Code Complete.")