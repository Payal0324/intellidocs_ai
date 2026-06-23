
import faiss
import numpy as np
import os
import pickle

class VectorStoreManager:
    def __init__(self, embedding_dimension: int = 384):
        self.index = None
        self.metadata_map = [] # Stores { 'content', 'document_id', 'page_number' }
        self.embedding_dimension = embedding_dimension

        if self.embedding_dimension is not None:
            self.index = faiss.IndexFlatL2(self.embedding_dimension)
        
    def add_embeddings(self, embeddings_with_metadata: list):
        if not embeddings_with_metadata:
            return

        embeddings_only = [item['embedding'] for item in embeddings_with_metadata]
        new_metadata = [{
            'content': item['content'],
            'document_id': item['document_id'],
            'page_number': item['page_number']
        } for item in embeddings_with_metadata]

        embeddings_np = np.array(embeddings_only).astype('float32')

        if self.index is None:
            self.embedding_dimension = embeddings_np.shape[1]
            self.index = faiss.IndexFlatL2(self.embedding_dimension)
        
        if embeddings_np.shape[1] != self.embedding_dimension:
            raise ValueError(
                f"Embedding dimension mismatch. Expected {self.embedding_dimension}, got {embeddings_np.shape[1]}."
            )

        self.index.add(embeddings_np)
        self.metadata_map.extend(new_metadata)

    def search_similar(self, query_embedding: list, k: int = 5) -> list:
        if self.index is None or self.index.ntotal == 0:
            return []

        query_np = np.array([query_embedding]).astype('float32')
        
        if query_np.shape[1] != self.embedding_dimension:
            raise ValueError(
                f"Query embedding dimension mismatch. Expected {self.embedding_dimension}, got {query_np.shape[1]}对了。"
            )

        distances, indices = self.index.search(query_np, k)

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1:
                results.append({
                    'content': self.metadata_map[idx]['content'],
                    'document_id': self.metadata_map[idx]['document_id'],
                    'page_number': self.metadata_map[idx]['page_number'],
                    'distance': distances[0][i].item()
                })
        return results

    def save_index(self, path: str):
        if self.index is None or self.index.ntotal == 0:
            print("No index to save or index is empty.")
            return

        os.makedirs(path, exist_ok=True)
        index_file = os.path.join(path, "faiss_index.bin")
        metadata_file = os.path.join(path, "metadata_map.pkl")

        faiss.write_index(self.index, index_file)
        with open(metadata_file, 'wb') as f:
            pickle.dump(self.metadata_map, f)

        # print(f"FAISS index and metadata saved to {path}")

    def load_index(self, path: str):
        index_file = os.path.join(path, "faiss_index.bin")
        metadata_file = os.path.join(path, "metadata_map.pkl")

        if not os.path.exists(index_file):
            # print(f"FAISS index file not found at {index_file}")
            self.index = None
            self.metadata_map = []
            return False

        if not os.path.exists(metadata_file):
            # print(f"Metadata map file not found at {metadata_file}")
            self.index = None # Invalidate index if metadata is missing
            self.metadata_map = []
            return False

        self.index = faiss.read_index(index_file)
        with open(metadata_file, 'rb') as f:
            self.metadata_map = pickle.load(f)

        self.embedding_dimension = self.index.d # Update embedding dimension from loaded index
        # print(f"FAISS index and metadata loaded from {path}. Total embeddings: {self.index.ntotal}")
        return True
