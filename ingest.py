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
