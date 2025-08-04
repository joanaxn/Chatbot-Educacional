from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from fastapi import Query
from typing import List
from pathlib import Path
from pydantic import BaseModel
import json
import threading
from fastapi import Body
import time
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
import os



app = FastAPI()

client = TestClient(app)

DATA_DIR = "data"
DB_DIR = "db"


DOCENTES_PATH = "docentes.json"
ALUNOS_PATH = "alunos.json"

# Permitir chamadas do frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Troca para o IP/domínio do frontend no futuro
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretório onde vamos guardar os ficheiros
BASE_DIR = "C:/xampp/htdocs/materiais"


@app.post("/receber_ficheiro")
async def receber_ficheiro(file: UploadFile, cadeira: str = Form(...)):
    try:
        # Criar pasta da cadeira se não existir
        pasta_cadeira = os.path.join(BASE_DIR, cadeira)
        os.makedirs(pasta_cadeira, exist_ok=True)

        # Caminho do ficheiro no servidor
        caminho_ficheiro = os.path.join(pasta_cadeira, file.filename)

        # Guardar ficheiro
        with open(caminho_ficheiro, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"mensagem": f"Ficheiro '{file.filename}' guardado com sucesso em '{cadeira}'."}
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)




@app.get("/listar_ficheiros")
def listar_ficheiros(cadeira: str = Query(...)):
    cadeira = cadeira.strip()  # REMOVE espaços e \n

    pasta = Path(f"{BASE_DIR}/{cadeira}")


    if not pasta.exists() or not pasta.is_dir():
        return {"ficheiros": []}

    ficheiros = [f.name for f in pasta.iterdir() if f.is_file()]
    return {"ficheiros": ficheiros}






@app.get("/listar_cadeiras")
def listar_cadeiras():
    try:
        diretorio = Path("C:/xampp/htdocs/materiais")
        if not diretorio.exists():
            return {"cadeiras": []}

        pastas = [f.name for f in diretorio.iterdir() if f.is_dir()]
        return {"cadeiras": pastas}
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)


class ConfirmacaoFicheiros(BaseModel):
    cadeira: str
    ficheiros: list

CONFIRMADOS_PATH = "confirmados.json"











#----------------EMBEDDINGS-----------------------
@app.post("/gerar_embeddings")
def gerar_embeddings(cadeira: str = Body(..., embed=True)):
    try:
        pasta_cadeira = os.path.join(DATA_DIR, cadeira)
        if not os.path.exists(pasta_cadeira):
            raise HTTPException(status_code=404, detail="Pasta da cadeira não encontrada.")

        docs = []
        for filename in os.listdir(pasta_cadeira):
            path = os.path.join(pasta_cadeira, filename)

            if filename.endswith(".pdf"):
                loader = PyMuPDFLoader(path)
            elif filename.endswith(".docx"):
                loader = Docx2txtLoader(path)
            elif filename.endswith(".pptx"):
                loader = UnstructuredPowerPointLoader(path)
            else:
                continue  # Ignora formatos desconhecidos

            docs.extend(loader.load())

        if not docs:
            raise HTTPException(status_code=400, detail="Nenhum documento válido encontrado.")

        # Divide o texto em pedaços
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        # Cria embeddings
        embeddings = OllamaEmbeddings(model="nomic-embed-text")

        # Cria pasta se não existir
        db_path = os.path.join(DB_DIR, cadeira)
        os.makedirs(db_path, exist_ok=True)

        # Guarda os embeddings
        Chroma.from_documents(chunks, embeddings, persist_directory=db_path)

        return {"mensagem": f"Embeddings gerados para a cadeira '{cadeira}' com sucesso."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







#para não travar a resposta do servidor, gera os embeddings em background
def gerar_embeddings_background(cadeira):
    try:
        client.post("http://localhost:8000/gerar_embeddings", json={"cadeira": cadeira})
    except Exception as e:
        print(f"⚠️ Erro ao gerar embeddings: {e}")


#mudado 3.08
@app.post("/confirmar_ficheiros")
def confirmar_ficheiros(data: dict = Body(...)):
    cadeira = data.get("cadeira", "").strip()
    ficheiros = data.get("ficheiros")

    if not cadeira or not ficheiros:
        return {"mensagem": "erro", "detalhe": "Cadeira ou ficheiros em falta"}

    confirmados_path = "confirmados.json"

    if os.path.exists(confirmados_path):
        with open(confirmados_path, "r", encoding="utf-8") as f:
            confirmados = json.load(f)
    else:
        confirmados = {}

    confirmados_da_cadeira = set(confirmados.get(cadeira, []))
    novos = [f for f in ficheiros if f not in confirmados_da_cadeira]

    if novos:
        confirmados_da_cadeira.update(novos)
        confirmados[cadeira] = list(confirmados_da_cadeira)

        with open(confirmados_path, "w", encoding="utf-8") as f:
            json.dump(confirmados, f, indent=2, ensure_ascii=False)

        for ficheiro in novos:
            origem = f"C:/xampp/htdocs/materiais/{cadeira}/{ficheiro}"
            destino = f"data/{cadeira}/{ficheiro}"
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            if not os.path.exists(destino):
                shutil.copy(origem, destino)

        # ✅ Gera embeddings em background
        threading.Thread(target=gerar_embeddings_background, args=(cadeira,)).start()

        return {"mensagem": "novos"}  # devolve logo!

    else:
        return {"mensagem": "repetidos"}










@app.get("/ficheiros_confirmados")
def ficheiros_confirmados(cadeira: str = Query(...)):
    try:
        if os.path.exists(CONFIRMADOS_PATH):
            with open(CONFIRMADOS_PATH, "r") as f:
                confirmados = json.load(f)
            return {"ficheiros": confirmados.get(cadeira.strip(), [])}
        return {"ficheiros": []}
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)






@app.post("/login_docente")
def login_docente(email: str = Body(...), password: str = Body(...)):
    try:
        if os.path.exists(DOCENTES_PATH):
            with open(DOCENTES_PATH, "r") as f:
                docentes = json.load(f)
        else:
            return JSONResponse(content={"erro": "Ficheiro de docentes não encontrado."}, status_code=500)

        for docente in docentes:
            if docente["email"] == email and docente["password"] == password:
                return {
                    "nome": docente["nome"],
                    "email": docente["email"],
                    "cadeiras": docente["cadeiras"]
                }

        return JSONResponse(content={"erro": "Credenciais inválidas."}, status_code=401)

    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
    






@app.post("/login_estudante")
def login_estudante(email: str = Body(...), password: str = Body(...)):
    try:
        if os.path.exists(ALUNOS_PATH):
            with open(ALUNOS_PATH, "r") as f:
                alunos = json.load(f)
        else:
            return JSONResponse(content={"erro": "Ficheiro de alunos não encontrado."}, status_code=500)

        for aluno in alunos:
            if aluno["email"] == email and aluno["password"] == password:
                return {
                    "nome": aluno["nome"],
                    "email": aluno["email"],
                    "cadeiras": aluno["cadeiras"]
                }

        return JSONResponse(content={"erro": "Credenciais inválidas."}, status_code=401)

    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
    












@app.get("/listar_cadeiras_docente")
def listar_cadeiras_docente(email: str = Query(...)):
    try:
        if os.path.exists(DOCENTES_PATH):
            with open(DOCENTES_PATH, "r") as f:
                docentes = json.load(f)
        else:
            return JSONResponse(content={"erro": "Ficheiro de docentes não encontrado."}, status_code=500)

        # Encontrar o docente pelo email
        docente = next((d for d in docentes if d["email"] == email), None)
        if not docente:
            return JSONResponse(content={"erro": "Docente não encontrado."}, status_code=404)

        # Ir buscar todas as pastas do XAMPP (todas as cadeiras existentes)
        diretorio = Path("C:/xampp/htdocs/materiais")
        if not diretorio.exists():
            return {"cadeiras": []}

        todas_cadeiras = [f.name for f in diretorio.iterdir() if f.is_dir()]

        # Filtrar apenas as que o docente leciona
        cadeiras_docente = [c for c in todas_cadeiras if c in docente["cadeiras"]]

        return {"cadeiras": cadeiras_docente}

    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500) 
    















#--------------------perguntar------------------------
@app.post("/perguntar")
def perguntar(pergunta: str = Query(...), cadeira: str = Query(...)):
    try:
        db_path = os.path.join("db", cadeira)
        if not os.path.exists(db_path):
            return JSONResponse(content={"erro": f"Não existem embeddings para a cadeira {cadeira}"}, status_code=404)

        # Carregar os embeddings e a base de dados
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        db = Chroma(persist_directory=db_path, embedding_function=embeddings)
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

        # Modelo local
        llm = Ollama(model="gemma:2b-instruct")

        # PROMPT reforçado que impede o modelo de inventar
        prompt_pt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
Usa apenas o contexto fornecido abaixo para responder à pergunta.
Se não encontrares a resposta no contexto, responde: "Não tenho informação para isso."
Nunca inventes. Responde sempre em português.

Contexto:
{context}

Pergunta: {question}
Resposta:
""".strip()
        )

        # Construção do QA chain
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt_pt}
        )

        resposta = qa.run(pergunta)

        # Validação da resposta
        if not resposta.strip() or "não tenho informação" in resposta.lower():
            return {"resposta": "Não tenho informação para isso."}

        return {"resposta": resposta}

    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
