# Chatbot Educacional com IA

Aplicação fullstack desenvolvida no meu estágio curricular em Engenharia Informática.  
O objetivo é permitir que os estudantes obtenham respostas baseadas **exclusivamente nos materiais fornecidos pelos docentes** para cada unidade curricular.

---

## Tecnologias Utilizadas

**Backend:** Python • FastAPI • LangChain • Ollama (Gemma 2b-instruct) • ChromaDB • MySQL  
**Frontend:** React • Fetch API  
**Infraestrutura:** InfinityFree (armazenamento de ficheiros)

---

## Funcionalidades Principais

- Upload e gestão de materiais pelos docentes (PDF, DOCX, PPTX)  
- Extração automática de texto  
- Geração de embeddings por cadeira  
- Pesquisa semântica com ChromaDB  
- Respostas contextualizadas usando IA local (Ollama)  
- Dashboard de aluno e docente  
- Autenticação e ligação a MySQL  

---

## Arquitetura do Sistema

- **Frontend React** gere login, dashboards e chat  
- **Backend FastAPI** trata pedidos, gera embeddings e comunica com o modelo  
- **Ollama (Gemma 2b-instruct)** gera respostas com base nos documentos  
- **ChromaDB** armazena vetores para pesquisa semântica  
- **MySQL** guarda utilizadores, cadeiras e ficheiros confirmados  
- **InfinityFree** funciona como repositório de ficheiros disponibilizados  

---

## Fluxo de Funcionamento

1. O docente seleciona os materiais a disponibilizar  
2. O backend extrai texto e gera embeddings  
3. Os embeddings são guardados em ChromaDB  
4. O aluno coloca questões no chat  
5. A IA responde com base **apenas** nos documentos confirmados  

---

## Desafios Resolvidos

- Integração FastAPI + LangChain + ChromaDB  
- Geração de embeddings por unidade curricular  
- Persistência de dados com MySQL  
- Orquestração do pipeline de IA (download → extração → embeddings → resposta)  
- Otimização do desempenho da IA local  
- Gestão de ficheiros utilizando InfinityFree  

---

## Como Executar

### Backend
```bash
cd Backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

---

## Frontend
```bash
cd Frontend
npm install
npm start



Contas de Teste
Docentes
Email	Password	Cadeiras
ana.silva@upt.pt
	ana123	IA, Redes
carlos.mendes@upt.pt
	carlos123	Design Gráfico, Animação
Alunos
Email	Password
joana@upt.pt
	1234
ana@upt.pt
	1234
