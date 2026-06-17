import sounddevice as sd
import soundfile as sf
import whisper
import edge_tts
import asyncio
import requests
import numpy as np
import os
import chromadb
from chromadb.utils import embedding_functions

# ── Configurações ──────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "phi3"
AUDIO_ARQUIVO = "gravacao.wav"
RESPOSTA_ARQUIVO = "resposta.mp3"
DURACAO_GRAVACAO = 5  # segundos
SAMPLE_RATE = 16000

SYSTEM_PROMPT = """Você é a assistente virtual da Néia Artesanatos, 
uma loja especializada em amigurumi, fios, bordado e artesanato.
Responda sempre em português, de forma simpática e prestativa.
Seja breve e objetiva nas respostas.
Use apenas as informações fornecidas no contexto para responder.
Se não souber a resposta, diga que vai verificar e retornar em breve."""

# ── Inicializa ChromaDB ────────────────────────────────────
def inicializar_banco():
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
    return colecao

def buscar_contexto(colecao, pergunta):
    resultado = colecao.query(
        query_texts=[pergunta],
        n_results=2
    )
    documentos = resultado["documents"][0]
    contexto = "\n".join(documentos)
    return contexto

# ── Funções de voz ─────────────────────────────────────────
def gravar_audio():
    print("\n🎤 Gravando... fale agora!")
    audio = sd.rec(
        int(DURACAO_GRAVACAO * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype=np.float32
    )
    sd.wait()
    sf.write(AUDIO_ARQUIVO, audio, SAMPLE_RATE)
    print("✅ Gravação concluída!")

def transcrever_audio():
    print("📝 Transcrevendo com Whisper...")
    modelo = whisper.load_model("base")
    resultado = modelo.transcribe(AUDIO_ARQUIVO, language="pt")
    texto = resultado["text"].strip()
    print(f"💬 Você disse: {texto}")
    return texto

def perguntar_ollama(pergunta, contexto):
    print("🧠 Consultando Ollama...")
    prompt = f"""[SYSTEM]{SYSTEM_PROMPT}[/SYSTEM]

Contexto da loja:
{contexto}

Pergunta do cliente: {pergunta}

Responda com base no contexto acima."""

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False
    }
    resposta = requests.post(OLLAMA_URL, json=payload)
    texto = resposta.json()["response"].strip()
    print(f"🤖 Resposta: {texto}")
    return texto

async def falar_resposta(texto):
    print("🔊 Gerando voz com Edge TTS...")
    comunicador = edge_tts.Communicate(texto, voice="pt-BR-FranciscaNeural")
    await comunicador.save(RESPOSTA_ARQUIVO)
    os.system(f"start {RESPOSTA_ARQUIVO}")

# ── Loop principal ─────────────────────────────────────────
def main():
    print("=" * 50)
    print("  🧶 Assistente Virtual - Néia Artesanatos")
    print("=" * 50)

    colecao = inicializar_banco()

    print("\nPressione ENTER para falar ou digite 'sair' para encerrar")

    while True:
        comando = input("\n▶ Pressione ENTER para falar: ").strip().lower()

        if comando == "sair":
            print("👋 Até logo!")
            break

        gravar_audio()
        pergunta = transcrever_audio()

        if not pergunta:
            print("⚠️ Não entendi, tente novamente.")
            continue

        print("🔍 Buscando na base de conhecimento...")
        contexto = buscar_contexto(colecao, pergunta)
        print(f"📌 Contexto encontrado: {contexto[:100]}...")

        resposta = perguntar_ollama(pergunta, contexto)
        asyncio.run(falar_resposta(resposta))

if __name__ == "__main__":
    main()