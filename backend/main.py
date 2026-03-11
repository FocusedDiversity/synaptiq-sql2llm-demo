from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import query, schema, suggestions

app = FastAPI(title="Synaptiq SQL2LLM Demo", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/api")
app.include_router(schema.router, prefix="/api")
app.include_router(suggestions.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
