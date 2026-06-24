
import streamlit as st
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)
import uuid
import json # Import json for citations
from datetime import datetime

# Import backend modules
from backend.ai_pipeline.pdf_processor import PDFProcessor
from backend.ai_pipeline.embedding_generator import EmbeddingGenerator
from backend.ai_pipeline.vector_store_manager import VectorStoreManager
from backend.database.manager import DatabaseManager, Document, ChatHistory, Chunk, UserSession
from backend.ai_pipeline.rag_pipeline import RAGPipeline
from backend.ai_pipeline.summarizer import Summarizer # Import Summarizer

st.set_page_config(
    page_title="IntelliDocs AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

[data-testid="stSidebar"]{
background:#161B22;
}

[data-testid="stSidebar"] *{
color:white;
}

.stApp{
background:#F8FAFC;
}

div[data-testid="metric-container"]{
background:white;
border-radius:12px;
padding:15px;
box-shadow:0 2px 8px rgba(0,0,0,0.08);
}

.stButton button{
border-radius:10px;
font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# Custom CSS for a modern, premium UI/UX
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    :root {
        --primary-color: #4A90E2; /* Blue */
        --secondary-color: #50E3C2; /* Teal */
        --background-color: #F8F9FA; /* Light Gray */
        --card-background: #FFFFFF; /* White */
        --text-color: #343A40; /* Dark Gray */
        --light-text-color: #6C757D; /* Medium Gray */
        --border-color: #E0E0E0; /* Lighter Gray */
        --shadow-light: rgba(0, 0, 0, 0.08);
        --shadow-medium: rgba(0, 0, 0, 0.15);
    }

    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
        color: var(--text-color);
    }

    /* Main container and sidebar styling */
    .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .st-emotion-cache-1pxczg0.e1gf0tb51 > div {
        background-color: var(--background-color);
    }
    .st-emotion-cache-z5rd5b {
        background-color: var(--card-background);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px var(--shadow-light);
        border: 1px solid var(--border-color);
    }
    .st-emotion-cache-1pxczg0.e1gf0tb51 {
      padding-top: 1rem;
    }

    /* Header styling */
    .header-container {
        background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
        padding: 1.5rem 2rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 20px var(--shadow-medium);
        color: white;
        margin-bottom: 2rem;
    }
    .header-container h1, .header-container h2, .header-container h3 {
        color: white;
    }
    .header-container .stMarkdown p {
        color: rgba(255, 255, 255, 0.8);
    }

    /* Card styling */
    .st-emotion-cache-f60vps {
        background-color: var(--card-background);
        border-radius: 12px;
        box-shadow: 0 4px 15px var(--shadow-light);
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border-color);
    }
    .st-emotion-cache-f60vps:hover {
        box-shadow: 0 6px 20px var(--shadow-medium);
        transform: translateY(-2px);
        transition: all 0.3s ease-in-out;
    }

    /* Buttons */
    .st-emotion-cache-f705ad, .st-emotion-cache-q8spsw, .st-emotion-cache-1c19ifw { /* Added .st-emotion-cache-1c19ifw for primary button on dashboard */
        background-color: var(--primary-color);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.7rem 1.2rem;
        font-weight: 600;
        transition: background-color 0.2s ease;
    }
    .st-emotion-cache-f705ad:hover, .st-emotion-cache-q8spsw:hover, .st-emotion-cache-1c19ifw:hover {
        background-color: #3A7ABD; /* Darker Primary */
        color: white;
    }
    .st-emotion-cache-f705ad:focus, .st-emotion-cache-q8spsw:focus, .st-emotion-cache-1c19ifw:focus {
        box-shadow: 0 0 0 0.2rem rgba(74, 144, 226, 0.5);
    }

    /* Inputs */
    .st-emotion-cache-1c9f20d, .st-emotion-cache-135wmpj, .st-emotion-cache-1gjnkpt {
        border-radius: 8px;
        border: 1px solid var(--border-color);
        box-shadow: inset 0 1px 3px var(--shadow-light);
        padding: 0.5rem 1rem;
    }

    /* Sidebar navigation */
    .st-emotion-cache-zq5wmm.ezr6i8g1 > div:first-child {
        background-color: var(--card-background);
        padding: 1rem;
        border-radius: 0 12px 12px 0;
        box-shadow: 4px 0 15px var(--shadow-light);
    }
    .st-emotion-cache-zq5wmm.ezr6i8g1 .st-emotion-cache-1y48h6w a {
        color: var(--text-color);
        text-decoration: none;
        padding: 0.8rem 1rem;
        margin: 0.2rem 0;
        border-radius: 8px;
        transition: background-color 0.2s ease, color 0.2s ease;
        display: flex;
        align-items: center;
    }
    .st-emotion-cache-zq5wmm.ezr6i8g1 .st-emotion-cache-1y48h6w a:hover {
        background-color: rgba(74, 144, 226, 0.1);
        color: var(--primary-color);
    }
    .st-emotion-cache-zq5wmm.ezr6i8g1 .st-emotion-cache-1y48h6w a.active {
        background-color: var(--primary-color);
        color: white;
        font-weight: 600;
    }

    /* Metric cards */
    .st-emotion-cache-1r650o0 {
        background-color: var(--card-background);
        border-radius: 12px;
        box-shadow: 0 4px 15px var(--shadow-light);
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border-color);
        text-align: center;
    }
    .st-emotion-cache-1r650o0 label {
        color: var(--light-text-color);
        font-size: 0.9em;
        margin-bottom: 0.5rem;
    }
    .st-emotion-cache-1r650o0 div[data-testid="stMetricValue"] {
        font-size: 2.2em;
        font-weight: 700;
        color: var(--primary-color);
    }

    /* Chat messages */
    .chat-message {
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        max-width: 80%;
        word-wrap: break-word;
        box-shadow: 0 2px 5px var(--shadow-light);
    }
    .user-message {
        background-color: var(--primary-color);
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 5px;
    }
    .ai-message {
        background-color: var(--card-background);
        color: var(--text-color);
        align-self: flex-start;
        border: 1px solid var(--border-color);
        border-bottom-left-radius: 5px;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }

    /* Source citations */
    .citation {
        font-size: 0.8em;
        color: var(--light-text-color);
        margin-top: 5px;
        padding-left: 5px;
        border-left: 2px solid var(--secondary-color);
    }

    /* Icons in sidebar */
    .icon-class {
        margin-right: 10px;
        color: var(--primary-color);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Initialize backend managers
@st.cache_resource
def get_database_manager():
    return DatabaseManager()

@st.cache_resource
def get_pdf_processor():
    return PDFProcessor()

@st.cache_resource
def get_embedding_generator():
    return EmbeddingGenerator()

@st.cache_resource
def get_vector_store_manager():
    return VectorStoreManager()

@st.cache_resource
def get_rag_pipeline():
    return RAGPipeline()

@st.cache_resource
def get_summarizer():
    return Summarizer() # Initialize the Summarizer

db_manager = get_database_manager()
pdf_processor = get_pdf_processor()
embedding_generator = get_embedding_generator()
vector_store_manager = get_vector_store_manager()
rag_pipeline = get_rag_pipeline()
summarizer = get_summarizer() # Get the summarizer instance


# Header Section
st.markdown("""
<div style="
padding:15px;
border-radius:12px;
background:#0E1117;
margin-bottom:20px;
">
<h1 style="color:white;margin-bottom:0;">
🧠 IntelliDocs AI
</h1>
<p style="color:#A0AEC0;margin-top:5px;">
Intelligent Multi-PDF Conversational Knowledge Assistant
</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# Sidebar Navigation
with st.sidebar:

    st.markdown("""
    # 🧠 IntelliDocs AI
    ### Knowledge Assistant
    ---
    """)
    
    selected_page = st.radio(
        "",
        [
            "💬 AI Chat",
            "📂 Documents",
            "📄 Summaries",
            "🕒 History",
            "📊 Dashboard",
            "ℹ️ About"
        ]
    )

    page_mapping = {
        "💬 AI Chat": "Chat with PDFs",
        "📂 Documents": "Uploaded Documents",
        "📄 Summaries": "Document Summary",
        "🕒 History": "Chat History",
        "📊 Dashboard": "Dashboard",
        "ℹ️ About": "About Project"
    }

    st.session_state.current_page = page_mapping[selected_page]

# Main Content Area based on selected page
st.markdown("<br>", unsafe_allow_html=True)

# Function for Dashboard
def show_dashboard():

    st.title("📊 Dashboard")

    docs = db_manager.get_all_documents()

    total_docs = len(docs)

    total_pages = sum(
        doc.num_pages or 0
        for doc in docs
    )

    total_chats = 0

    if "session_id" in st.session_state:
        total_chats = len(
            db_manager.get_chat_history(
                st.session_state.session_id
            )
        )

    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric(
            "Documents",
            total_docs
        )

    with col2:
        st.metric(
            "Pages Indexed",
            total_pages
        )

    with col3:
        st.metric(
            "Questions Asked",
            total_chats
        )

    st.markdown("---")

    st.subheader("📂 Recent Documents")

    if docs:

        for doc in docs[-5:]:

            with st.container(border=True):

                st.markdown(
                    f"**{doc.filename}**"
                )

                st.caption(
                    f"Status: {doc.status}"
                )

    else:
        st.info(
            "No documents uploaded yet."
        )


def show_uploaded_documents(): # Renamed function
    st.title("📂 Document Library")

    st.caption(
    "Upload PDF files and build your searchable knowledge base."
    )

    uploaded_files = st.file_uploader(
        "Drag and drop PDF files here or click to browse",
        type=["pdf"],
        accept_multiple_files=True,
        help="Only PDF files are supported."
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "application/pdf":
                file_name = uploaded_file.name
                document_uuid = str(uuid.uuid4())
                temp_file_path = os.path.join("data", "uploaded_pdfs", f"{document_uuid}_{file_name}")

                # Save the file to a temporary location
                os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                progress_text = st.empty()
                progress_text.info(f"Processing '{file_name}'...")

                try:
                    # 1. Add document metadata to DB
                    new_doc = db_manager.add_document(
                        filename=file_name,
                        status='processing',
                        file_path=temp_file_path
                    )
                    document_id = new_doc.document_id

                    # 2. Extract text from PDF
                    extracted_data = pdf_processor.extract_text_from_pdf(temp_file_path)
                    # Count total pages
                    num_pages = len(extracted_data)
                    progress_text.success(f"Extracted text from {num_pages} pages of '{file_name}'.")

                    # 3. Generate embeddings
                    embeddings_with_metadata = embedding_generator.generate_embeddings_for_document_pages(
                        extracted_data, str(document_id) # Convert doc_id to string for metadata consistency
                    )
                    progress_text.success(f"Generated {len(embeddings_with_metadata)} embeddings for '{file_name}'.")

                    # 4. Add embeddings to vector store
                    vector_store_manager.add_embeddings(embeddings_with_metadata)
                    progress_text.success(f"Embeddings added to vector store for '{file_name}'.")

                    # 5. Add chunks to database for source citation and explicit lookup
                    for chunk_item in embeddings_with_metadata:
                        db_manager.add_chunk(
                            document_id=document_id,
                            text_content=chunk_item['content'],
                            page_number=chunk_item['page_number']
                        )
                    progress_text.success(f"Chunks saved to database for '{file_name}'.")

                    # 6. Update document status and number of pages in DB
                    db_manager.update_document_status(document_id, 'completed', num_pages=num_pages)
                    progress_text.success(f"Successfully processed and indexed '{file_name}'.")

                except Exception as e:
                    error_message = f"Error processing '{file_name}': {e}"
                    progress_text.error(error_message)
                    st.exception(e)
                    if 'document_id' in locals():
                        db_manager.update_document_status(document_id, 'failed')
                finally:
                    # Clean up temporary file (optional, depending on storage strategy)
                    # os.remove(temp_file_path)
                    st.rerun() # Rerun to update document list

            else:
                st.error(f"Skipping {uploaded_file.name}: Only PDF files are allowed.")

    st.markdown("### Your Uploaded Documents")

    documents = db_manager.get_all_documents()

    if not documents:
        st.info("No documents uploaded yet. Upload PDFs above to see them listed here.")
    else:
        # Display documents in a grid
        cols = st.columns(3) # Adjust number of columns as needed
        for i, doc in enumerate(documents):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{doc.filename}**")
                    st.write(f"Status: {doc.status}")
                    st.write(f"Uploaded: {doc.upload_date.strftime('%Y-%m-%d %H:%M')}")
                    if hasattr(doc, 'num_pages') and doc.num_pages is not None:
                        st.write(f"Pages: {doc.num_pages}")
                    else:
                         # Handle cases where num_pages might not be set or is None
                        st.write("Pages: N/A")

                    col_btns1, col_btns2 = st.columns(2)
                    with col_btns1:
                        if st.button("View Summary", key=f"summary_doc_{doc.document_id}"):
                            st.session_state.current_page = "Document Summary"
                            st.session_state.selected_document_id = doc.document_id # Store selected doc ID
                            st.rerun()
                    with col_btns2:
                        if st.button("Delete", key=f"delete_doc_{doc.document_id}"):
                            db_manager.delete_document(doc.document_id)
                            st.success(f"Document '{doc.filename}' deleted.")
                            st.rerun()

def show_chat_with_pdfs():
    st.title("💬 AI Document Chat")

    st.caption(
    "Ask questions about uploaded PDFs and receive AI-powered answers with citations."
    )

    col1, col2 = st.columns([8,1])

    with col2:
        if st.button("🗑 Clear Chat"):
            st.session_state.messages = []

            if "session_id" in st.session_state:
                db_manager.delete_chat_history_for_session(
                    st.session_state.session_id
                )

        st.rerun()
    
    # Initialize session state for chat history if not present
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        db_manager.create_user_session(st.session_state.session_id) # Create a new session in DB

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "citations" in message and message["citations"]:
                citation_str = ", ".join([f"(Doc: {c['document_id']}, Page: {c['page_number']})" for c in message["citations"]])
                st.markdown(f"<div class='citation'>Sources: {citation_str}</div>", unsafe_allow_html=True)

    # Chat input area
    if prompt := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Thinking..."):
            # Generate query embedding
            query_embedding = embedding_generator.generate_query_embedding(prompt)
            # Retrieve relevant chunks
            retrieved_chunks = vector_store_manager.search_similar(query_embedding)

            # Convert chat history for RAGPipeline (only last few turns)
            chat_history_for_rag = []
            for msg in st.session_state.messages[:-1]: # Exclude current prompt
                if msg["role"] == "user":
                    chat_history_for_rag.append({"question": msg["content"], "answer": ""})
                elif msg["role"] == "assistant":
                    # Assuming AI messages are direct answers or have 'answer' field
                    chat_history_for_rag[-1]["answer"] = msg["content"] # Update the last user entry with AI's answer

            # Generate AI answer
            response = rag_pipeline.generate_answer(prompt, retrieved_chunks, chat_history_for_rag)
            ai_answer = response.get('answer', 'Sorry, I could not generate an answer.')
            citations = response.get('citations', [])

            with st.chat_message("assistant"):
                st.markdown(ai_answer)
                if citations:
                    citation_str = ", ".join([f"(Doc: {c['document_id']}, Page: {c['page_number']})" for c in citations])
                    st.markdown(f"<div class='citation'>Sources: {citation_str}</div>", unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": ai_answer, "citations": citations})

            # Save to chat history in DB (linking to document if relevant, for now just session)
            # For simplicity, we'll link to the document of the first retrieved chunk if any
            linked_document_id = None
            if retrieved_chunks:
                linked_document_id = retrieved_chunks[0].get('document_id')

            db_manager.save_chat_entry(
                session_id=st.session_state.session_id,
                question=prompt,
                answer=ai_answer,
                citations=str(citations), # Store citations as string/JSON string
                document_id=linked_document_id
            )
            db_manager.update_session_activity(st.session_state.session_id)

def show_chat_history():
    st.subheader("Chat History")
    st.write("Review your past conversations with IntelliDocs AI.")

    # Initialize session ID if not present (should already be from chat page, but for direct access)
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        db_manager.create_user_session(st.session_state.session_id)

    search_query = st.text_input("Search chat history", key="chat_history_search_input", placeholder="Enter keywords to search...")

    # Fetch all chat history for the current session
    all_history = db_manager.get_chat_history(st.session_state.session_id)

    if not all_history:
        st.info("No chat history found for this session. Start a conversation in 'Chat with PDFs'!")
    else:
        # Filter history based on search query
        filtered_history = [entry for entry in all_history if search_query.lower() in entry.question.lower() or search_query.lower() in entry.answer.lower()]

        if not filtered_history:
            st.warning("No chat entries match your search query.")
        else:
            # Display chat history entries as cards
            for i, entry in enumerate(filtered_history):
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**Question:** {entry.question}")
                        st.markdown(f"**Answer Preview:** {entry.answer[:150]}...")
                        if entry.document_id:
                            doc = db_manager.get_document_by_id(entry.document_id)
                            doc_filename = doc.filename if doc else "Unknown Document"
                            st.markdown(f"_Related Document:_ {doc_filename}")
                        if entry.citations:
                            try:
                                # Citations are stored as stringified JSON
                                citation_list = json.loads(entry.citations)
                                if citation_list:
                                    citation_str = ", ".join([f"(Doc: {c['document_id']}, Page: {c['page_number']})" for c in citation_list])
                                    st.markdown(f"<div class='citation'>Sources: {citation_str}</div>", unsafe_allow_html=True)
                            except json.JSONDecodeError:
                                st.markdown(f"<div class='citation'>Sources: {entry.citations}</div>", unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"<small>{entry.timestamp.strftime('%Y-%m-%d %H:%M')}</small>", unsafe_allow_html=True)
                        if st.button("Delete", key=f"delete_chat_{entry.chat_id}"):
                            # Implement delete functionality for individual chat entries
                            db_manager.delete_chat_entry(entry.chat_id) # Assuming delete_chat_entry exists
                            st.success(f"Chat entry {entry.chat_id} deleted.")
                            st.rerun()

            st.markdown("--- Other Actions ---")
            if st.button("Clear All Chat History"):
                db_manager.delete_chat_history_for_session(st.session_state.session_id)
                st.success("All chat history cleared.")
                st.rerun()

def show_document_summary():
    st.title("📄 AI Document Summaries")

    st.caption(
    "Generate intelligent summaries, key points and concepts."
    )

    documents = db_manager.get_all_documents()

    if not documents:
        st.info("No documents uploaded yet. Please upload documents in the 'Uploaded Documents' page to enable summarization.")
        return

    # Determine selected document based on session state or new selection
    selected_document_id = st.session_state.get('selected_document_id', None)
    selected_filename = None

    document_options = {doc.filename: doc.document_id for doc in documents}

    if selected_document_id:
        # Find the filename for the pre-selected ID
        for filename, doc_id in document_options.items():
            if doc_id == selected_document_id:
                selected_filename = filename
                break
        # Set default index for selectbox
        initial_index = list(document_options.keys()).index(selected_filename) if selected_filename else 0
    else:
        initial_index = 0 # Default to first document if nothing pre-selected

    # Selectbox for documents
    selected_filename_from_box = st.selectbox(
        "Choose a document to summarize:",
        list(document_options.keys()),
        index=initial_index, # Pre-select if ID is present, otherwise first
        placeholder="Select a document...",
        key="summary_doc_selector"
    )

    if selected_filename_from_box:
        current_selected_document_id = document_options[selected_filename_from_box]
        # Update session state if user changes selection in the dropdown
        if current_selected_document_id != st.session_state.get('selected_document_id_from_box', None):
            st.session_state.selected_document_id_from_box = current_selected_document_id
            st.rerun()

        document_to_summarize_id = st.session_state.get('selected_document_id_from_box', current_selected_document_id)

        with st.spinner(f"Generating summary for '{selected_filename_from_box}'..."):
            try:
                # Retrieve all chunks for the selected document
                chunks = db_manager.get_chunks_by_document_id(document_to_summarize_id)
                full_text = " ".join([chunk.text_content for chunk in chunks])

                if not full_text.strip():
                    st.warning("Selected document has no extractable text for summarization.")
                    return

                # Generate summary
                generated_summary = summarizer.summarize_text(full_text)

                st.markdown(f"### Summary of {selected_filename_from_box}")
                with st.container(border=True):
                    st.write(generated_summary)

                # Placeholder for Key Points, Concepts, Keywords
                # These would typically be extracted/generated in a more advanced summarizer.
                with st.expander("Key Points (Placeholder)"):
                    st.write("Key point 1: Document emphasizes X.")
                    st.write("Key point 2: Major conclusion is Y.")
                with st.expander("Important Concepts (Placeholder)"):
                    st.write("Concept A, Concept B, Concept B")
                with st.expander("Keywords (Placeholder)"):
                    st.write("Keyword1, Keyword2, Keyword3")

            except Exception as e:
                st.error(f"Error generating summary for '{selected_filename_from_box}': {e}")
                st.exception(e)

def show_about_project():
    st.subheader("About IntelliDocs AI")
    st.write("Learn more about this project, its architecture, and the team behind it.")

    st.markdown("""
    IntelliDocs AI is an intelligent document interaction system designed to enhance how users engage with PDF documents.
    Leveraging Retrieval-Augmented Generation (RAG) principles, it allows users to:

    *   **Upload PDF documents**: Easily ingest multiple PDF files into the system.
    *   **Ask natural language questions**: Get AI-generated answers grounded in the content of the uploaded documents.
    *   **Receive source citations**: Answers are accompanied by references to the specific documents and page numbers from which the information was retrieved.
    *   **Review chat history**: Maintain and manage past conversations for continuity and record-keeping.
    *   **Generate document summaries**: Quickly grasp the essence of lengthy documents.

    ### Technology Stack
    *   **Frontend**: Streamlit
    *   **Backend & AI Orchestration**: Python
    *   **PDF Processing**: PyMuPDF (`fitz`)
    *   **Embedding Generation**: Sentence Transformers (`all-MiniLM-L6-v2`)
    *   **Vector Store**: FAISS
    *   **Large Language Model (LLM)**: Google Gemini
    *   **Database**: SQLite (SQLAlchemy ORM)

    ### Project Architecture
    The system follows a modular architecture, separating concerns into Frontend, Backend (API, AI Pipeline, Database), and Data storage layers. This design ensures scalability, maintainability, and ease of development.

    ### Developed by
    [Payal Jangale] - Google Colab Unified DSA Agent
    """)


# Conditional rendering of pages
if st.session_state.current_page == "Dashboard":
    show_dashboard()
elif st.session_state.current_page == "Chat with PDFs":
    show_chat_with_pdfs()
elif st.session_state.current_page == "Document Summary":
    show_document_summary()
elif st.session_state.current_page == "Chat History":
    show_chat_history()
elif st.session_state.current_page == "Uploaded Documents":
    show_uploaded_documents()
elif st.session_state.current_page == "About Project":
    show_about_project()
