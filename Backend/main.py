from fastapi import FastAPI, Body, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import os
import json
import shutil
import threading
from pathlib import Path
from typing import List, Optional

import mysql.connector

# LangChain
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

from pydantic import BaseModel
from db_mysql import ligar_bd
import zipfile


#  CONFIGURAÇÃO
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MATERIAIS_DIR = "materiais"
DATA_DIR = "data"
DB_DIR = "db"

CADEIRAS_VALIDAS = ["IA", "Redes"]


def is_valid_pdf(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(5) == b"%PDF-"
    except:
        return False


def is_valid_docx(path: str) -> bool:
    try:
        return zipfile.is_zipfile(path)
    except:
        return False



#  EMBEDDINGS
def gerar_embeddings_para_ficheiros(cadeira: str, ficheiros: list):
    try:
        pasta_origem = os.path.join(DATA_DIR, cadeira)
        pasta_db = os.path.join(DB_DIR, cadeira)
        os.makedirs(pasta_db, exist_ok=True)

        documentos = []

        for nome in ficheiros:
            caminho = os.path.join(pasta_origem, nome)
            ext = os.path.splitext(nome)[1].lower()

            if ext == ".pdf":
                if not is_valid_pdf(caminho):
                    print(f"[WARN] PDF inválido: {nome}")
                    continue
                loader = PyPDFLoader(caminho)

            elif ext == ".docx":
                if not is_valid_docx(caminho):
                    print(f"[WARN] DOCX inválido: {nome}")
                    continue
                loader = Docx2txtLoader(caminho)

            else:
                continue

            try:
                documentos.extend(loader.load())
            except:
                print(f"[ERRO] Falhou ao carregar {nome}")

        if not documentos:
            print("[INFO] Nenhum documento válido para embeddings.")
            return

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = splitter.split_documents(documentos)

        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        db = Chroma(persist_directory=pasta_db, embedding_function=embeddings)
        db.add_documents(chunks)
        db.persist()

        print(f"[OK] Embeddings atualizados para {cadeira}")

    except Exception as e:
        print("ERRO AO GERAR EMBEDDINGS:", e)



#  Listar Ficheiros (sem Infinity)
@app.get("/listar_ficheiros_remotos")
def listar_ficheiros_remotos(cadeira: str = Query(...)):
    cadeira = cadeira.strip()

    if cadeira not in CADEIRAS_VALIDAS:
        return {"cadeira": cadeira, "ficheiros": []}

    pasta = os.path.join(MATERIAIS_DIR, cadeira)

    if not os.path.isdir(pasta):
        return {"cadeira": cadeira, "ficheiros": []}

    ficheiros = [f for f in os.listdir(pasta) if f.lower().endswith((".pdf", ".docx"))]
    ficheiros.sort()

    return {"cadeira": cadeira, "ficheiros": ficheiros}


#  Confirmar Ficheiros
class ConfirmacaoFicheiros(BaseModel):
    cadeira: str
    ficheiros: list


@app.post("/confirmar_ficheiros")
def confirmar_ficheiros(dados: ConfirmacaoFicheiros):

    cadeira = dados.cadeira.strip()
    ficheiros = dados.ficheiros

    if cadeira not in CADEIRAS_VALIDAS:
        return JSONResponse({"erro": "Cadeira inválida."}, 400)

    pasta_origem = os.path.join(MATERIAIS_DIR, cadeira)
    pasta_destino = os.path.join(DATA_DIR, cadeira)

    os.makedirs(pasta_destino, exist_ok=True)

    conn = ligar_bd()
    cursor = conn.cursor()

    novos, repetidos, falhados = [], [], []

    for nome in ficheiros:

        caminho_origem = os.path.join(pasta_origem, nome)
        caminho_destino = os.path.join(pasta_destino, nome)

        # Vê se existe na bd
        cursor.execute(
            "SELECT COUNT(*) FROM ficheiros_confirmados WHERE nome=%s AND cadeira=%s",
            (nome, cadeira),
        )
        if cursor.fetchone()[0] > 0:
            repetidos.append(nome)
            continue

    
        try:
            shutil.copy2(caminho_origem, caminho_destino)
        except:
            falhados.append(nome)
            continue

        # Inserir BD
        try:
            cursor.execute(
                "INSERT INTO ficheiros_confirmados (nome, cadeira, caminho) VALUES (%s, %s, %s)",
                (nome, cadeira, caminho_destino),
            )
            novos.append(nome)
        except:
            falhados.append(nome)

    conn.commit()
    cursor.close()
    conn.close()

    # Gerar embeddings em background
    if novos:
        threading.Thread(
            target=gerar_embeddings_para_ficheiros,
            args=(cadeira, novos),
            daemon=True,
        ).start()

    return {
        "mensagem": "ok",
        "novos": novos,
        "repetidos": repetidos,
        "falhados": falhados,
    }



# Login
class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login_docente")
def login_docente(dados: LoginRequest):

    conn = ligar_bd()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT nome, email, cadeiras FROM docentes WHERE email=%s AND password=%s",
        (dados.email, dados.password),
    )
    docente = cursor.fetchone()

    conn.close()

    if docente:
        return docente
    return JSONResponse({"erro": "Credenciais inválidas."}, 401)


@app.post("/login_estudante")
def login_estudante(dados: LoginRequest):

    conn = ligar_bd()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT nome, email FROM alunos WHERE email=%s AND password=%s",
        (dados.email, dados.password),
    )
    aluno = cursor.fetchone()

    if aluno:
        cursor.execute(
            "SELECT cadeira FROM inscricoes WHERE email=%s",
            (aluno["email"],)
        )
        aluno["cadeiras"] = [row["cadeira"] for row in cursor.fetchall()]
        conn.close()
        return aluno

    conn.close()
    return JSONResponse({"erro": "Credenciais inválidas."}, 401)



#  Listar Cadeiras Docente
@app.get("/listar_cadeiras_docente")
def listar_cadeiras_docente(email: str):

    conn = ligar_bd()
    cursor = conn.cursor()

    cursor.execute("SELECT cadeira FROM leciona WHERE email=%s", (email,))
    rows = cursor.fetchall()

    conn.close()

    return {"cadeiras": [r[0] for r in rows]}


# Ficheiros Confirmados
@app.get("/ficheiros_confirmados")
def ficheiros_confirmados(cadeira: str = Query(...)):

    conn = ligar_bd()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT nome, caminho FROM ficheiros_confirmados WHERE cadeira=%s ORDER BY nome ASC",
        (cadeira,),
    )
    rows = cursor.fetchall()

    conn.close()

    return {
        "cadeira": cadeira,
        "ficheiros": rows,
    }


# Chatbot
@app.post("/perguntar")
def perguntar(pergunta: str = Body(...), cadeira: str = Body(...), email: str = Body(...)):

    # Validar inscrição
    conn = ligar_bd()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM inscricoes WHERE email=%s AND cadeira=%s",
        (email, cadeira),
    )
    inscrito = cursor.fetchone()
    conn.close()

    if not inscrito:
        return JSONResponse({"erro": "Não estás inscrito nesta cadeira."}, 403)

    # Verificar embeddings
    pasta_db = os.path.join(DB_DIR, cadeira)
    if not os.path.isdir(pasta_db) or not os.listdir(pasta_db):
        return {"resposta": "Ainda não existem embeddings para esta cadeira."}

    # RAG
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(persist_directory=pasta_db, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 4})

    llm = Ollama(model="gemma:2b-instruct")

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
Usa apenas o contexto abaixo para responder.
Se não existir informação suficiente, responde:
"Não tenho informações suficientes para responder."

Contexto:
{context}

Pergunta: {question}
Resposta:
"""
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt}
    )

    resposta = chain.run(pergunta)

    if not resposta.strip():
        resposta = "Não tenho informações suficientes para responder."

    return {"resposta": resposta}
