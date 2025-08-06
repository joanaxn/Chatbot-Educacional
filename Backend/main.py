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
from fastapi import Body
import threading
from shutil import copyfile
import mysql.connector
from fastapi.responses import JSONResponse
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaLLM

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from datetime import datetime


from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
import glob



from langchain.prompts import PromptTemplate

from fastapi import APIRouter
from datetime import datetime



import os

from db_mysql import ligar_bd
from datetime import datetime



app = FastAPI()



# Caminhos
DOCENTES_PATH = "docentes.json"
ALUNOS_PATH = "alunos.json"
BASE_DIR = "C:/xampp/htdocs/materiais"
DATA_DIR = "data"

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/listar_ficheiros")
def listar_ficheiros(cadeira: str = Query(...)):
    cadeira = cadeira.strip()
    pasta = Path(os.path.join(BASE_DIR, cadeira))
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










#----------------EMBEDDINGS-------------------
def gerar_embeddings(cadeira):
    try:
        pasta_ficheiros = os.path.join("data", cadeira)
        pasta_db = os.path.join("db", cadeira)
        os.makedirs(pasta_db, exist_ok=True)

        documentos = []

        # Carregar todos os .pdf e .docx da cadeira
        ficheiros_pdf = glob.glob(os.path.join(pasta_ficheiros, "*.pdf"))
        ficheiros_docx = glob.glob(os.path.join(pasta_ficheiros, "*.docx"))

        for path in ficheiros_pdf:
            loader = PyPDFLoader(path)
            documentos.extend(loader.load())

        for path in ficheiros_docx:
            loader = Docx2txtLoader(path)
            documentos.extend(loader.load())

        if not documentos:
            print("⚠️ Nenhum documento encontrado para gerar embeddings.")
            return

        # Divide o texto
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        docs_divididos = splitter.split_documents(documentos)

        # Gerar e guardar embeddings em bd/{CADEIRA}
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        db = Chroma.from_documents(documents=docs_divididos, embedding=embeddings, persist_directory=pasta_db)
        db.persist()

        print(f"✅ Embeddings gerados com sucesso para a cadeira: {cadeira}")

    except Exception as e:
        print(f"❌ Erro ao gerar embeddings: {e}")

#-----------------------------------------------------









#mandar para a base de dados e para a pasta data/
@app.post("/confirmar_ficheiros")
def confirmar_ficheiros(dados: ConfirmacaoFicheiros):
    try:
        cadeira = dados.cadeira.strip()
        ficheiros = dados.ficheiros

        pasta_origem = os.path.join(BASE_DIR, cadeira)
        pasta_destino = os.path.join("data", cadeira)
        os.makedirs(pasta_destino, exist_ok=True)

        conn = ligar_bd()
        cursor = conn.cursor()

        novos_confirmados = []

        for ficheiro in ficheiros:
            cursor.execute("""
                SELECT COUNT(*) FROM ficheiros_confirmados
                WHERE nome = %s AND cadeira = %s
            """, (ficheiro, cadeira))
            ja_existe = cursor.fetchone()[0] > 0

            if not ja_existe:
                origem = os.path.join(pasta_origem, ficheiro)
                destino_fisico = os.path.join(pasta_destino, ficheiro)

                # Este é o caminho que o frontend pode abrir no browser
                caminho_web = f"http://localhost/materiais/{cadeira}/{ficheiro}"

                shutil.copyfile(origem, destino_fisico)

                cursor.execute("""
                    INSERT INTO ficheiros_confirmados (nome, cadeira, caminho)
                    VALUES (%s, %s, %s)
                """, (ficheiro, cadeira, caminho_web))

                novos_confirmados.append(ficheiro)

        conn.commit()
        cursor.close()
        conn.close()

        # ✅ GERAR EMBEDDINGS AUTOMATICAMENTE
        if novos_confirmados:
            gerar_embeddings(cadeira)

        if novos_confirmados:
            return {"mensagem": "novos", "ficheiros": novos_confirmados}
        else:
            return {"mensagem": "repetidos", "ficheiros": []}

    except Exception as e:
        print("❌ ERRO:", e)
        return JSONResponse(content={"erro": str(e)}, status_code=500)






#mandar para data/ e para a base de dados
@app.get("/ficheiros_confirmados")
def ficheiros_confirmados(cadeira: str = Query(...)):
    try:
        conn = ligar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, caminho FROM ficheiros_confirmados WHERE cadeira = %s", (cadeira.strip(),))
        resultados = cursor.fetchall()
        ficheiros = [{"nome": row[0], "caminho": row[1]} for row in resultados]
        cursor.close()
        conn.close()
        return {"ficheiros": ficheiros}
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)






#------------------ LOGIN -------------------
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
    
#------------------------------------------------------







#listar na dropdown as cadeiras que o docente leciona
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
    




#------------------ CHAT -------------------

@app.post("/perguntar")
def perguntar(pergunta: str = Body(...), cadeira: str = Body(...)):
    try:
        # Caminho dos embeddings da cadeira
        pasta_db = os.path.join("db", cadeira)

        # Verifica se existe base de embeddings
        if not os.path.exists(pasta_db):
            return {"resposta": "❌ Ainda não existem embeddings para esta cadeira."}

        # Carregar os embeddings
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        db = Chroma(persist_directory=pasta_db, embedding_function=embeddings)

        # Inicializar o modelo (gemma)
        modelo = OllamaLLM(model="gemma:2b-instruct")

        # Prompt com 'context' e 'question'
        prompt_template = """
Usa apenas a informação abaixo para responder à pergunta.
Responde em português de forma clara e objetiva.
Se não houver informação suficiente, responde com: "Não tenho informações suficientes para responder."

Informação dos documentos:
{context}

Pergunta: {question}
"""
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=prompt_template
        )

        # Construir cadeia de QA
        qa_chain = RetrievalQA.from_chain_type(
            llm=modelo,
            retriever=db.as_retriever(),
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )

        resultado = qa_chain.run(pergunta)
        return {"resposta": resultado}

    except Exception as e:
        print("❌ ERRO NO /perguntar:", e)
        return JSONResponse(content={"erro": str(e)}, status_code=500)