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
            doc.metadata["source"] = f"./data/{file}"
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
            chunk_size=800,
            chunk_overlap=120,
            length_function=len,
        )
        chunked.extend(splitter.split_documents([doc]))

    return chunked

