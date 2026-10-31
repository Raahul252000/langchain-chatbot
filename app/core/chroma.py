from langchain_chroma import Chroma
from app.core.embeddings import embeddings

vector_store = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)