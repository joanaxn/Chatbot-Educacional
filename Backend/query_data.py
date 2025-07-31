from pathlib import Path
from langchain_chroma import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import time

DB_DIR = Path("db")

def responder_pergunta(pergunta, cadeira):
    cadeira_id = cadeira.replace(" ", "_").lower()
    persist_dir = DB_DIR / cadeira_id

    if not persist_dir.exists():
        return "⚠️ Materiais dessa cadeira não foram carregados ainda."

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectordb = Chroma(persist_directory=str(persist_dir), embedding_function=embeddings)
    retriever = vectordb.as_retriever()



    # Prompt para a resposta
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="""
Baseia-te apenas no contexto abaixo para responder à pergunta. 
Se a resposta não estiver no contexto, diz: "❌ Não encontrei informação suficiente nos documentos."

Contexto:
{context}

Pergunta: {question}

Resposta:"""
    )



    llm = OllamaLLM(model="gemma:2b-instruct")


    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_template}
    )

    try:
        start = time.time()
        resposta = qa.invoke(pergunta)
        end = time.time()
        print(f"⏱️ Tempo de resposta: {end - start:.2f} segundos")
    except Exception as e:
        print(f"❌ Erro ao gerar resposta com o modelo: {e}")
        return "❌ Ocorreu um erro ao gerar a resposta."

    resposta_str = resposta.strip() if isinstance(resposta, str) else resposta.get("result", "")
    if not resposta_str or resposta_str.lower().startswith(("não sei", "não encontrei", "não tenho", "i don't know")):
        return "❌ Não encontrei informação suficiente nos documentos."

    return resposta_str
