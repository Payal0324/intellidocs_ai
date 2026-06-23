
import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# Define the base class for declarative models
Base = declarative_base()

# Document Model
class Document(Base):
    __tablename__ = 'documents'
    document_id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.now, nullable=False)
    status = Column(String, nullable=False) # e.g., 'pending', 'processing', 'completed', 'failed'
    file_path = Column(String, nullable=True) # Path to the stored PDF file
    num_pages = Column(Integer, nullable=True) # Number of pages in the document

    # Relationships
    chunks = relationship('Chunk', back_populates='document', cascade='all, delete-orphan')
    chat_entries = relationship('ChatHistory', back_populates='document')

    def __repr__(self):
        return f"<Document(document_id={self.document_id}, filename='{self.filename}', status='{self.status}')>"

# ChatHistory Model
class ChatHistory(Base):
    __tablename__ = 'chat_history'
    chat_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    document_id = Column(Integer, ForeignKey('documents.document_id'), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now, nullable=False)
    citations = Column(Text, nullable=True) # Storing citations as JSON string or comma-separated

    # Relationships
    document = relationship('Document', back_populates='chat_entries')
    user_session = relationship('UserSession', back_populates='chat_history_entries')

    def __repr__(self):
        return f"<ChatHistory(chat_id={self.chat_id}, session_id='{self.session_id}', question='{self.question[:30]}...')>"

# Chunk Model
class Chunk(Base):
    __tablename__ = 'chunks'
    chunk_id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.document_id'), nullable=False)
    page_number = Column(Integer, nullable=True)
    start_offset = Column(Integer, nullable=True)
    end_offset = Column(Integer, nullable=True)
    text_content = Column(Text, nullable=False)

    # Relationships
    document = relationship('Document', back_populates='chunks')

    def __repr__(self):
        return f"<Chunk(chunk_id={self.chunk_id}, document_id={self.document_id}, page_number={self.page_number})>"

# UserSession Model
class UserSession(Base):
    __tablename__ = 'user_sessions'
    session_id = Column(String, primary_key=True)
    start_time = Column(DateTime, default=datetime.datetime.now, nullable=False)
    last_active = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    user_id = Column(String, nullable=True) # Optional: For authenticated users

    # Relationships
    chat_history_entries = relationship('ChatHistory', backref='session', lazy=True)

    def __repr__(self):
        return f"<UserSession(session_id='{self.session_id}', last_active='{self.last_active}')>"


class DatabaseManager:
    def __init__(self, db_url: str = 'sqlite:///./data/intellidocs.db'):
        # Ensure the directory for the database exists
        db_dir = os.path.dirname(db_url.replace('sqlite:///./', ''))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine) # Create tables if they don't exist
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    # --- CRUD for Documents ---
    def add_document(self, filename: str, status: str = 'pending', file_path: str = None) -> Document:
        session = self.get_session()
        new_document = Document(filename=filename, status=status, file_path=file_path)
        session.add(new_document)
        session.commit()
        session.refresh(new_document)
        session.close()
        return new_document

    def get_document_by_id(self, document_id: int) -> Document:
        session = self.get_session()
        document = session.query(Document).filter_by(document_id=document_id).first()
        session.close()
        return document

    def get_all_documents(self) -> list[Document]:
        session = self.get_session()
        documents = session.query(Document).all()
        session.close()
        return documents

    def update_document_status(self, document_id: int, new_status: str, num_pages: int = None):
        session = self.get_session()
        document = session.query(Document).filter_by(document_id=document_id).first()
        if document:
            document.status = new_status
            if num_pages is not None:
                document.num_pages = num_pages
            session.commit()
            session.refresh(document)
        session.close()
        return document

    def delete_document(self, document_id: int):
        session = self.get_session()
        document = session.query(Document).filter_by(document_id=document_id).first()
        if document:
            session.delete(document)
            session.commit()
        session.close()

    # --- CRUD for Chat History ---
    def save_chat_entry(self, session_id: str, question: str, answer: str, citations: str = None, document_id: int = None) -> ChatHistory:
        session = self.get_session()
        new_chat_entry = ChatHistory(
            session_id=session_id,
            document_id=document_id,
            question=question,
            answer=answer,
            citations=citations
        )
        session.add(new_chat_entry)
        session.commit()
        session.refresh(new_chat_entry)
        session.close()
        return new_chat_entry

    def get_chat_history(self, session_id: str, limit: int = 100) -> list[ChatHistory]:
        session = self.get_session()
        history = session.query(ChatHistory).filter_by(session_id=session_id).order_by(ChatHistory.timestamp.asc()).limit(limit).all()
        session.close()
        return history

    def delete_chat_history_for_session(self, session_id: str):
        session = self.get_session()
        session.query(ChatHistory).filter_by(session_id=session_id).delete()
        session.commit()
        session.close()

    def delete_chat_entry(self, chat_id: int):
        session = self.get_session()
        chat_entry = session.query(ChatHistory).filter_by(chat_id=chat_id).first()
        if chat_entry:
            session.delete(chat_entry)
            session.commit()
        session.close()

    # --- CRUD for Chunks ---
    def add_chunk(self, document_id: int, text_content: str, page_number: int = None, start_offset: int = None, end_offset: int = None) -> Chunk:
        session = self.get_session()
        new_chunk = Chunk(
            document_id=document_id,
            page_number=page_number,
            start_offset=start_offset,
            end_offset=end_offset,
            text_content=text_content
        )
        session.add(new_chunk)
        session.commit()
        session.refresh(new_chunk)
        session.close()
        return new_chunk

    def get_chunks_by_document_id(self, document_id: int) -> list[Chunk]:
        session = self.get_session()
        chunks = session.query(Chunk).filter_by(document_id=document_id).all()
        session.close()
        return chunks

    # --- CRUD for User Sessions ---
    def create_user_session(self, session_id: str, user_id: str = None) -> UserSession:
        session = self.get_session()
        new_session = UserSession(session_id=session_id, user_id=user_id)
        session.add(new_session)
        session.commit()
        session.refresh(new_session)
        session.close()
        return new_session

    def get_user_session(self, session_id: str) -> UserSession:
        session = self.get_session()
        user_session = session.query(UserSession).filter_by(session_id=session_id).first()
        session.close()
        return user_session

    def update_session_activity(self, session_id: str):
        session = self.get_session()
        user_session = session.query(UserSession).filter_by(session_id=session_id).first()
        if user_session:
            user_session.last_active = datetime.datetime.now()
            session.commit()
            session.refresh(user_session)
        session.close()

    def delete_user_session(self, session_id: str):
        session = self.get_session()
        user_session = session.query(UserSession).filter_by(session_id=session_id).first()
        if user_session:
            session.delete(user_session)
            session.commit()
        session.close()
