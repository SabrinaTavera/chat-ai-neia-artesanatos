import json
from faq_neia import faq

def buscar_contexto(pergunta):
    pergunta_lower = pergunta.lower()
    
    # Busca por palavras-chave
    melhor = None
    maior_score = 0
    
    for item in faq:
        palavras_pergunta = set(item["pergunta"].lower().split())
        palavras_busca = set(pergunta_lower.split())
        score = len(palavras_pergunta & palavras_busca)
        
        if score > maior_score:
            maior_score = score
            melhor = item
    
    if melhor:
        return melhor["resposta"]
    return "Não encontrei informações sobre isso. Entre em contato conosco!"