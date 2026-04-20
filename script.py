from langchain_community.document_loaders import UnstructuredMarkdownLoader, UnstructuredPDFLoader, UnstructuredWordDocumentLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os 
LOADER_MAP = {
    ".md": lambda path: UnstructuredMarkdownLoader(file_path=path, mode="single"),
    ".pdf": lambda path: UnstructuredPDFLoader(file_path=path),
    ".docx": lambda path: UnstructuredWordDocumentLoader(file_path=path),
    ".txt": lambda path: UnstructuredFileLoader(file_path=path),
}
def retrieve_documents() -> list[Document]:
    files = os.listdir("./data")
    documents = []
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        loader_factory = LOADER_MAP.get(ext)
        if loader_factory is None:
            print(f"Formato {file} non supportato!")
            continue
        loader = loader_factory(path=f"./data/{file}")
        docs = loader.load()
        for doc in docs:
            doc.metadata["file_type"] = ext.lstrip(".")
            doc.metadata["source"] = file
        documents.extend(docs)
    return documents

SEPARATORS_MAP = {
    "md":   ["\n# ", "\n## ", "\n### ", "\n\n", "\n", " ", ""],
    "pdf":  ["\n\n", "\n", ". ", " ", ""],
    "docx": ["\n\n", "\n", ". ", " ", ""],
    "txt":  ["\n\n", "\n", " ", ""],
}

def chunk_documents(documents: list[Document]) -> list[Document]:
    chunked = []

    for doc in documents:
        file_type = doc.metadata.get("file_type", "txt")
        separators = SEPARATORS_MAP.get(file_type, ["\n\n", "\n", " ", ""])

        splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunked.extend(splitter.split_documents([doc]))

    return chunked

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
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

def get_dense_retriever():
    """Dense retriever: ricerca semantica su ChromaDB (MMR)."""
    vector_store = Chroma(
        persist_directory="./chroma_db",
        collection_name="data_pulse",
        embedding_function=OpenAIEmbeddings(
             model="text-embedding-3-large",
        ),
    )
    return vector_store.as_retriever(
        search_type="mmr",  # Max Marginal Relevance
        search_kwargs={"k": 3, "fetch_k": 10}
    )

def get_hybrid_retriever(chunked_documents: list[Document]):
    """Hybrid retriever: BM25 (sparse) + ChromaDB MMR (dense) via EnsembleRetriever."""
    # BM25 — ricerca keyword esatta, in-memory, nessun costo API
    bm25_retriever = BM25Retriever.from_documents(chunked_documents)
    bm25_retriever.k = 3

    # Dense — ricerca semantica su ChromaDB
    dense_retriever = get_dense_retriever()

    # Ensemble con pesi uguali (50% BM25, 50% dense) e Reciprocal Rank Fusion
    return EnsembleRetriever(
        retrievers=[bm25_retriever, dense_retriever],
        weights=[0.5, 0.5],
    )

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
import os

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
system_prompt = (
    "Sei l'assistente virtuale di DataPulse S.p.A. Rispondi alle domande dei dipendenti "
    "utilizzando esclusivamente il contesto fornito. Se non conosci la risposta, "
    "dichiara che l'informazione non è presente nei manuali aziendali.\n\n"
    "REGOLE:\n"
    "1. Cita sempre il nome del documento sorgente.\n"
    "2. Fornisci un livello di confidenza (Alto/Medio/Basso) basato sulla pertinenza del contesto.\n"
    "3. Elenca le date di validità se presenti nei metadati.\n\n"
    "CONTESTO:\n{context}"
)

def setup_chain(retriever):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    combine_documents_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    # Creazione della catena di retrieval completa
    # Questa catena restituisce un dizionario con: 'input', 'context', 'answer'
    retrieval_chain = create_retrieval_chain(retriever, combine_documents_chain)
    return retrieval_chain

if __name__ == "__main__":
    # BM25 è in-memory: i chunk servono sempre
    documents = retrieve_documents()
    chunked_documents = chunk_documents(documents)

    # ChromaDB: indicizza solo se non esiste già
    if not os.path.exists("./chroma_db"):
        print("[INIT] Nessun DB trovato, avvio indicizzazione dense...")
        build_vector_store(chunked_documents)
    else:
        print("[INIT] DB ChromaDB esistente trovato, skip indicizzazione.")

    # Hybrid retriever: BM25 + dense
    retriever = get_hybrid_retriever(chunked_documents)
    rag_chain = setup_chain(retriever)

    print("\nData Pulse Assistant è pronto! (Scrivi 'esci' o 'exit' per terminare)")
    while True:
        question = input("\nFai una domanda: ").strip()
        if not question:
            continue
        if question.lower() in ["esci", "exit"]:
            print("Arrivederci!")
            break
        answer = rag_chain.invoke({"input": question})
        print(f"\nRisposta: {answer['answer']}")
        print("\n📚 Sorgenti:")
        seen = set()
        for doc in answer["context"]:
            src = doc.metadata.get("source", "sconosciuta")
            ftype = doc.metadata.get("file_type", "").upper()
            label = f"  📄 {src} [{ftype}]"
            if label not in seen:
                print(label)
                seen.add(label)
        print()