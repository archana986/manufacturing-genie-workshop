"""Workshop config with fail-fast validation.

Catalog, schema, and warehouse stay as widgets or environment variables.
Do not hardcode workspace hostnames, IDs, or emails.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

_PLACEHOLDERS = {
    "",
    "YOUR_CATALOG",
    "YOUR_SCHEMA",
    "YOUR_WAREHOUSE_ID",
    "<catalog>",
    "<schema>",
}


class ConfigError(ValueError):
    """Raised when workshop config is missing or still a placeholder."""


def _read_widget(name: str, default: str = "") -> str:
    try:
        from pyspark.dbutils import DBUtils  # type: ignore
        from pyspark.sql import SparkSession

        spark = SparkSession.getActiveSession()
        if spark is None:
            return default
        value = DBUtils(spark).widgets.get(name)
        return str(value).strip() if value is not None else default
    except Exception:
        try:
            import IPython

            ip = IPython.get_ipython()
            if ip is not None and "dbutils" in ip.user_ns:
                value = ip.user_ns["dbutils"].widgets.get(name)
                return str(value).strip() if value is not None else default
        except Exception:
            pass
    return default


def _first(*values: str) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text and text not in _PLACEHOLDERS:
            return text
    return ""


def _require(name: str, value: str) -> str:
    if not value or value in _PLACEHOLDERS:
        raise ConfigError(
            f"{name} is not set. Open shared/00_config and set the widget, "
            f"or export {name} before you run."
        )
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise ConfigError(
            f"{name} must be a Unity Catalog identifier (letters, digits, underscore). Got {value!r}."
        )
    return value


@dataclass(frozen=True)
class WorkshopConfig:
    catalog: str
    schema: str
    warehouse_id: str
    volume: str = "raw_data"
    company: str = "Apex Precision Manufacturing"
    telemetry_rows: int = 10_000_000

    @property
    def fqn(self) -> str:
        return f"{self.catalog}.{self.schema}"

    @property
    def volume_path(self) -> str:
        return f"/Volumes/{self.catalog}/{self.schema}/{self.volume}"

    def table(self, name: str) -> str:
        return f"{self.fqn}.{name}"


def load_config() -> WorkshopConfig:
    catalog = _first(
        os.environ.get("WORKSHOP_CATALOG", ""),
        _read_widget("catalog"),
    )
    schema = _first(
        os.environ.get("WORKSHOP_SCHEMA", ""),
        _read_widget("schema"),
    )
    warehouse_id = _first(
        os.environ.get("WORKSHOP_WAREHOUSE_ID", ""),
        _read_widget("warehouse_id"),
    )
    catalog = _require("WORKSHOP_CATALOG / catalog", catalog)
    schema = _require("WORKSHOP_SCHEMA / schema", schema)
    if not warehouse_id or warehouse_id in _PLACEHOLDERS:
        raise ConfigError(
            "warehouse_id is not set. Pass a serverless or Pro SQL warehouse id "
            "via the warehouse_id widget or WORKSHOP_WAREHOUSE_ID."
        )
    telemetry = _first(
        os.environ.get("WORKSHOP_TELEMETRY_ROWS", ""),
        _read_widget("telemetry_rows"),
        "10000000",
    )
    try:
        telemetry_rows = int(telemetry)
    except ValueError as exc:
        raise ConfigError("WORKSHOP_TELEMETRY_ROWS must be an integer") from exc
    if telemetry_rows not in (10_000_000, 50_000_000):
        raise ConfigError("WORKSHOP_TELEMETRY_ROWS must be 10000000 or 50000000")
    return WorkshopConfig(
        catalog=catalog,
        schema=schema,
        warehouse_id=warehouse_id,
        telemetry_rows=telemetry_rows,
    )
