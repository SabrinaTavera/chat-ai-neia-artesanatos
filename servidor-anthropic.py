from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import anthropic
import chromadb
from chromadb.utils import embedding_functions
import os

# ── Configurações ──────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "sua-api-key-aqui")
MODELO = "claude-sonnet-4-6"

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

# ── Inicializa Anthropic ───────────────────────────────────
cliente_anthropic = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ── Inicializa ChromaDB ────────────────────────────────────
print("📚 Carregando base de conhecimento...")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="neuralmind/bert-base-portuguese-cased"
)
client_chroma = chromadb.PersistentClient(path="./banco_neia")
colecao = client_chroma.get_or_create_collection(
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
    prompt = f"""Contexto da loja:
{contexto}

Pergunta do cliente: {pergunta.texto}

Responda com base no contexto acima."""

    # Chama API da Anthropic
    mensagem = cliente_anthropic.messages.create(
        model=MODELO,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    texto = mensagem.content[0].text.strip()
    return {"resposta": texto}
