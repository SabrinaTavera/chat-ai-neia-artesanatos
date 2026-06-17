import chromadb
from chromadb.utils import embedding_functions

# Modelo treinado em português e inglês
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="neuralmind/bert-base-portuguese-cased"
)

client = chromadb.Client()
colecao = client.create_collection(
    "teste_neia",
    embedding_function=embedding_fn
)

# Mesmos documentos de antes...
documentos = [
    "Entregamos para todo o Brasil em até 5 dias úteis",
    "Aceitamos PIX, cartão de crédito e boleto bancário",
    "O fio Amigurumi é ideal para iniciantes pois é macio e fácil de trabalhar",
    "Fazemos trocas em até 7 dias após o recebimento do produto",
    "Nossos kits já vêm com agulha, fio e olhinhos inclusos"
]

colecao.add(
    documents=documentos,
    ids=["doc1", "doc2", "doc3", "doc4", "doc5"]
)

pergunta = "como posso pagar?"
resultados = colecao.query(
    query_texts=[pergunta],
    n_results=1
)

print(f"\n Pergunta: {pergunta}")
print(f" Resposta encontrada: {resultados['documents'][0][0]}")