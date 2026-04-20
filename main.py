from scripts.ingest import retrieve_documents, chunk_documents
from scripts.retriever import build_vector_store, get_hybrid_retriever
from scripts.rag_chain import setup_chain

if __name__ == "__main__":
    documents = retrieve_documents()
    chunked_documents = chunk_documents(documents)
    build_vector_store(chunked_documents)
    rag_chain = setup_chain(get_hybrid_retriever(chunked_documents))
    question = "Come posso richiedere un permesso di lavoro da remoto?"
    answer = rag_chain.invoke({"input": question})
    print("Answer:", answer["answer"])
    for doc in answer["context"]:
        print(f"  📄 {doc.metadata.get('source')}")