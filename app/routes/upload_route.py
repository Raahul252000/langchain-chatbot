from fastapi import File, UploadFile, APIRouter
from app.services.file_service import upload_document, user_query
from app.schemas.chat_schema import UserQuery
router = APIRouter(prefix="/documents")
"""

                  DOCUMENT INGESTION PIPELINE IN Langchain

                            Client
                               │
                               ▼
                            Upload PDF
                               │
                               ▼
                            Save PDF
                               │
                               ▼
                            PyPDFLoader
                               │
                               ▼
                            Document Objects
                               │
                               ▼
                            RecursiveCharacterTextSplitter
                               │
                               ▼
                            Chunks (Document Objects)
                               │
                               ▼
                            GoogleGenerativeAIEmbeddings
                               │
                               ▼
                            ChromaDB
"""
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    result = await upload_document(file)
    return {"result": result}


"""
        User Query
              │
              ▼
        Retriever
              │
              ▼
        Relevant Documents
              │
              ▼
        Context String
              │
              ▼
        ChatPromptTemplate
              │
              ▼
        ChatGoogleGenerativeAI
              │
              ▼
        Final Answer
"""
@router.post("/chat")
async def chat(request: UserQuery):
    response = await user_query(request.query)
    return {
        "result": response
    }