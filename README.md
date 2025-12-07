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
- **Ollama (Gemma 2b-instruct)** gera respostas com base nos documentos confirmados  
- **ChromaDB** armazena vetores para pesquisa semântica  
- **MySQL** guarda utilizadores, inscrições e ficheiros confirmados  
- **InfinityFree** funciona como repositório para os materiais disponibilizados pelos docentes  

---

## Fluxo de Funcionamento

1. O docente seleciona os materiais a disponibilizar por cadeira  
2. O backend extrai texto e gera embeddings  
3. Os embeddings são guardados em ChromaDB  
4. O aluno coloca perguntas no chat da cadeira  
5. A IA responde com base **apenas nos documentos confirmados**  

---

## Desafios Resolvidos

- Integração FastAPI + LangChain + ChromaDB  
- Geração de embeddings por unidade curricular  
- Ligação e persistência de dados em MySQL  
- Orquestração de todo o pipeline (download → extração → embeddings → resposta)  
- Otimização do desempenho da IA local via Ollama  
- Gestão de ficheiros com InfinityFree  

---

## Como Executar

### Backend
cd Backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload


### Frontend
cd Frontend
npm install
npm start

### Contas de Teste
## Docentes
Email                     	 Password	           Cadeiras
ana.silva@upt.pt             ana123   	          	IA, Redes  
carlos.mendes@upt.pt         carlos123               Design Gráfico, Animação
	
## Alunos
Email                        Password
joana@upt.pt                 1234
ana@upt.pt                   1234
	
