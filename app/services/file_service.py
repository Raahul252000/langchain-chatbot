from pathlib import Path
from uuid import uuid4
from fastapi import File, UploadFile, HTTPException, status
from langchain_community.document_loaders import PyMuPDFLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from app.core.chroma import vector_store


BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

async def upload_document(file):

    # Phase 1 Start: File upload start
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Only pdf files are allowed")

    filename = f"{str(uuid4())}_{file.filename}"
    file_path = UPLOAD_FOLDER / filename
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Unable to upload file - {str(e)}")

    finally:
        await file.close()
    # Phase 1 End: File uploaded

    # Phase 2 Start: Read file saved file and create documents
    loader = PyMuPDFLoader(str(file_path))
    documents = loader.load()
    # Phase 2 End: Documents created.

    # Phase 3 Start: Create chunks using the splitter (every chunk is one document )
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120
    )
    chunks = splitter.split_documents(documents=documents)
    # Phase 3 End: Chunks are created from the documents

    # Phase 4 Start: Initialize embedding model
    vector_store.add_documents(documents=chunks)
    print("counts: ", vector_store._collection.count())
    # print("get vector: ", vector_store._collection.get())

    return {
        "filename": filename,
        "file": file_path,
        "status_code": status.HTTP_200_OK,
        "mimetype": file.content_type,
        "size": file.size,
        "metadata": chunks[0].metadata,
        "total_pages": len(documents),
        "total_chunks": len(chunks),
    }

#-----------------------------------------------------------------------------------------------------------------------
RAG_PROMPT = ChatPromptTemplate.from_template(
    """
        You are a helpful AI assistant.
        
        Answer the user's question ONLY using the provided context.
        
        If the answer is not available in the context, say:
        
        "I couldn't find this information in the uploaded documents."
        
        Context:
        {context}
        
        Question:
        {question}
        
        Answer:
    """
)
async def user_query(user_query: str):
    from app.core.llm import llm
    if user_query is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User query is empty")

    # 1. create retriever and fetch k number of documents
    retriever = vector_store.as_retriever(
        search_kwargs = {
            "k": 5
        }
    )

    # 2. Invoke retriever to return matched documents
    documents = retriever.invoke(user_query)
    print("length of retrieved documents: ", len(documents))

    # print("Chunks retrieved relevant to user's query: ",documents)
    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    # 3. Invoke prompt and embed values in prompt
    prompt = RAG_PROMPT.invoke(
        {
            "context": context,
            "question": user_query,
        }
    )

    # 4. Invoke LLM with the Prompt and get the result.
    response = llm.invoke(prompt)

    # 5. return the result
    return {
        "user_query": user_query,
        "answer": response
    }
