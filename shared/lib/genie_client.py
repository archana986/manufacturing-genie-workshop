"""Single place for Genie REST calls.

Lessons baked in:
- GET-merge-PATCH for serialized_space updates
- example_question_sqls sorted by id
- text_instructions (not sql_instructions)
- question and sql stored as arrays
- permissions object type is genie
- Azure UI links append ?o=<workspace_id>
- no ctx.apiToken(); use WorkspaceClient.config.authenticate
- eval-runs API is Beta; wrap here so shape changes stay in one file
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any
from urllib.parse import urlencode

import requests
from databricks.sdk import WorkspaceClient


def _hex32(raw: Any) -> str:
    text = str(raw or "")
    if re.fullmatch(r"[0-9a-f]{32}", text):
        return text
    return hashlib.md5(text.encode()).hexdigest()


class GenieClientError(RuntimeError):
    pass


class GenieClient:
    def __init__(self, warehouse_id: str | None = None, client: WorkspaceClient | None = None):
        self.w = client or WorkspaceClient()
        self.warehouse_id = warehouse_id
        host = (self.w.config.host or "").rstrip("/")
        if not host:
            raise GenieClientError("WorkspaceClient has no host")
        self.host = host
        self.workspace_id = str(getattr(self.w.config, "workspace_id", "") or "")

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        auth = getattr(self.w.config, "authenticate", None)
        if auth is None:
            raise GenieClientError("WorkspaceClient config has no authenticate()")
        try:
            result = auth(headers)
        except TypeError:
            result = auth()
        if isinstance(result, dict):
            headers.update(result)
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.host}{path}"
        response = requests.request(method, url, headers=self._headers(), timeout=60, **kwargs)
        if response.status_code >= 400:
            raise GenieClientError(f"{method} {path} -> {response.status_code}: {response.text[:800]}")
        return response

    def ui_space_url(self, space_id: str) -> str:
        url = f"{self.host}/genie/rooms/{space_id}"
        if self.workspace_id:
            return f"{url}?o={self.workspace_id}"
        return url

    def list_spaces(self) -> list[dict[str, Any]]:
        spaces: list[dict[str, Any]] = []
        page_token = None
        while True:
            query = {"page_token": page_token} if page_token else {}
            suffix = f"?{urlencode(query)}" if query else ""
            payload = self._request("GET", f"/api/2.0/genie/spaces{suffix}").json()
            spaces.extend(payload.get("spaces") or [])
            page_token = payload.get("next_page_token")
            if not page_token:
                break
        return spaces

    def get_space(self, space_id: str, include_serialized: bool = True) -> dict[str, Any]:
        query = "include_serialized_space=true" if include_serialized else ""
        path = f"/api/2.0/genie/spaces/{space_id}"
        if query:
            path = f"{path}?{query}"
        return self._request("GET", path).json()

    def create_space(
        self,
        title: str,
        description: str,
        table_identifiers: list[str],
        serialized_space: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        table_identifiers = sorted(table_identifiers)
        if serialized_space is None:
            serialized_space = {
                "version": 2,
                "data_sources": {
                    "tables": [{"identifier": ident} for ident in table_identifiers]
                },
            }
        else:
            tables = ((serialized_space.get("data_sources") or {}).get("tables")) or []
            tables = sorted(tables, key=lambda row: str(row.get("identifier", "")))
            serialized_space.setdefault("data_sources", {})["tables"] = tables
        body: dict[str, Any] = {
            "title": title,
            "description": description,
            "table_identifiers": table_identifiers,
            "serialized_space": json.dumps(serialized_space),
        }
        if self.warehouse_id:
            body["warehouse_id"] = self.warehouse_id
        return self._request("POST", "/api/2.0/genie/spaces", json=body).json()

    def patch_serialized_space(self, space_id: str, serialized_space: dict[str, Any]) -> dict[str, Any]:
        examples = (
            ((serialized_space.get("instructions") or {}).get("example_question_sqls")) or []
        )
        for item in examples:
            item["id"] = _hex32(item.get("id"))
        examples.sort(key=lambda item: str(item.get("id", "")))
        if "instructions" not in serialized_space:
            serialized_space["instructions"] = {}
        serialized_space["instructions"]["example_question_sqls"] = examples
        for item in ((serialized_space.get("instructions") or {}).get("text_instructions")) or []:
            item["id"] = _hex32(item.get("id"))
        for item in ((serialized_space.get("benchmarks") or {}).get("questions")) or []:
            item["id"] = _hex32(item.get("id"))
        tables = ((serialized_space.get("data_sources") or {}).get("tables")) or []
        if tables:
            tables = sorted(tables, key=lambda row: str(row.get("identifier", "")))
            serialized_space.setdefault("data_sources", {})["tables"] = tables
        body = {"serialized_space": json.dumps(serialized_space)}
        return self._request("PATCH", f"/api/2.0/genie/spaces/{space_id}", json=body).json()

    def merge_serialized_space(self, space_id: str, updater) -> dict[str, Any]:
        current = self.get_space(space_id, include_serialized=True)
        blob = current.get("serialized_space")
        if isinstance(blob, str):
            space = json.loads(blob)
        elif isinstance(blob, dict):
            space = blob
        else:
            raise GenieClientError("Space has no serialized_space; cannot GET-merge-PATCH")
        updated = updater(space)
        return self.patch_serialized_space(space_id, updated)

    def start_conversation(self, space_id: str, content: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/api/2.0/genie/spaces/{space_id}/start-conversation",
            json={"content": content},
        ).json()

    def get_message(self, space_id: str, conversation_id: str, message_id: str) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}",
        ).json()

    def wait_for_message(
        self,
        space_id: str,
        conversation_id: str,
        message_id: str,
        timeout_seconds: int = 180,
        poll_seconds: float = 3.0,
    ) -> dict[str, Any]:
        deadline = time.time() + timeout_seconds
        last: dict[str, Any] = {}
        while time.time() < deadline:
            last = self.get_message(space_id, conversation_id, message_id)
            status = (last.get("status") or last.get("state") or "").upper()
            if status in {"COMPLETED", "FAILED", "CANCELLED", "QUERY_RESULT_EXPIRED"}:
                return last
            time.sleep(poll_seconds)
        raise GenieClientError("TIMEOUT waiting for Genie message")

    def create_eval_run(self, space_id: str, benchmark_question_ids: list[str] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if benchmark_question_ids:
            body["benchmark_question_ids"] = benchmark_question_ids
        return self._request("POST", f"/api/2.0/genie/spaces/{space_id}/eval-runs", json=body).json()

    def get_eval_run(self, space_id: str, eval_run_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/2.0/genie/spaces/{space_id}/eval-runs/{eval_run_id}").json()

    def list_eval_results(self, space_id: str, eval_run_id: str) -> dict[str, Any]:
        return self._request(
            "GET", f"/api/2.0/genie/spaces/{space_id}/eval-runs/{eval_run_id}/results"
        ).json()

    def wait_eval_run(
        self,
        space_id: str,
        eval_run_id: str,
        timeout_seconds: int = 900,
        poll_seconds: float = 5.0,
    ) -> dict[str, Any]:
        deadline = time.time() + timeout_seconds
        last: dict[str, Any] = {}
        while time.time() < deadline:
            last = self.get_eval_run(space_id, eval_run_id)
            status = (last.get("status") or last.get("state") or "").upper()
            if status in {"COMPLETED", "FAILED", "CANCELLED", "ERROR"}:
                return last
            time.sleep(poll_seconds)
        raise GenieClientError("TIMEOUT waiting for eval-run")

    def set_permissions(self, space_id: str, access_control_list: list[dict[str, Any]]) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/api/2.0/permissions/genie/{space_id}",
            json={"access_control_list": access_control_list},
        ).json()

    def search_prompts(self, catalog_name: str, schema_name: str, max_results: int = 50, page_token: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {
            "catalog_schema": {"catalog_name": catalog_name, "schema_name": schema_name},
            "max_results": max_results,
        }
        if page_token:
            body["page_token"] = page_token
        return self._request("POST", "/api/2.0/mlflow/unity-catalog/prompts/search", json=body).json()
