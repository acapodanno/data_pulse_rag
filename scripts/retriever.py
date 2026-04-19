from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

def store_and_retrieve(chunked_documents: list[Document]):
    vector_store = Chroma.from_documents(
        documents=chunked_documents, 
        embedding=OpenAIEmbeddings(
             model="text-embedding-3-large",
        ),
        persist_directory="./chroma_db",
        collection_name="data_pulse",
    )
    return vector_store.as_retriever()
