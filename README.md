# Smarter.Codes — Async test

## Prereqs
- Python 3.10+, Node 18+
- pip packages: fastapi, uvicorn, requests, beautifulsoup4, chromadb, sentence-transformers, tiktoken
- npm packages: (from Vite template)

## Run backend
# create project folder
mkdir smarter-codes && cd smarter-codes

# python env
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate

# install backend deps
pip install fastapi uvicorn requests beautifulsoup4 chromadb sentence-transformers tiktoken

# create backend folder
mkdir backend

Files: backend/main.py, backend/vector_store.py, backend/utils.py

uvicorn backend.main:app --reload --port 8000



## Run frontend
# from project root
npm create vite@latest frontend -- --template react
cd frontend
npm install

npm run dev

## Example
URL: https://example.com
Query: example

