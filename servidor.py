from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import chromadb
from chromadb.utils import embedding_functions

# ── Configurações ──────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "phi3"

SYSTEM_PROMPT = """Você é a assistente virtual da Néia Artesanatos, 
uma loja especializada em amigurumi, fios, bordado e artesanato.
Responda sempre em português, de forma simpática e prestativa.
Seja breve e objetiva nas respostas.
Use apenas as informações fornecidas no contexto para responder.
Se não souber a resposta, diga que vai verificar e retornar em breve."""

# ── Inicializa FastAPI ─────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Inicializa ChromaDB ────────────────────────────────────
print("📚 Carregando base de conhecimento...")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="neuralmind/bert-base-portuguese-cased"
)
client = chromadb.PersistentClient(path="./banco_neia")
colecao = client.get_or_create_collection(
    name="faq_neia",
    embedding_function=embedding_fn
)
print("✅ Base de conhecimento carregada!")

# ── Models ─────────────────────────────────────────────────
class Pergunta(BaseModel):
    texto: str

# ── Rotas ──────────────────────────────────────────────────
@app.get("/")
def index():
    return FileResponse("index.html")

@app.post("/perguntar")
def perguntar(pergunta: Pergunta):
    # Busca contexto no ChromaDB
    resultado = colecao.query(
        query_texts=[pergunta.texto],
        n_results=2
    )
    contexto = "\n".join(resultado["documents"][0])

    # Monta prompt com contexto
    prompt = f"""[SYSTEM]{SYSTEM_PROMPT}[/SYSTEM]

Contexto da loja:
{contexto}

Pergunta do cliente: {pergunta.texto}

Responda com base no contexto acima."""

    # Chama Ollama
    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False
    }
    resposta = requests.post(OLLAMA_URL, json=payload)
    texto = resposta.json()["response"].strip()

    return {"resposta": texto}
