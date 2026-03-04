import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

class RAGEngine:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )

    def process_file(self, file_path):
        """Processes a file and adds it to the vector store."""
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)
        
        docs = loader.load()
        chunks = self.text_splitter.split_documents(docs)
        
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vector_store.add_documents(chunks)
        
        return len(chunks)

    def query(self, text, k=3):
        """Retrieves relevant context for a query."""
        if self.vector_store is None:
            return ""
        
        docs = self.vector_store.similarity_search(text, k=k)
        return "\n\n".join([doc.page_content for doc in docs])

    def clear(self):
        """Clears the vector store."""
        self.vector_store = None
