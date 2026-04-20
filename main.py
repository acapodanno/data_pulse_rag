from scripts.ingest import retrieve_documents, chunk_documents
from scripts.retriever import store_and_retrieve
from scripts.rag_chain import setup_chain

if __name__ == "__main__":
    documents = retrieve_documents()
    chunked_documents = chunk_documents(documents)
    retriever = store_and_retrieve(chunked_documents)
    rag_chain = setup_chain(retriever)
    question = "Come posso richiedere un permesso di lavoro da remoto?"
    answer = rag_chain.invoke({"input": question})
    print("Answer:", answer["answer"])