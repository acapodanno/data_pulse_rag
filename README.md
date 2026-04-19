# 🧬 DataPulse S.p.A. - Sistema RAG Professionale

Questo documento descrive l'architettura tecnica e la struttura del sistema **Retrieval-Augmented Generation (RAG)** progettato per DataPulse S.p.A. L'obiettivo è passare da una ricerca testuale tradizionale a una pipeline di **Knowledge Management** avanzata che garantisca precisione, tracciabilità e affidabilità enterprise.

---

## 1. Architettura del Sistema
Il sistema è modulare, permettendo la sostituzione dei componenti (modelli di embedding, database vettoriali o LLM) senza riscrivere la logica core.

### A. Modulo di Ingestion & Processing
La fase di preparazione è critica per gestire documenti eterogenei (email, manuali, policy):
*   **Document Loading**: Utilizzo di `LangChain` per il caricamento di file PDF, Markdown e TXT.
*   **Chunking Strategico**: Utilizzo di `RecursiveCharacterTextSplitter` con un **overlap del 10-15%** (circa 120 caratteri su chunk di 800) per mantenere la coerenza del contesto tecnico.
*   **Arricchimento Metadati**: Ogni chunk include: `source_file`, `last_updated`, `compliance_tag`, `version`.

### B. Indicizzazione e Retrieval Ibrido
*   **Vector Store**: Utilizzo di **ChromaDB** per la persistenza locale e lo sviluppo rapido.
*   **Dense Retrieval**: Ricerca semantica basata su vettori per cogliere il significato (es. "accesso dati").
* ** Sparse Retrieval**: Ricerca basata su parole chiave per cogliere il significato (es. "accesso dati").
*   **Metadata Filtering**: Capacità di restringere la ricerca per stato documento o data di validità.

---

## 2. Pipeline di Generazione (LLM)
Il sistema utilizza un prompt strutturato per minimizzare le allucinazioni:

> **Istruzioni di Sistema:**
> "Sei un assistente esperto di DataPulse S.p.A. Rispondi utilizzando ESCLUSIVAMENTE il contesto fornito. Se l'informazione non è presente, dichiara di non saperlo."

### Regole di Risposta:
1.  **Attribuzione**: Indicazione obbligatoria della fonte (es. [Manuale Privacy, pag 4]).
2.  **Confidenza Self-Check**: Valutazione della risposta da 1 a 5 basata sulla chiarezza del contesto.
3.  **Audit Temporale**: Indicazione della data di validità dei documenti citati.

---

## 3. Implementazione Tecnica

| Modulo | Tecnologie Utilizzate | Scopo |
| :--- | :--- | :--- |
| **Orchestrazione** | `LangChain` | Gestione del flusso dati e catene LCEL. |
| **Embeddings** | `text-embeddings-3-small` | Trasformazione del testo in vettori semantici. |
| **Vector DB** | `ChromaDB` | Database vettoriale e storage dei metadati. |
| **LLM Interface** | `GPT-4o-mini` | Generazione della risposta finale con ragionamento. |

---

## 4. Gestione Tracciabilità e Confidenza
Per i requisiti di compliance di DataPulse:
*   **Calcolo Confidenza**: Basato sulla similarità coseno del Vector DB combinata con il self-check dell'LLM.
*   **Timestamp**: Estrazione automatica del metadato `last_modified` per garantire che l'utente non consulti policy obsolete.

---

## 5. Come Utilizzare il Progetto

### Setup iniziale
1. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
2. Configura le variabili d'ambiente nel file `.env` (usa `.env.example` come base).

### Esecuzione
1. **Ingestion**: Carica e vettorizza i documenti nella cartella `data/`:
   ```bash
   python -m scripts.ingest
   ```
2. **Chat**: Avvia l'interfaccia di interrogazione:
   ```bash
   python main.py
   ```

---

*Documentazione tecnica redatta per il team IT di DataPulse S.p.A.*
