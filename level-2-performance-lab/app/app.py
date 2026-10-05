"""Ask + Test Lab app. Throttles Genie Conversation API to about 5 questions per minute."""

from __future__ import annotations

import os
import time
from typing import Any

from databricks.sdk import WorkspaceClient
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Apex Genie Lab")
_last_ask = 0.0
MIN_INTERVAL_S = 13.0


class AskBody(BaseModel):
    question: str


def _client() -> WorkspaceClient:
    return WorkspaceClient()


def _space_id() -> str:
    value = os.environ.get("GENIE_SPACE_ID", "").strip()
    if not value:
        raise HTTPException(500, "Set GENIE_SPACE_ID on the app")
    return value


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html><head><meta charset="utf-8"><title>Apex Genie Lab</title>
<style>
 body { font-family: sans-serif; margin: 24px; }
 nav button { margin-right: 8px; }
 textarea { width: 100%; height: 80px; }
 pre { background: #111; color: #eee; padding: 12px; overflow: auto; }
</style></head>
<body>
<nav>
  <button onclick="show('ask')">Ask</button>
  <button onclick="show('lab')">Test Lab</button>
</nav>
<section id="ask">
  <h1>Ask</h1>
  <p>One question every 13 seconds.</p>
  <textarea id="q" placeholder="What is overall OEE?"></textarea>
  <p><button onclick="ask()">Send</button></p>
  <pre id="out"></pre>
</section>
<section id="lab" hidden>
  <h1>Test Lab</h1>
  <p>Reads scorecard_runs from your workshop schema.</p>
  <pre id="labout">Open /scorecard after notebook 13 writes the table.</pre>
  <p><button onclick="loadScore()">Reload</button></p>
</section>
<script>
function show(id) {
  document.getElementById('ask').hidden = id !== 'ask';
  document.getElementById('lab').hidden = id !== 'lab';
}
async function ask() {
  const question = document.getElementById('q').value;
  const res = await fetch('/ask', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({question})});
  document.getElementById('out').textContent = await res.text();
}
async function loadScore() {
  const res = await fetch('/scorecard');
  document.getElementById('labout').textContent = await res.text();
}
</script>
</body></html>
"""


@app.post("/ask")
def ask(body: AskBody) -> dict[str, Any]:
    global _last_ask
    now = time.time()
    wait = MIN_INTERVAL_S - (now - _last_ask)
    if wait > 0:
        time.sleep(wait)
    _last_ask = time.time()
    w = _client()
    space = _space_id()
    started = w.api_client.do(
        "POST",
        f"/api/2.0/genie/spaces/{space}/start-conversation",
        body={"content": body.question},
    )
    return {"started": started}


@app.get("/scorecard")
def scorecard() -> dict[str, Any]:
    catalog = os.environ.get("WORKSHOP_CATALOG", "")
    schema = os.environ.get("WORKSHOP_SCHEMA", "")
    warehouse = os.environ.get("DATABRICKS_WAREHOUSE_ID", "")
    if not (catalog and schema and warehouse):
        return {"error": "Set WORKSHOP_CATALOG, WORKSHOP_SCHEMA, DATABRICKS_WAREHOUSE_ID"}
    w = _client()
    stmt = w.statement_execution.execute_statement(
        warehouse_id=warehouse,
        statement=f"SELECT agent, verdict, COUNT(*) AS n FROM {catalog}.{schema}.scorecard_runs GROUP BY agent, verdict",
        wait_timeout="30s",
    )
    return {"result": stmt.as_dict()}
