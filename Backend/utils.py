from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from pathlib import Path

DB_DIR = Path("db")


#tipos de ficheiros 
def extrair_texto(file_path):
    ext = Path(file_path).suffix
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".pptx":
        loader = UnstructuredPowerPointLoader(file_path)
    else:
        raise ValueError("Formato não suportado.")
    return loader.load()

def preparar_embeddings(docs, cadeira_id):
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs_split = splitter.split_documents(docs)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    persist_dir = DB_DIR / cadeira_id

    Chroma.from_documents(docs_split, embeddings, persist_directory=str(persist_dir))
    print(f"✅ Embeddings criados e guardados para {cadeira_id}")
