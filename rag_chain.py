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