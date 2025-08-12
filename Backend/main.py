from fastapi import FastAPI, Body, Query, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Stdlib
import os
import glob
import shutil
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Optional



import zipfile




# DB / Network
import mysql.connector
import requests
from ftplib import FTP, error_perm

# LangChain (usar sempre a versão community)
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Projeto
from pydantic import BaseModel
from db_mysql import ligar_bd

import json
from urllib.parse import quote

# --- slug igual ao PHP (preg_replace sem 'u'): cada byte fora de A-Za-z0-9_- vira "_"
def cadeira_slug_php_like(nome: str) -> str:
    s = (nome or '').strip()
    b = s.encode('utf-8', 'ignore')  # bytes como o PHP vê
    out = []
    for ch in b:  # ch é um byte (0..255)
        if (48 <= ch <= 57) or (65 <= ch <= 90) or (97 <= ch <= 122) or ch in (95, 45):  # 0-9 A-Z a-z _ -
            out.append(chr(ch))
        else:
            out.append('_')
    return ''.join(out)




app = FastAPI()


REMOTE_BASE_URL = "https://chatbotestagio.page.gd"
print("🔍 REMOTE_BASE_URL =", REMOTE_BASE_URL)


# mete isto por variáveis de ambiente ou direto enquanto testas
FTP_HOST = os.getenv("FTP_HOST", "ftpupload.net")          # InfinityFree
FTP_USER = os.getenv("FTP_USER", "if0_39670755")      # ex.: if0_39670755
FTP_PASS = os.getenv("FTP_PASS", "Estagio2004")      # a do painel

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

#-----------------
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
    

#-----------------






#-------------EMBEDDINGS----------------
def gerar_embeddings_para_ficheiros(cadeira: str, ficheiros: list):
    """
    Lê APENAS os ficheiros dados em data/{cadeira}/{ficheiro} (.pdf/.docx),
    valida, cria chunks e adiciona os embeddings na base Chroma em db/{cadeira}.
    """
    try:
        pasta_ficheiros = os.path.join("data", cadeira)
        pasta_db = os.path.join("db", cadeira)
        os.makedirs(pasta_db, exist_ok=True)

        documentos = []
        for nome in ficheiros:
            caminho = os.path.join(pasta_ficheiros, nome)
            if not os.path.isfile(caminho):
                print(f"⚠️ Não encontrado para embeddings: {caminho}")
                continue

            ext = os.path.splitext(nome)[1].lower()

            # valida conteúdo antes de carregar
            if ext == ".pdf" and not is_valid_pdf(caminho):
                print(f"⚠️ PDF inválido (skip): {nome}")
                continue
            if ext == ".docx" and not is_valid_docx(caminho):
                print(f"⚠️ DOCX inválido (skip): {nome}")
                continue

            try:
                if ext == ".pdf":
                    loader = PyPDFLoader(caminho)
                elif ext == ".docx":
                    loader = Docx2txtLoader(caminho)
                else:
                    print(f"ℹ️ Extensão não suportada (skip): {nome}")
                    continue
                documentos.extend(loader.load())
            except Exception as e:
                print(f"⚠️ Erro a ler {nome} p/ embeddings: {e}")

        if not documentos:
            print("ℹ️ Sem documentos válidos para gerar embeddings (nesta chamada).")
            return

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=120)
        docs_divididos = splitter.split_documents(documentos)

        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        db = Chroma(persist_directory=pasta_db, embedding_function=embeddings)
        db.add_documents(docs_divididos)  # adiciona aos existentes
        db.persist()

        print(f"✅ Embeddings atualizados em db/{cadeira} (chunks: {len(docs_divididos)})")
    except Exception as e:
        print(f"❌ Erro ao gerar embeddings p/ {cadeira}: {e}")










@app.get("/listar_ficheiros_remotos")
def listar_ficheiros_remotos(cadeira: str = Query(...)):
    cadeira = (cadeira or '').strip()
    if not cadeira:
        return {"cadeira": "", "ficheiros": []}

    slug = cadeira_slug_php_like(cadeira)                      # <--- AQUI
    base = f"/htdocs/materiais/{slug}"                         # <--- E AQUI

    nomes = []
    try:
        with FTP(FTP_HOST, timeout=25) as ftp:
            ftp.set_pasv(True)
            ftp.login(FTP_USER, FTP_PASS)
            ftp.cwd(base)
            for name in ftp.nlst():
                if name in ('.', '..'):
                    continue
                try:
                    ftp.size(name)
                    nomes.append(name)
                except error_perm:
                    pass
        nomes.sort()
        return {"cadeira": cadeira, "ficheiros": nomes}
    except Exception as e:
        print("⚠️ FTP erro:", e)
        return {"cadeira": cadeira, "ficheiros": []} 




#posso apagar acho eu
@app.get("/listar_ficheiros")
async def listar_ficheiros(cadeira: str):
    import requests
    import os

    # URL do PHP no InfinityFree que lista os ficheiros
    remote_url = f"https://TEU_DOMINIO.infinityfreeapp.com/list.php?cadeira={cadeira}"

    try:
        print(f"📡 Tentando listar ficheiros remotos para cadeira: {cadeira}")
        resp = requests.get(remote_url, timeout=5)

        if resp.status_code == 200:
            data = resp.json()  # espera JSON do PHP
            return {"cadeira": cadeira, "ficheiros": data.get("ficheiros", [])}
        else:
            print(f"⚠️ Erro remoto: Status {resp.status_code}")
    except Exception as e:
        print(f"⚠️ Falha ao buscar ficheiros remotos: {e}")

    # Se não conseguir remoto, devolve lista local (apenas debug)
    local_path = os.path.join("materiais", cadeira)
    if os.path.exists(local_path):
        return {"cadeira": cadeira, "ficheiros": os.listdir(local_path)}
    else:
        return {"cadeira": cadeira, "ficheiros": []}




#posso apagar acho eu
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















# meter na base de dados e data/{CADEIRA} — VERSÃO FTP (sem HTML do host)
@app.post("/confirmar_ficheiros")
def confirmar_ficheiros(dados: ConfirmacaoFicheiros):
    try:
        cadeira_nome = (dados.cadeira or "").strip()
        ficheiros = dados.ficheiros or []

        if not cadeira_nome:
            return JSONResponse(content={"erro": "Cadeira inválida."}, status_code=400)
        if not ficheiros:
            return JSONResponse(content={"erro": "Nenhum ficheiro selecionado."}, status_code=400)

        # pasta local onde guardamos os ficheiros (pode ter acentos)
        pasta_destino = os.path.join("data", cadeira_nome)
        os.makedirs(pasta_destino, exist_ok=True)

        # slug da pasta remota (igual ao PHP do upload)
        slug = cadeira_slug_php_like(cadeira_nome)

        conn = ligar_bd()
        cursor = conn.cursor()

        novos_confirmados, repetidos, falhados = [], [], []
        headers = {"User-Agent": "Mozilla/5.0 (ChatbotUPT)", "Referer": REMOTE_BASE_URL}

        for nome in ficheiros:
            nome = (nome or "").strip()
            if not nome:
                continue

            # já existe na BD?
            cursor.execute(
                "SELECT COUNT(*) FROM ficheiros_confirmados WHERE nome=%s AND cadeira=%s",
                (nome, cadeira_nome),
            )
            if cursor.fetchone()[0] > 0:
                repetidos.append(nome)
                continue

            # URL pública (nome encodado)
            nome_url = quote(nome, safe="._-()")
            url_publica = f"{REMOTE_BASE_URL}/materiais/{slug}/{nome_url}"
            destino_fisico = os.path.join(pasta_destino, nome)

            # 1) tenta HTTP
            ok = False
            try:
                r = requests.get(url_publica, headers=headers, timeout=30, stream=True)
                ct = (r.headers.get("Content-Type") or "").lower()
                if r.status_code == 200 and "text/html" not in ct:
                    with open(destino_fisico, "wb") as out:
                        for chunk in r.iter_content(1024 * 1024):
                            if chunk:
                                out.write(chunk)
                    ok = True
                else:
                    print(f"⚠️ HTTP falhou: status={r.status_code} ct={ct}")
            except Exception as e:
                print(f"⚠️ HTTP exceção '{nome}': {e}")

            # 2) fallback FTP se necessário
            if not ok:
                try:
                    with FTP(FTP_HOST, timeout=25) as ftp:
                        ftp.set_pasv(True)
                        ftp.login(FTP_USER, FTP_PASS)
                        ftp.cwd(f"/htdocs/materiais/{slug}")
                        with open(destino_fisico, "wb") as f:
                            ftp.retrbinary(f"RETR {nome}", f.write)
                    ok = True
                except Exception as e:
                    print(f"❌ FTP falhou '{nome}': {e}")

            if not ok:
                falhados.append(nome)
                continue

            # valida conteúdo base (evita ficheiro HTML/lixo)
            ext = os.path.splitext(nome)[1].lower()
            valido = (ext == ".pdf" and is_valid_pdf(destino_fisico)) or \
                     (ext == ".docx" and is_valid_docx(destino_fisico))
            if not valido:
                print(f"⚠️ Conteúdo inválido após download: {destino_fisico}")
                try:
                    os.remove(destino_fisico)
                except:
                    pass
                falhados.append(nome)
                continue

            # inserir na BD
            try:
                cursor.execute(
                    "INSERT INTO ficheiros_confirmados (nome, cadeira, caminho) VALUES (%s, %s, %s)",
                    (nome, cadeira_nome, url_publica),
                )
                novos_confirmados.append(nome)
            except Exception as e:
                print(f"⚠️ Falha ao inserir BD '{nome}': {e}")
                falhados.append(nome)

        conn.commit()
        cursor.close()
        conn.close()

        # gera embeddings em background
        if novos_confirmados:
            threading.Thread(
                target=gerar_embeddings_para_ficheiros,
                args=(cadeira_nome, novos_confirmados),
                daemon=True,
            ).start()

        return {
            "mensagem": "ok",
            "novos": novos_confirmados,
            "repetidos": repetidos,
            "falhados": falhados,
        }

    except Exception as e:
        print("❌ ERRO /confirmar_ficheiros:", e)
        return JSONResponse(content={"erro": str(e)}, status_code=500)




#-------------------REGISTO ALUNO/DOCENTE------------------


class RegistoDocente(BaseModel):
    nome: str
    email: str
    password: str
    cadeiras: Optional[List[str]] = []

class RegistoAluno(BaseModel):
    nome: str
    email: str
    password: str
    cadeiras: Optional[List[str]] = []


@app.post("/registar_docente")
def registar_docente(dados: RegistoDocente):
    try:
        conn = ligar_bd()
        cursor = conn.cursor()

        # 1) impedir emails repetidos
        cursor.execute("SELECT COUNT(*) FROM docentes WHERE email=%s", (dados.email,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return JSONResponse(content={"erro": "Email já registado."}, status_code=409)

        # 2) gravar em docentes (cadeiras em JSON string p/ manter compatibilidade)
        cadeiras_json = json.dumps(dados.cadeiras or [], ensure_ascii=False)
        cursor.execute("""
            INSERT INTO docentes (nome, email, password, cadeiras)
            VALUES (%s, %s, %s, %s)
        """, (dados.nome, dados.email, dados.password, cadeiras_json))

        # 3) também preencher a tabela de relação 'leciona' (se existir)
        if dados.cadeiras:
            for cad in dados.cadeiras:
                cursor.execute("""
                    INSERT INTO leciona (email, cadeira)
                    SELECT %s, %s FROM DUAL
                    WHERE NOT EXISTS (
                        SELECT 1 FROM leciona WHERE email=%s AND cadeira=%s
                    )
                """, (dados.email, cad, dados.email, cad))

        conn.commit()
        conn.close()
        return {"mensagem": "Docente registado com sucesso."}
    except Exception as e:
        print("❌ ERRO /registar_docente:", e)
        return JSONResponse(content={"erro": str(e)}, status_code=500)




@app.post("/registar_aluno")
def registar_aluno(dados: RegistoAluno):
    try:
        conn = ligar_bd()
        cursor = conn.cursor()

        # 1) impedir emails repetidos
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE email=%s", (dados.email,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return JSONResponse(content={"erro": "Email já registado."}, status_code=409)

        
        cursor.execute("""
            INSERT INTO alunos (nome, email, password)
            VALUES (%s, %s, %s)
        """, (dados.nome, dados.email, dados.password))

        if dados.cadeiras:
            for cad in dados.cadeiras:
                cursor.execute("""
                    INSERT INTO inscricoes (email, cadeira)
                    SELECT %s, %s FROM DUAL
                    WHERE NOT EXISTS (
                        SELECT 1 FROM inscricoes WHERE email=%s AND cadeira=%s
                    )
                """, (dados.email, cad, dados.email, cad))

        conn.commit()
        conn.close()
        return {"mensagem": "Aluno registado com sucesso."}
    except Exception as e:
        print("ERRO /registar_aluno:", e)
        return JSONResponse(content={"erro": str(e)}, status_code=500)
    


# ------------------ LOGIN -------------------
class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login_docente")
def login_docente(dados: LoginRequest):
    print("📩 Pedido recebido para login_docente:", dados.email, dados.password)

    conn = ligar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT nome, email, cadeiras FROM docentes WHERE email = %s AND password = %s",
        (dados.email, dados.password)
    )
    docente = cursor.fetchone()
    conn.close()

    if docente:
        print("✅ Login docente OK:", docente["nome"])
        return docente
    else:
        print("❌ Credenciais inválidas para docente:", dados.email)
        return JSONResponse(content={"erro": "Credenciais inválidas."}, status_code=401)



@app.post("/login_estudante")
def login_estudante(dados: LoginRequest):
    print("📩 Pedido recebido para login_estudante:", dados.email, dados.password)

    conn = ligar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT nome, email FROM alunos WHERE email = %s AND password = %s",
        (dados.email, dados.password)
    )
    aluno = cursor.fetchone()

    if aluno:
        cursor.execute("SELECT cadeira FROM inscricoes WHERE email = %s", (dados.email,))
        resultado_cadeiras = cursor.fetchall()
        aluno["cadeiras"] = [row["cadeira"] for row in resultado_cadeiras]
        conn.close()
        print("✅ Login estudante OK:", aluno["nome"])
        return aluno
    else:
        conn.close()
        print("❌ Credenciais inválidas para estudante:", dados.email)
        return JSONResponse(content={"erro": "Credenciais inválidas."}, status_code=401)

    


#------------------------------------------------------




#listar na dropdown as cadeiras que o docente leciona
@app.get("/listar_cadeiras_docente")
def listar_cadeiras_docente(email: str):
    try:
        conn = ligar_bd()
        cursor = conn.cursor()

        cursor.execute("SELECT cadeira FROM leciona WHERE email = %s", (email,))
        resultados = cursor.fetchall()
        conn.close()

        cadeiras = [linha[0] for linha in resultados]
        return {"cadeiras": cadeiras}

    except Exception as e:
        print("❌ ERRO ao listar cadeiras:", e)
        return JSONResponse(content={"erro": str(e)}, status_code=500)

    

#------------------------------------------------------
@app.get("/ficheiros_confirmados")
def ficheiros_confirmados(cadeira: str = Query(...)):
    try:
        cadeira = (cadeira or "").strip()
        if not cadeira:
            return JSONResponse(content={"erro": "Cadeira inválida."}, status_code=400)

        conn = ligar_bd()
        cursor = conn.cursor(dictionary=True)

        # Se tiveres 'data_confirmacao' na tabela, podes ordenar por ela. Aqui uso nome por segurança.
        cursor.execute("""
            SELECT nome, caminho
            FROM ficheiros_confirmados
            WHERE cadeira = %s
            ORDER BY nome ASC
        """, (cadeira,))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "cadeira": cadeira,
            "ficheiros": [{"nome": r["nome"], "caminho": r["caminho"]} for r in rows]
        }
    except Exception as e:
        print("❌ ERRO /ficheiros_confirmados:", e)
        return JSONResponse(content={"erro": str(e)}, status_code=500)















#--------------------CHATBOT----------------------

@app.post("/perguntar")
def perguntar(pergunta: str = Body(...), cadeira: str = Body(...), email: str = Body(...)):
    try:
        # 1) valida inscrição do aluno
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="chatbot")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM inscricoes WHERE email=%s AND cadeira=%s", (email, cadeira))
        inscrito = cursor.fetchone()
        conn.close()

        if not inscrito:
            return JSONResponse(content={"erro": "🚫 Não estás inscrito nesta cadeira."}, status_code=403)

        # 2) garantir que existe base de embeddings
        pasta_db = os.path.join("db", cadeira)
        if not os.path.isdir(pasta_db) or len(os.listdir(pasta_db)) == 0:
            return {"resposta": "❌ Ainda não existem embeddings para esta cadeira (ou estão a ser gerados). Tenta de novo em instantes."}

        # 3) carregar Chroma + modelo
        embeddings = OllamaEmbeddings(model="nomic-embed-text")  # precisa do ollama serve + modelo puxado
        db = Chroma(persist_directory=pasta_db, embedding_function=embeddings)

        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

        modelo = Ollama(model="gemma:2b-instruct")  # idem, modelo puxado no ollama

        prompt_template = """
Usa APENAS o contexto abaixo para responder.
Responde em português, claro e objetivo.
Se o contexto não tiver a resposta, diz: "Não tenho informações suficientes para responder."

Contexto:
{context}

Pergunta: {question}
Resposta:
"""
        prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

        qa_chain = RetrievalQA.from_chain_type(
            llm=modelo,
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )

        resposta = qa_chain.run(pergunta)
        if not resposta or not str(resposta).strip():
            resposta = "Não tenho informações suficientes para responder."

        return {"resposta": resposta}

    except Exception as e:
        print("❌ ERRO NO /perguntar:", e)
        return JSONResponse(content={"erro": str(e)}, status_code=500)