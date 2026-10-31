from langchain_google_genai import GoogleGenerativeAI

llm = GoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)