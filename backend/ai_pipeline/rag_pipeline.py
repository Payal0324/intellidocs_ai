
import google.generativeai as genai
import os
import re
import streamlit as st

api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

class RAGPipeline:
    def __init__(self):
        self.gemini_api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=self.gemini_api_key)

    def _build_prompt(self, query: str, retrieved_chunks: list, chat_history: list = None) -> str:
        prompt_parts = [
            """You are an AI assistant for IntelliDocs. Your primary goal is to answer questions accurately
            based SOLELY on the provided document excerpts. If the answer cannot be found in the provided
            documents, state that you don't have enough information.
            Cite sources from the 'Retrieved Documents' section by mentioning the Document ID and Page number (e.g., (Doc: ID, Page: Num)).
            Do not invent information or use your general knowledge.
            """
        ]
        if retrieved_chunks:
            prompt_parts.append("""--- Retrieved Documents ---""")
            for i, chunk in enumerate(retrieved_chunks):
                content = chunk.get('content', 'N/A')
                doc_id = chunk.get('document_id', 'N/A')
                page_num = chunk.get('page_number', 'N/A')
                prompt_parts.append(
                     f"Document ID: {doc_id}, Page: {page_num}:\n{content}"
                )

        if chat_history:
            prompt_parts.append("""--- Chat History ---""")
            for entry in chat_history:
                prompt_parts.append(f"User: {entry.get('question', '')}")
                prompt_parts.append(f"Assistant: {entry.get('answer', '')}")

        prompt_parts.append("""--- User Query ---""")
        prompt_parts.append(query)

        return "\n\n".join(prompt_parts)

    def generate_answer(self, query: str, retrieved_chunks: list, chat_history: list = None) -> dict:
        prompt_text = self._build_prompt(query, retrieved_chunks, chat_history)

        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt_text)

            ai_answer = response.text

            citations = []
            citation_pattern = re.compile(r'\(Doc: ([A-Za-z0-9_]+), Page: (\d+)\)')
            found_citations = citation_pattern.findall(ai_answer)

            for doc_id, page_num in found_citations:
                citations.append({'document_id': doc_id, 'page_number': int(page_num)})

            return {'answer': ai_answer, 'citations': citations}

        except Exception as e:
            print(f"Error generating content from Gemini: {e}")
            ai_answer = "An error occurred while generating the answer."
            if hasattr(e, 'text'):
                ai_answer = e.text
                found_citations = citation_pattern.findall(ai_answer)
                for doc_id, page_num in found_citations:
                    citations.append({'document_id': doc_id, 'page_number': int(page_num)})
            return {'answer': ai_answer, 'citations': citations, 'error': str(e)}
