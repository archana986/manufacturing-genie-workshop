"""Locate the workshop repo root so notebooks can import shared.config."""

from __future__ import annotations

import sys
from pathlib import Path


def repo_root() -> Path:
    try:
        from pyspark.dbutils import DBUtils
        from pyspark.sql import SparkSession

        spark = SparkSession.getActiveSession()
        if spark is not None:
            raw = str(DBUtils(spark).widgets.get("repo_root") or "").strip()
            if raw:
                path = Path(raw)
                if (path / "shared" / "config.py").exists():
                    return path
    except Exception:
        pass
    here = Path.cwd().resolve()
    for path in [here, *here.parents]:
        if (path / "shared" / "config.py").exists():
            return path
    raise FileNotFoundError(
        "Could not find shared/config.py. Set the repo_root widget to the workspace folder that contains shared/."
    )


def on_sys_path() -> Path:
    root = repo_root()
    text = str(root)
    if text not in sys.path:
        sys.path.insert(0, text)
    return root
