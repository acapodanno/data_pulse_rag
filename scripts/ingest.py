from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
import os 

def retrieve_documents() -> list[Document]:
    files = os.listdir("../data")
    documents = []
    for file in files:
        loader = UnstructuredMarkdownLoader(file_path=f"../data/{file}",mode="elements")
        documents.extend(loader.load())
    return documents


def chunk_documents(documents: list[Document]) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["#", "##", "###"],
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    return text_splitter.split_documents(documents)

def embed_documents(documents: list[Document]) -> list[Document]:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
    )
    return embeddings.embed_documents(documents)

if __name__ == "__main__":
    documents = retrieve_documents()
    chunked_documents = chunk_documents(documents)
    embedded_documents = embed_documents(chunked_documents)
    print(embedded_documents)