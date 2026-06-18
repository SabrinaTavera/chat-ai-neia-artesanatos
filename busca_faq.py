from faq_neia import faq

def buscar_contexto(pergunta):
    pergunta_lower = pergunta.lower()
    
    melhor = None
    maior_score = 0
    
    for item in faq:
        score = 0
        pergunta_faq = item["pergunta"].lower()
        resposta_faq = item["resposta"].lower()
        
        # Busca por palavras da pergunta do usuário
        for palavra in pergunta_lower.split():
            if len(palavra) > 3:  # ignora palavras curtas
                if palavra in pergunta_faq or palavra in resposta_faq:
                    score += 1
        
        if score > maior_score:
            maior_score = score
            melhor = item
    
    if melhor and maior_score > 0:
        return melhor["resposta"]
    return "Não encontrei informações sobre isso. Entre em contato conosco através do contato (18) 99634-0125!"