
import os
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2',
                 chunk_size: int = 1000, chunk_overlap: int = 200):
        self.model = SentenceTransformer(model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def generate_embeddings_for_document_pages(self, extracted_data: list, document_id: str) -> list:
        all_chunks = []
        for item in extracted_data:
            page_content = item['page_content']
            page_number = item['metadata']['page_number']
            texts = self.text_splitter.split_text(page_content)

            for text in texts:
                all_chunks.append({
                    'content': text,
                    'document_id': document_id,
                    'page_number': page_number
                })

        if not all_chunks:
            return []

        chunk_contents = [chunk['content'] for chunk in all_chunks]
        embeddings = self.model.encode(chunk_contents, show_progress_bar=False).tolist()

        embeddings_with_metadata = []
        for i, chunk in enumerate(all_chunks):
            embeddings_with_metadata.append({
                'embedding': embeddings[i],
                'content': chunk['content'],
                'document_id': chunk['document_id'],
                'page_number': chunk['page_number']
            })
        return embeddings_with_metadata

    def generate_query_embedding(self, query: str) -> list:
        query_embedding = self.model.encode(query).tolist()
        return query_embedding
