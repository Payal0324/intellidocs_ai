
import google.generativeai as genai
import re
import streamlit as st

class Summarizer:
    def __init__(self, model_name: str = 'gemini-2.5-flash'):
        self.gemini_api_key = st.secrets["GOOGLE_API_KEY"]

        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel(model_name='gemini-2.5-flash')

    def summarize_text(self, text: str, max_words: int = 200) -> str:
        if not text.strip():
            return "No content provided for summarization."

        prompt = f"""Summarize the following text concisely, focusing on key information and main points. The summary should not exceed {max_words} words.

Text: {text}

Summary:"""
        try:
            response = self.model.generate_content(prompt)
            summary = response.text
            return summary
        except Exception as e:
            return f"Failed to generate summary due to an error: {e}"

    def extract_key_points(self, text: str, num_points: int = 5) -> list:
        if not text.strip():
            return []

        prompt = f"""From the following text, extract {num_points} most important key points as a numbered list. Each key point should be concise.

Text: {text}

Key Points:"""
        try:
            response = self.model.generate_content(prompt)
            key_points_str = response.text
            key_points = [
                point.strip()
                for point in key_points_str.split('\n')
                if point.strip() and re.match(r'^\d+\.', point.strip())
            ]
            return key_points
        except Exception as e:
            return [f"Failed to extract key points due to an error: {e}"]

    def identify_concepts(self, text: str, num_concepts: int = 5) -> list:
        if not text.strip():
            return []

        prompt = f"""From the following text, identify {num_concepts} important concepts or entities. List them as comma-separated terms.

Text: {text}

Important Concepts:"""
        try:
            response = self.model.generate_content(prompt)
            concepts_str = response.text
            concepts = [c.strip() for c in concepts_str.split(',') if c.strip()]
            return concepts
        except Exception as e:
            return [f"Failed to identify concepts due to an error: {e}"]
