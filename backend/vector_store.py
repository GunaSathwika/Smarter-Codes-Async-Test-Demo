# backend/vector_store.py

import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from chromadb import EphemeralClient
from tiktoken import get_encoding

# new required client
client = EphemeralClient()

model = SentenceTransformer("all-MiniLM-L6-v2")

def fetch_text(url):
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def chunk_text_by_tokens(text, max_tokens=500):
    enc = get_encoding("gpt2")
    tokens = enc.encode(text)
    chunks = []
    i = 0
    while i < len(tokens):
        chunk_tokens = tokens[i:i+max_tokens]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)
        i += max_tokens
    return chunks

def index_and_search(url, query, top_k=10):
    text = fetch_text(url)
    chunks = chunk_text_by_tokens(text, max_tokens=500)

    col = client.create_collection(name="tmp")
    ids = [f"chunk-{i}" for i in range(len(chunks))]
    emb = model.encode(chunks, show_progress_bar=False)

    col.add(documents=chunks, embeddings=emb.tolist(), ids=ids)

    q_emb = model.encode([query])[0].tolist()
    res = col.query(query_embeddings=[q_emb], n_results=top_k)

    results = []
    for ids_row, docs_row, distances_row in zip(res["ids"], res["documents"], res["distances"]):
        for id_, doc, dist in zip(ids_row, docs_row, distances_row):
            results.append({"id": id_, "text": doc, "score": float(dist)})

    client.delete_collection(name="tmp")
    return results