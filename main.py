from scripts.ingest import retrieve_documents, chunk_documents
from scripts.retriever import store_and_retrieve

if __name__ == "__main__":
    documents = retrieve_documents()
    chunked_documents = chunk_documents(documents)
    retriever = store_and_retrieve(chunked_documents)
    print(retriever)