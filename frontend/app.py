
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
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a modern, premium UI/UX
st.markdown("""
<style>

/* =========================
   GLOBAL THEME (ChatGPT-like)
========================= */

.main {
    background-color: #0B0F19;
    color: #E5E7EB;
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* =========================
   SIDEBAR
========================= */

section[data-testid="stSidebar"] {
    background-color: #0F172A;
    border-right: 1px solid #1F2937;
}

section[data-testid="stSidebar"] * {
    color: #E5E7EB;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton button {
    background-color: transparent;
    border: 1px solid #334155;
    border-radius: 10px;
    color: #E5E7EB;
    padding: 10px;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background-color: #1E293B;
}

/* =========================
   HEADINGS
========================= */

h1, h2, h3 {
    color: #F9FAFB;
    font-weight: 600;
}

/* =========================
   BUTTONS
========================= */

.stButton button {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 16px;
    font-weight: 600;
    transition: 0.2s ease-in-out;
}

.stButton button:hover {
    background-color: #1D4ED8;
    transform: translateY(-1px);
}

/* =========================
   CHAT INPUT
========================= */

.stChatInputContainer {
    border-radius: 12px;
}

/* Chat bubbles */
.stChatMessage {
    border-radius: 12px;
}

/* =========================
   METRICS CARDS
========================= */

[data-testid="metric-container"] {
    background-color: #111827;
    border: 1px solid #1F2937;
    padding: 16px;
    border-radius: 14px;
}

[data-testid="metric-container"] label {
    color: #9CA3AF;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #60A5FA;
}

/* =========================
   FILE UPLOADER
========================= */

[data-testid="stFileUploader"] {
    border: 2px dashed #3B82F6;
    border-radius: 14px;
    padding: 20px;
    background-color: #0F172A;
}

/* =========================
   CARDS / CONTAINERS
========================= */

div[data-testid="stVerticalBlock"] > div:has(div.stContainer) {
    background-color: #0F172A;
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 16px;
}

/* =========================
   SUCCESS / INFO BOXES
========================= */

.stSuccess, .stInfo, .stWarning {
    border-radius: 10px;
}

/* =========================
   SCROLLBAR (Modern)
========================= */

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #475569;
}

/* Dashboard spacing */
.block-container{
    padding-top:1.5rem;
    padding-bottom:2rem;
}

/* Remove horizontal line spacing */
hr{
    margin:0.3rem 0 1rem 0;
}

/* Buttons full width */
.stButton > button{
    width:100%;
    height:50px;
    font-size:15px;
}

/* Better metric hover */
[data-testid="metric-container"]{
    transition:0.2s ease;
}

[data-testid="metric-container"]:hover{
    transform:translateY(-3px);
    border:1px solid #3B82F6;
}

/* =========================
   BIGGER DASHBOARD METRICS
========================= */

[data-testid="metric-container"] {
    padding: 24px 20px !important;
    border-radius: 16px;
}

/* Metric label (📄 Documents etc.) */
[data-testid="metric-container"] label {
    font-size: 18px !important;
    font-weight: 600;
}

/* Metric value (1, 9, 0) */
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 34px !important;
    font-weight: 700;
}

/* Metric delta/help text */
[data-testid="metric-container"] [data-testid="stMetricDelta"],
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 13px !important;
    color: #9CA3AF;
}

</style>
""", unsafe_allow_html=True)

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

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# Sidebar Navigation
with st.sidebar:

    # App Title
    st.markdown("## 🧠 IntelliDocs AI")
    st.caption("RAG-powered Document Intelligence")

    st.markdown("---")

    # Navigation Title
    st.markdown("### Navigation")

    # Custom navigation buttons (ChatGPT style)
    if st.button("🏠 Dashboard", use_container_width=True):
        st.session_state.current_page = "Dashboard"

    if st.button("💬 Chat with PDFs", use_container_width=True):
        st.session_state.current_page = "Chat with PDFs"

    if st.button("📝 Document Summary", use_container_width=True):
        st.session_state.current_page = "Document Summary"

    if st.button("🕒 Chat History", use_container_width=True):
        st.session_state.current_page = "Chat History"

    if st.button("📂 Uploaded Documents", use_container_width=True):
        st.session_state.current_page = "Uploaded Documents"

    st.markdown("---")

    # Quick Info Section (mini dashboard feel)
    st.markdown("### 📊 Quick Stats")

    try:
        db = db_manager.get_all_documents()
        st.metric("Total Documents", len(db))
    except:
        st.metric("Total Documents", "0")

    st.markdown("---")

    # About Section
    st.markdown("### ℹ️ About")
    st.caption("Upload PDFs → Ask Questions → Get AI Answers with Citations")

# Function for Dashboard
def show_dashboard():

    st.title("🧠 IntelliDocs AI")

    st.caption("AI-powered document intelligence platform for chatting, summarizing and managing PDF documents.")

    st.markdown("---")
    
    # =========================
    # REAL METRICS (DYNAMIC)
    # =========================
    col1, col2, col3 = st.columns(3)

    try:
        documents = db_manager.get_all_documents()
        total_docs = len(documents)
    except:
        total_docs = 0

    try:
        total_pages = sum([doc.num_pages or 0 for doc in documents])
    except:
        total_pages = 0

    try:
        chats = db_manager.get_chat_history(st.session_state.get("session_id", "default"))
        total_chats = len(chats)
    except:
        total_chats = 0

    with col1:
        st.metric(
            label="📄 Documents",
            value=total_docs,
            help="Uploaded PDF files"
        )

    with col2:
        st.metric(
            label="📑 Pages",
            value=total_pages,
            help="Total processed pages"
        )

    with col3:
        st.metric(
            label="💬 Chats",
            value=total_chats,
            help="Saved conversations"
        )

    st.markdown("---")
    
    # =========================
    # QUICK ACTIONS (CLEAN UI)
    # =========================
    st.subheader("⚡Quick Actions")
    st.caption("Choose what you'd like to do.")

    colA, colB, colC = st.columns(3, gap="large")

    with colA:
        if st.button("📤 Upload Documents", use_container_width=True):
            st.session_state.current_page = "Uploaded Documents"
            st.rerun()

    with colB:
        if st.button("💬 Start Chat", use_container_width=True):
            st.session_state.current_page = "Chat with PDFs"
            st.rerun()

    with colC:
        if st.button("📂 Manage Documents", use_container_width=True):
            st.session_state.current_page = "Uploaded Documents"
            st.rerun()

    st.markdown("---")

    # =========================
    # ACTIVITY SNAPSHOT (NEW IDEA)
    # =========================
    st.subheader("Recent Documents")

    if documents:
        for doc in documents[:5]:
            st.markdown(
                f"📄 **{doc.filename}**  \n"
                f"<span style='color:#94A3B8;'>Pages: {doc.num_pages}</span>",
                unsafe_allow_html=True
            )
    else:
        st.info("No documents uploaded yet.")

def show_uploaded_documents():
    st.markdown("## 📂 Document Library")
    st.caption("Upload, manage, and view all your documents in one place")

    # ---------------- UPLOAD SECTION ----------------
    with st.container():
        st.markdown("### ⬆️ Upload Documents")

        uploaded_files = st.file_uploader(
            "Drop your PDFs here",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

        documents = db_manager.get_all_documents()
        existing_files = {doc.filename for doc in documents}
    
        processed_any = False
        if uploaded_files:
            for uploaded_file in uploaded_files:

                file_name = uploaded_file.name

                if file_name in existing_files:
                    st.warning(f"{file_name} already exists. Skipping.")
                    continue

                document_uuid = str(uuid.uuid4())
                temp_file_path = os.path.join(
                    "data", "uploaded_pdfs",
                    f"{document_uuid}_{file_name}"
                )

                os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                progress = st.progress(0)
                status_text = st.empty()

                try:
                    status_text.info(f"Processing {file_name}...")

                    new_doc = db_manager.add_document(
                        filename=file_name,
                        status='processing',
                        file_path=temp_file_path
                    )
                    document_id = new_doc.document_id

                    progress.progress(20)

                    extracted_data = pdf_processor.extract_text_from_pdf(temp_file_path)
                    num_pages = len(extracted_data)

                    progress.progress(40)

                    embeddings = embedding_generator.generate_embeddings_for_document_pages(
                        extracted_data, str(document_id)
                    )

                    progress.progress(60)

                    vector_store_manager.add_embeddings(embeddings)

                    for chunk in embeddings:
                        db_manager.add_chunk(
                            document_id=document_id,
                            text_content=chunk['content'],
                            page_number=chunk['page_number']
                        )

                    progress.progress(80)

                    db_manager.update_document_status(
                        document_id,
                        'completed',
                        num_pages=num_pages
                    )

                    progress.progress(100)

                    status_text.success(f"✅ {file_name} processed successfully!")
                    processed_any = True

                except Exception as e:
                    status_text.error(f"❌ Error: {file_name}")
                    db_manager.update_document_status(document_id, 'failed')
                    st.exception(e)

        if processed_any:
            st.rerun()

    st.divider()

    # ---------------- DOCUMENT LIST ----------------
    st.markdown("### 📄 Your Documents")

    if not documents:
        st.info("No documents uploaded yet.")
        return

    # Cards UI (ChatGPT style)
    for doc in documents:
        with st.container():
            st.markdown(
                f"""
                <div style="
                    padding:15px;
                    border-radius:12px;
                    border:1px solid #e0e0e0;
                    margin-bottom:10px;
                    background:white;
                ">
                    <h4 style="margin-bottom:5px;">📄 {doc.filename}</h4>
                    <p style="margin:0; color:gray;">
                        Status: <b>{doc.status}</b> |
                        Pages: {doc.num_pages if doc.num_pages else "N/A"} |
                        Uploaded: {doc.upload_date.strftime('%Y-%m-%d %H:%M')}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns([1,1,4])

            with col1:
                if st.button("📑 Summary", key=f"sum_{doc.document_id}"):
                    st.session_state.selected_document_id = doc.document_id
                    st.session_state.current_page = "Document Summary"
                    st.rerun()

            with col2:
                if st.button("🗑️ Delete", key=f"del_{doc.document_id}"):
                    db_manager.delete_document(doc.document_id)
                    st.rerun()
                    
def show_chat_history():
    st.markdown("## 💬 Chat History")
    st.caption("Review and manage all your past conversations.")

    # Ensure session exists
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        db_manager.create_user_session(st.session_state.session_id)

    # Search bar (clean)
    search_query = st.text_input(
        "",
        placeholder="🔍 Search questions or answers...",
        key="chat_history_search_input"
    )

    all_history = db_manager.get_chat_history(st.session_state.session_id)

    if not all_history:
        st.info("No chat history found. Start chatting with your PDFs first.")
        return

    # Filter
    filtered_history = [
        entry for entry in all_history
        if search_query.lower() in entry.question.lower()
        or search_query.lower() in entry.answer.lower()
    ] if search_query else all_history

    if not filtered_history:
        st.warning("No results found for your search.")
        return

    # Top actions bar
    colA, colB = st.columns([3, 1])

    with colB:
        if st.button("🗑️ Clear All History", use_container_width=True):
            db_manager.delete_chat_history_for_session(st.session_state.session_id)
            st.success("Chat history cleared.")
            st.rerun()

    st.markdown("---")

    # CHAT STYLE DISPLAY
    st.markdown("### 💬 Conversation History")

    for entry in reversed(filtered_history):

        with st.container():
                
            # TOP CARD (CHAT MESSAGE)
            with st.container(border=True):

            # Header row (timestamp + delete button)
                col1, col2 = st.columns([6, 1])

                with col1:
                    st.caption(f"🕒 {entry.timestamp.strftime('%Y-%m-%d %H:%M')}")

                with col2:
                    if st.button("🗑️", key=f"del_{entry.chat_id}"):
                        db_manager.delete_chat_entry(entry.chat_id)
                        st.rerun()

                st.markdown("")

                # USER MESSAGE
                st.markdown("#### 🧑 You")
                st.write(entry.question)

                st.markdown("---")

                # AI RESPONSE
                st.markdown("#### 🤖 Assistant")
                st.write(entry.answer)

                # CITATIONS (if any)
                if entry.citations:
                    try:
                        citation_list = json.loads(entry.citations)

                        if citation_list:
                            st.markdown("**📚 Sources:**")

                            for c in citation_list:
                                st.caption(
                                    f"📄 Document {c['document_id']} | Page {c['page_number']}"
                                )

                    except:
                        pass

def show_document_summary():
    st.markdown("## 📝 Document Intelligence Center")
    st.caption("Select a document and generate AI-powered structured insights")

    documents = db_manager.get_all_documents()

    if not documents:
        st.info("No documents available. Upload PDFs first.")
        return

    # ---------------- DOCUMENT SELECTOR (ChatGPT STYLE) ----------------
    document_map = {doc.filename: doc.document_id for doc in documents}

    st.markdown("### 📄 Select Document")

    selected_filename = st.selectbox(
        "",
        list(document_map.keys()),
        key="summary_selector",
        label_visibility="collapsed"
    )

    selected_doc_id = document_map[selected_filename]

    st.divider()

    # ---------------- FETCH CONTENT ----------------
    with st.spinner("Analyzing document..."):
        chunks = db_manager.get_chunks_by_document_id(selected_doc_id)
        full_text = " ".join([c.text_content for c in chunks])

    if not full_text.strip():
        st.warning("This document has no readable text.")
        return

    # ---------------- AI SUMMARY ----------------
    
    if "summary_cache" not in st.session_state:
            st.session_state.summary_cache = {}
    try:
        if selected_doc_id not in st.session_state.summary_cache:
            st.session_state.summary_cache[selected_doc_id] = summarizer.summarize_text(full_text)

        summary = st.session_state.summary_cache[selected_doc_id]
        
    except Exception as e:
        st.error("Failed to generate summary")
        st.exception(e)
        return

    # ---------------- MAIN LAYOUT (CHATGPT STYLE SPLIT VIEW) ----------------
    col1, col2 = st.columns([2, 1])

    # LEFT SIDE → MAIN SUMMARY
    with col1:
        st.markdown("### 🧠 AI Summary")

        st.markdown(
            f"""
            <div style="
                background:white;
                padding:20px;
                border-radius:12px;
                border:1px solid #e6e6e6;
                line-height:1.6;
                font-size:15px;
            ">
                {summary}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 📌 Key Insights")

        with st.expander("🟦 Important Points"):
            st.write("• Extracted insights will appear here (can be upgraded later)")
            st.write("• You can connect LLM-based key point extraction")

        with st.expander("🟩 Concepts Detected"):
            st.write("• Concept extraction can be enabled via summarizer upgrade")

        with st.expander("🟨 Keywords"):
            st.write("• Keyword extraction placeholder")

    # RIGHT SIDE → DOCUMENT INFO PANEL
    with col2:
        st.markdown("### 📊 Document Info")

        doc = db_manager.get_document_by_id(selected_doc_id)

        st.markdown(
            f"""
            <div style="
                background:#f9f9f9;
                padding:15px;
                border-radius:10px;
                border:1px solid #ddd;
            ">
                <p><b>Filename:</b> {doc.filename}</p>
                <p><b>Status:</b> {doc.status}</p>
                <p><b>Pages:</b> {doc.num_pages if doc.num_pages else "N/A"}</p>
                <p><b>Uploaded:</b> {doc.upload_date.strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### ⚡ Actions")

        if st.button("💬 Ask Questions About This Doc"):
            st.session_state.current_page = "Chat with PDFs"
            st.rerun()

        if st.button("📄 Re-generate Summary"):
            if "summary_cache" in st.session_state:
                st.session_state.summary_cache.pop(selected_doc_id, None)
            st.rerun()

        if st.button("🗑️ Delete Document"):
            db_manager.delete_document(selected_doc_id)
            st.success("Deleted successfully")
            st.session_state.current_page = "Uploaded Documents"
            st.rerun()
            
def show_settings():
    st.markdown("## ⚙️ Settings")
    st.caption("Manage your IntelliDocs experience")

    # ---------------- ACCOUNT / SESSION INFO ----------------
    st.markdown("### 👤 Session Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style="
                padding:15px;
                border-radius:12px;
                border:1px solid #e6e6e6;
                background:white;
            ">
                <b>Session ID</b><br>
                <span style="color:gray;">Active user session for chat tracking</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="
                padding:15px;
                border-radius:12px;
                border:1px solid #e6e6e6;
                background:white;
            ">
                <b>System Mode</b><br>
                <span style="color:gray;">RAG + Gemini AI Enabled</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # ---------------- CHAT SETTINGS (REAL ONLY) ----------------
    st.markdown("### 💬 Chat Settings")

    col1, col2 = st.columns(2)

    with col1:
        chat_mode = st.selectbox(
            "Response Style",
            ["Balanced", "Precise", "Detailed"],
            index=0
        )

    with col2:
        memory_mode = st.selectbox(
            "Conversation Memory",
            ["Session Only", "Persistent (DB)"],
            index=0
        )

    st.divider()

    # ---------------- DATA MANAGEMENT ----------------
    st.markdown("### 🗂️ Data Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧹 Clear Chat History"):
            if "session_id" in st.session_state:
                db_manager.delete_chat_history_for_session(st.session_state.session_id)
                st.success("Chat history cleared")

    with col2:
        if st.button("🗑️ Reset All Documents"):
            docs = db_manager.get_all_documents()
            for doc in docs:
                db_manager.delete_document(doc.document_id)
            st.success("All documents deleted")

    st.divider()

    # ---------------- ABOUT SYSTEM ----------------
    st.markdown("### ℹ️ System Info")

    st.markdown(
        """
        <div style="
            padding:15px;
            border-radius:12px;
            border:1px solid #e6e6e6;
            background:white;
            line-height:1.6;
        ">
        <b>IntelliDocs AI</b><br><br>

        • RAG-based PDF Question Answering System<br>
        • Powered by Google Gemini<br>
        • Vector search using FAISS<br>
        • Built with Streamlit<br><br>

        <b>Version:</b> 1.0.0 (MVP)<br>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_about_project():
    st.markdown("## ℹ️ About IntelliDocs AI")
    st.caption("A modern AI-powered document intelligence system")

    # ---------------- HERO SECTION ----------------
    st.markdown(
        """
        <div style="
            padding:20px;
            border-radius:14px;
            border:1px solid #e6e6e6;
            background:white;
            line-height:1.6;
        ">
        <b>IntelliDocs AI</b> is a Retrieval-Augmented Generation (RAG) system that lets you
        chat with PDFs, extract insights, and generate AI-powered summaries with source grounding.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ---------------- CORE FEATURES ----------------
    st.markdown("### 🚀 Core Capabilities")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **📄 Document Intelligence**
        - Upload and process PDFs
        - Extract structured text
        - Store embeddings for semantic search
        """)

        st.markdown("""
        **💬 AI Chat**
        - Ask questions in natural language
        - Context-aware responses
        - Source-backed answers
        """)

    with col2:
        st.markdown("""
        **🧠 Smart Summarization**
        - Auto-generated document summaries
        - Key insights extraction (upgradable)
        - Fast document understanding
        """)

        st.markdown("""
        **🔎 Retrieval System**
        - Vector similarity search (FAISS)
        - Embedding-based ranking
        - Accurate context retrieval
        """)

    st.divider()

    # ---------------- TECHNOLOGY STACK ----------------
    st.markdown("### 🧱 Tech Stack")

    st.markdown(
        """
        <div style="
            padding:15px;
            border-radius:12px;
            border:1px solid #e6e6e6;
            background:white;
        ">
        <b>Frontend:</b> Streamlit<br>
        <b>AI Model:</b> Google Gemini<br>
        <b>Embeddings:</b> Sentence Transformers<br>
        <b>Vector DB:</b> FAISS<br>
        <b>Database:</b> SQLite (SQLAlchemy)<br>
        <b>PDF Processing:</b> PyMuPDF
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ---------------- SYSTEM DESIGN ----------------
    st.markdown("### 🏗️ System Design")

    st.markdown(
        """
        <div style="
            padding:15px;
            border-radius:12px;
            border:1px solid #e6e6e6;
            background:white;
            line-height:1.6;
        ">
        <b>Architecture:</b> Modular RAG Pipeline<br><br>

        1. PDF Upload → Text Extraction  
        2. Chunking → Embedding Generation  
        3. Vector Storage (FAISS)  
        4. Semantic Retrieval  
        5. Gemini LLM Response Generation  
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ---------------- FOOTER ----------------
    st.markdown(
        """
        <div style="text-align:center; color:gray; padding:10px;">
            Built with Streamlit • Powered by Gemini AI • RAG Architecture
        </div>
        """,
        unsafe_allow_html=True
    )

def show_chat_with_pdfs():
    st.markdown("## 💬 Chat with your Documents")
    st.caption("Ask questions from your PDFs. Answers are generated using RAG + citations.")

    # ----------------------------
    # SESSION INIT
    # ----------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        db_manager.create_user_session(st.session_state.session_id)

    # ----------------------------
    # CLEAR CHAT BUTTON (FIXED)
    # ----------------------------
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    # ----------------------------
    # CHAT HISTORY DISPLAY
    # ----------------------------
    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.messages:
            role = msg["role"]

            with st.chat_message(role):
                st.markdown(msg["content"])

                if role == "assistant" and msg.get("citations"):
                    st.caption("📚 Sources:")
                    for c in msg["citations"]:
                        st.write(f"Doc {c['document_id']} • Page {c['page_number']}")

    # ----------------------------
    # CHAT INPUT (CHATGPT STYLE)
    # ----------------------------
    user_query = st.chat_input("Ask anything from your PDFs...")

    if user_query:
        # show user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_query
        })

        with st.chat_message("user"):
            st.markdown(user_query)

        # ----------------------------
        # AI RESPONSE GENERATION
        # ----------------------------
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                query_embedding = embedding_generator.generate_query_embedding(user_query)
                retrieved_chunks = vector_store_manager.search_similar(query_embedding)

                chat_history_for_rag = [
                    {"question": m["content"], "answer": ""}
                    for m in st.session_state.messages[-6:]
                    if m["role"] == "user"
                ]

                response = rag_pipeline.generate_answer(
                    user_query,
                    retrieved_chunks,
                    chat_history_for_rag
                )

                answer = response.get("answer", "No response generated.")
                citations = response.get("citations", [])

                st.markdown(answer)

                if citations:
                    st.caption("📚 Sources")
                    for c in citations:
                        st.write(f"Doc {c['document_id']} • Page {c['page_number']}")

        # save assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "citations": citations
        })

        # DB save
        linked_doc = None
        if retrieved_chunks:
            linked_doc = retrieved_chunks[0].get("document_id")

        db_manager.save_chat_entry(
            session_id=st.session_state.session_id,
            question=user_query,
            answer=answer,
            citations=str(citations),
            document_id=linked_doc
        )

        db_manager.update_session_activity(st.session_state.session_id)


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
elif st.session_state.current_page == "Settings":
    show_settings()
elif st.session_state.current_page == "About Project":
    show_about_project()
