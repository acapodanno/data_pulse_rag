from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# Dense search
def build_vector_store(chunked_documents: list[Document]):
    vector_store = Chroma.from_documents(
        documents=chunked_documents, 
        embedding=OpenAIEmbeddings(
             model="text-embedding-3-large",
        ),
        persist_directory="./chroma_db",
        collection_name="data_pulse",
    )
    return vector_store

def get_retriever():
    vector_store = Chroma(
        persist_directory="./chroma_db",
        collection_name="data_pulse",
        embedding_function=OpenAIEmbeddings(
             model="text-embedding-3-large",
        ),
    )
    return vector_store.as_retriever(
        search_type="mmr", # Max Marginal Relevance
        search_kwargs={'k': 3, 'fetch_k': 10}
    )
