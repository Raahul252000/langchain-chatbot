from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import GEMINI_API_KEY
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    # GOOGLE_API_KEY=GEMINI_API_KEY,
)