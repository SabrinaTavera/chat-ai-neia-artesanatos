import sounddevice as sd
import soundfile as sf
import whisper
import edge_tts
import asyncio
import requests
import numpy as np
import os

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
Seja breve e objetiva nas respostas."""

# ── Funções ────────────────────────────────────────────────

def gravar_audio():
    print("\n� Gravando... fale agora!")
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
    print("� Transcrevendo com Whisper...")
    modelo = whisper.load_model("base")
    resultado = modelo.transcribe(AUDIO_ARQUIVO, language="pt")
    texto = resultado["text"].strip()
    print(f"� Você disse: {texto}")
    return texto

def perguntar_ollama(pergunta):
    print("� Consultando Ollama...")
    payload = {
        "model": MODELO,
        "prompt": f"[SYSTEM]{SYSTEM_PROMPT}[/SYSTEM]\n\nPergunta: {pergunta}",
        "stream": False
    }
    resposta = requests.post(OLLAMA_URL, json=payload)
    texto = resposta.json()["response"].strip()
    print(f"� Resposta: {texto}")
    return texto

async def falar_resposta(texto):
    print("� Gerando voz com Edge TTS...")
    comunicador = edge_tts.Communicate(texto, voice="pt-BR-FranciscaNeural")
    await comunicador.save(RESPOSTA_ARQUIVO)
    os.system(f"start {RESPOSTA_ARQUIVO}")

# ── Loop principal ─────────────────────────────────────────

def main():
    print("=" * 50)
    print("  � Assistente Virtual - Néia Artesanatos")
    print("=" * 50)
    print("Pressione ENTER para falar ou 'sair' para encerrar")

    while True:
        comando = input("\n▶ Pressione ENTER para falar: ").strip().lower()

        if comando == "sair":
            print("� Até logo!")
            break

        gravar_audio()
        pergunta = transcrever_audio()

        if not pergunta:
            print("⚠️ Não entendi, tente novamente.")
            continue

        resposta = perguntar_ollama(pergunta)
        asyncio.run(falar_resposta(resposta))

if __name__ == "__main__":
    main()