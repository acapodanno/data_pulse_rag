from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os 

def retrieve_documents() -> list[Document]:
    files = os.listdir("./data")
    documents = []
    for file in files:
        loader = UnstructuredMarkdownLoader(file_path=f"./data/{file}",mode="single")
        documents.extend(loader.load())
    return documents


def chunk_documents(documents: list[Document]) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n# ", "\n## ", "\n### ", "\n\n", "\n", " ", ""],
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        
    )
    return text_splitter.split_documents(documents)

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
    return vector_store.as_retriever(
        search_type="mmr", # Max Marginal Relevance
        search_kwargs={'k': 3, 'fetch_k': 10}
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
    documents = retrieve_documents()
    chunked_documents = chunk_documents(documents)
    retriever = store_and_retrieve(chunked_documents)
    rag_chain = setup_chain(retriever)
    print("Data Pulse Assistant é pronto! (Scrivi 'esci', 'exit' o premi Ctrl+C per terminare)")
    while True:
        question = input("\nFai una domanda: ")
        if question.lower() in ['esci', 'exit']:
            print("Arrivederci!")
            break
        answer = rag_chain.invoke({"input": question})
        print("Answer:", answer["answer"])