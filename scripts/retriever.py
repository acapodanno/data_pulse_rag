from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from dotenv import load_dotenv

load_dotenv()

def build_vector_store(chunked_documents: list[Document]):
    # Cancella la collection esistente per evitare accumulo di dati stantii/duplicati
    import chromadb
    client = chromadb.PersistentClient(path="./chroma_db")
    try:
        client.delete_collection("data_pulse")
    except Exception:
        pass  # collection non esisteva, va bene

    vector_store = Chroma.from_documents(
        documents=chunked_documents,
        embedding=OpenAIEmbeddings(
            model="text-embedding-3-large",
        ),
        persist_directory="./chroma_db",
        collection_name="data_pulse",
    )
    return vector_store

def get_dense_retriever():
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

# sparse retriever
def get_sparse_retriever(chunked_documents: list[Document]):
    return BM25Retriever.from_documents(chunked_documents)

# 30% sparse + 70% dense
def get_hybrid_retriever(chunked_documents: list[Document]):
    bm25_retriever = get_sparse_retriever(chunked_documents)
    bm25_retriever.k = 3
    dense_retriever = get_dense_retriever()
    return EnsembleRetriever(
        retrievers=[bm25_retriever, dense_retriever],
        weights=[0.3, 0.7],
    )