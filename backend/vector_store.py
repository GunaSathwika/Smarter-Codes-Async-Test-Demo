# backend/vector_store.py

import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from chromadb import EphemeralClient
from tiktoken import get_encoding

# Ephemeral in-memory vector database
client = EphemeralClient()

# Fast lightweight embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------------------------------------
# 1. Fetch & clean webpage text
# ---------------------------------------------------------
def fetch_text(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return ""

        soup = BeautifulSoup(r.text, "html.parser")

        # Remove script/style/noscript tags
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n").strip()
        if not text:
            return ""

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    except Exception as e:
        print("❌ Error fetching URL:", e)
        return ""


# ---------------------------------------------------------
# 2. Split text into token-aware chunks (with fallback)
# ---------------------------------------------------------
def chunk_text_by_tokens(text, max_tokens=500):
    if not text or len(text.strip()) == 0:
        return []

    try:
        enc = get_encoding("gpt2")
        tokens = enc.encode(text)

        if not tokens:
            raise Exception("Tokenization returned empty")

        chunks = []
        i = 0
        while i < len(tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = enc.decode(chunk_tokens)
            chunks.append(chunk_text)
            i += max_tokens

        return chunks

    except Exception as e:
        print("⚠️ Tokenization failed, falling back to character-based chunking:", e)
        # fallback: safe splitting by characters
        return [text[i:i + 3000] for i in range(0, len(text), 3000)]


# ---------------------------------------------------------
# 3. Index + Search
# ---------------------------------------------------------
def index_and_search(url, query, top_k=10):

    # ---- FETCH TEXT ----
    text = fetch_text(url)
    if not text:
        return [{
            "id": "none",
            "text": "No text could be extracted from the webpage.",
            "score": 0
        }]

    # ---- CHUNKING ----
    chunks = chunk_text_by_tokens(text, max_tokens=500)
    if not chunks:
        return [{
            "id": "none",
            "text": "Failed to split webpage text into chunks.",
            "score": 0
        }]

    # ---- EMBEDDINGS ----
    try:
        embeddings = model.encode(chunks, show_progress_bar=False).tolist()
    except Exception as e:
        print("❌ Embedding failed:", e)
        return [{
            "id": "none",
            "text": "Embedding generation failed.",
            "score": 0
        }]

    if not embeddings or len(embeddings) == 0:
        return [{
            "id": "none",
            "text": "Embeddings list is empty.",
            "score": 0
        }]

    # ---- CREATE COLLECTION ----
    col = client.create_collection(name="tmp")

    ids = [f"chunk-{i}" for i in range(len(chunks))]

    # ---- SAFE ADD ----
    try:
        col.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids
        )
    except Exception as e:
        print("❌ Chroma add() failed:", e)
        return [{
            "id": "none",
            "text": "Failed to add embeddings to vector database.",
            "score": 0
        }]

    # ---- QUERY ----
    try:
        q_emb = model.encode([query])[0].tolist()
        res = col.query(query_embeddings=[q_emb], n_results=top_k)
    except Exception as e:
        print("❌ Query failed:", e)
        client.delete_collection(name="tmp")
        return [{"id": "none", "text": "Search failed.", "score": 0}]

    # ---- PARSE RESULTS ----
    results = []
    for ids_row, docs_row, distances_row in zip(res["ids"], res["documents"], res["distances"]):
        for id_, doc, dist in zip(ids_row, docs_row, distances_row):
            results.append({
                "id": id_,
                "text": doc,
                "score": float(dist)
            })

    # Cleanup
    client.delete_collection(name="tmp")

    return results
