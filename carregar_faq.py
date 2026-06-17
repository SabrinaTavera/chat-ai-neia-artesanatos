import chromadb
from chromadb.utils import embedding_functions
from faq_neia import faq

# Modelo em português
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="neuralmind/bert-base-portuguese-cased"
)

# Cria banco de dados persistente (salva no disco)
client = chromadb.PersistentClient(path="./banco_neia")
colecao = client.get_or_create_collection(
    name="faq_neia",
    embedding_function=embedding_fn
)

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