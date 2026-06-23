
import fitz  # PyMuPDF
import re

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_from_pdf(self, pdf_path: str) -> list:
        doc = fitz.open(pdf_path)
        extracted_data = []
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text()
            extracted_data.append({
                'page_content': text,
                'metadata': {'page_number': page_num + 1}
            })
        doc.close()
        return extracted_data

    def clean_text(self, text: str) -> str:
        # Remove multiple newlines and excessive whitespace
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def chunk_text(self, extracted_data: list, document_id: str) -> list:
        chunks = []
        for item in extracted_data:
            page_content = item['page_content']
            page_number = item['metadata']['page_number']
            cleaned_text = self.clean_text(page_content)

            if not cleaned_text:
                continue

            # Simple character-based chunking with overlap
            start_idx = 0
            while start_idx < len(cleaned_text):
                end_idx = start_idx + self.chunk_size
                chunk_text = cleaned_text[start_idx:end_idx]

                chunks.append({
                    'content': chunk_text,
                    'metadata': {
                        'document_id': document_id,
                        'page_number': page_number,
                        'start_index': start_idx,
                        'end_index': min(end_idx, len(cleaned_text))
                    }
                })
                start_idx += (self.chunk_size - self.chunk_overlap)
                if start_idx >= len(cleaned_text): # Ensure loop terminates if chunk_size - chunk_overlap is 0 or negative
                    break

        return chunks
