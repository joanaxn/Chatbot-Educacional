from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaLLM
import os
import unicodedata
import re
import traceback

app = FastAPI()

# CORS para permitir pedidos da React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Normaliza nome da cadeira (remove acentos e espaços)
def normalizar_nome(nome):
    nome_sem_acentos = unicodedata.normalize('NFD', nome).encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'[^a-zA-Z0-9_-]', '_', nome_sem_acentos)

# Corta resposta na última frase
def corta_em_frase(texto):
    for p in [".", "!", "?"]:
        idx = texto.rfind(p)
        if idx != -1:
            return texto[:idx+1]
    return texto

# Modelos
embedding_function = OllamaEmbeddings(model="nomic-embed-text")  # ⚠️ precisa estar disponível no ollama
llm = OllamaLLM(model="gemma3")  # ⚠️ precisa estar disponível no ollama

# ======================
# 📥 ENDPOINT /upload
# ======================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), cadeira: str = Form(...)):
    try:
        pasta = normalizar_nome(cadeira)
        folder_path = Path(f"data/{pasta}")
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = folder_path / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())

        loader = PyPDFLoader(str(file_path))
        documentos = loader.load()

        chroma_db = Chroma.from_documents(
            documents=documentos,
            embedding=embedding_function,
            persist_directory=str(folder_path)
        )
        chroma_db.persist()

        return {"message": f"Ficheiro {file.filename} guardado e embeddings criados com sucesso!"}

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"erro": f"Erro inesperado: {str(e)}"})


# ========================
# 💬 ENDPOINT /perguntar
# ========================
@app.post("/perguntar")
async def perguntar(request: Request):
    try:
        data = await request.json()
        pergunta = data.get("pergunta")
        cadeira_raw = data.get("cadeira")

        if not pergunta or not cadeira_raw:
            return JSONResponse(status_code=400, content={"erro": "Pergunta ou cadeira em falta."})

        cadeira = normalizar_nome(cadeira_raw)
        path = f"data/{cadeira}"

        if not os.path.exists(path):
            return JSONResponse(status_code=404, content={"erro": "Não existem materiais para esta cadeira."})

        vectordb = Chroma(
            persist_directory=path,
            embedding_function=embedding_function
        )
        docs = vectordb.similarity_search(pergunta, k=1)

        if not docs:
            return {"resposta": "❌ Não encontrei informação suficiente nos materiais desta cadeira."}

        contexto = docs[0].page_content

        prompt = f"""
        Usa apenas os seguintes materiais da cadeira "{cadeira_raw}" para responder:
        \"\"\"{contexto}\"\"\"

        Se não conseguires responder com base neles, diz:
        'Não encontrei informação suficiente nos materiais para responder.'

        Pergunta: \"{pergunta}\"
        Resposta:
        """

        resposta = llm.invoke(prompt)
        return {"resposta": corta_em_frase(resposta)}

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"erro": f"Erro: {str(e)}"})
