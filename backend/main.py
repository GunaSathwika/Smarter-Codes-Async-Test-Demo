from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.vector_store import index_and_search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    url: str
    query: str

@app.get("/")
def home():
    return {"status": "Backend working!"}

@app.post("/api/search")
async def search(req: SearchRequest):
    results = index_and_search(req.url, req.query, top_k=10)
    return {"results": results}