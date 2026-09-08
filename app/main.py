from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .db import get_conn
from .filters import execute_filter
from .llm import parse_query

# The /query endpoint calls Gemini, which needs GOOGLE_API_KEY. Load a local
# .env if one exists; a key already present in the environment takes precedence.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(title="slim-lite")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class QueryBody(BaseModel):
    text: str
    org_id: int


@app.get("/people")
def list_people(org_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM people WHERE org_id = ? ORDER BY id", (org_id,)
    ).fetchall()
    conn.close()
    return {"people": [dict(r) for r in rows], "count": len(rows)}


@app.get("/tags")
def list_tags(org_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM tags WHERE org_id = ? ORDER BY name", (org_id,)
    ).fetchall()
    conn.close()
    return {"tags": [dict(r) for r in rows]}


@app.post("/query")
def run_query(body: QueryBody):
    filter_json = parse_query(body.text)
    people = execute_filter(filter_json, body.org_id)
    return {"people": people, "count": len(people), "filter": filter_json}


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
