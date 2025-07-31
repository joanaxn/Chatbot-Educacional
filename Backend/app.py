# app.py
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
from utils import extrair_texto, preparar_embeddings
from query_data import responder_pergunta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

DATA_DIR = Path("data")
DB_DIR = Path("db")
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)





@app.post("/upload")
async def upload(file: UploadFile = File(...), cadeira: str = Form(...)):
    try:
        cadeira_id = cadeira.replace(" ", "_").lower()
        cadeira_path = DATA_DIR / cadeira_id
        cadeira_path.mkdir(parents=True, exist_ok=True)

        file_path = cadeira_path / file.filename

        # vê se já existe
        if file_path.exists():
            return JSONResponse(
                content={"erro": "Este ficheiro já foi enviado anteriormente."},
                status_code=400
            )

        # Guardar e processar o ficheiro
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        docs = extrair_texto(str(file_path))
        preparar_embeddings(docs, cadeira_id)

        return {"mensagem": "Ficheiro enviado e processado com sucesso!"}

    except ValueError as ve:
        return JSONResponse(content={"erro": str(ve)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"erro": f"Erro inesperado: {str(e)}"}, status_code=500)








#endpoint para responder a perguntas

@app.post("/perguntar")
async def perguntar(request: Request):
    try:
        body = await request.json()
        pergunta = body.get("pergunta")
        cadeira = body.get("cadeira")

        if not pergunta or not cadeira:
            return JSONResponse(content={"erro": "Pergunta ou cadeira em falta."}, status_code=400)

        resposta = responder_pergunta(pergunta, cadeira)
        return {"resposta": resposta}

    except Exception as e:
        return JSONResponse(content={"erro": f"Erro ao responder: {str(e)}"}, status_code=500)
