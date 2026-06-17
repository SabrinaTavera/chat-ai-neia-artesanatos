import chromadb
from faq_neia import faq

# Cria banco de dados persistente (salva no disco)
client = chromadb.PersistentClient(path="./banco_neia")

# Apaga coleção antiga e cria nova
try:
    client.delete_collection("faq_neia")
    print("🗑️ Coleção antiga removida!")
except:
    pass

colecao = client.create_collection(name="faq_neia")

# Carrega o FAQ
documentos = [item["resposta"] for item in faq]
ids = [item["id"] for item in faq]
metadados = [{"pergunta": item["pergunta"]} for item in faq]

colecao.add(
    documents=documentos,
    ids=ids,
    metadatas=metadados
)

print(f"✅ FAQ carregado! {len(faq)} perguntas indexadas.")

# Teste rápido
pergunta = "que agulha uso para amigurumi?"
resultado = colecao.query(query_texts=[pergunta], n_results=1)
print(f"\n🔍 Teste — Pergunta: {pergunta}")
print(f"📌 Resposta encontrada: {resultado['documents'][0][0]}")