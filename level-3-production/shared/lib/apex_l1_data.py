"""Deterministic Apex Precision Manufacturing seed for Level 1.

Six plants, 24 lines, 400 operators, about 50,000 events.
Dates roll so the last day is yesterday.
Units use unit_serial.
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta
from typing import Any

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    BooleanType,
    DateType,
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from shared.config import WorkshopConfig

FIRST_NAMES = [
    "James", "Maria", "Robert", "Linda", "David", "Sarah", "Carlos", "Jennifer", "Michael", "Patricia",
    "William", "Elizabeth", "Richard", "Barbara", "Joseph", "Susan", "Thomas", "Jessica", "Daniel", "Karen",
]
LAST_NAMES = [
    "Nguyen", "Patel", "Garcia", "Kim", "Johnson", "Chen", "Williams", "Singh", "Martinez", "Brown",
    "Lee", "Anderson", "Taylor", "Moore", "Jackson", "White", "Harris", "Clark", "Lewis", "Walker",
]
SHIFTS = ["Morning", "Afternoon", "Night"]
EVENT_TYPES = ["unit_produced", "defect_detected", "scrap", "rework_completed", "downtime"]
DEFECT_CODES = [
    "DEF-WELD-01", "DEF-WELD-02", "DEF-PAINT-01", "DEF-FIT-01", "DEF-ELEC-01", "DEF-STMP-01",
]
PRODUCT_TYPES = {
    "automotive_components": ["Axle housing", "Brake caliper", "Steering knuckle"],
    "industrial_pumps": ["Centrifugal pump", "Diaphragm pump", "Gear pump"],
    "electronics_assembly": ["Control board", "Sensor module", "Power inverter"],
}

PLANTS = [
    ("PLT-01", "Apex Columbus", "Columbus", "OH", "industrial_pumps", 1200),
    ("PLT-02", "Apex Austin", "Austin", "TX", "electronics_assembly", 1400),
    ("PLT-03", "Apex Nashville", "Nashville", "TN", "automotive_components", 1600),
    ("PLT-04", "Apex Raleigh", "Raleigh", "NC", "electronics_assembly", 1100),
    ("PLT-05", "Apex Indianapolis", "Indianapolis", "IN", "industrial_pumps", 1000),
    ("PLT-06", "Apex Atlanta", "Atlanta", "GA", "automotive_components", 1500),
]


def _h(seed: str) -> int:
    return int(hashlib.sha256(seed.encode()).hexdigest()[:12], 16)


def _pick(seed: str, items: list[Any]) -> Any:
    return items[_h(seed) % len(items)]


def date_window() -> tuple[date, date]:
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=364)
    return start, end


def write_l1_tables(spark: SparkSession, cfg: WorkshopConfig) -> dict[str, int]:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {cfg.fqn}")
    spark.sql(f"CREATE VOLUME IF NOT EXISTS {cfg.fqn}.{cfg.volume}")
    start, end = date_window()
    days = (end - start).days + 1

    plants = [
        (pid, name, city, state, industry, float(capacity), start)
        for pid, name, city, state, industry, capacity in PLANTS
    ]
    plants_df = spark.createDataFrame(
        plants,
        schema=StructType(
            [
                StructField("plant_id", StringType(), False),
                StructField("plant_name", StringType(), False),
                StructField("city", StringType(), False),
                StructField("state", StringType(), False),
                StructField("industry", StringType(), False),
                StructField("capacity_units_per_hour", DoubleType(), False),
                StructField("opened_date", DateType(), False),
            ]
        ),
    )

    lines = []
    for pid, name, city, state, industry, capacity in PLANTS:
        products = PRODUCT_TYPES[industry]
        for i in range(4):
            line_id = f"LN-{pid[-2:]}-{i+1:02d}"
            status = "Maintenance" if _h(line_id) % 11 == 0 else "Active"
            lines.append(
                (
                    line_id,
                    f"{name} Line {i+1}",
                    pid,
                    products[i % len(products)],
                    industry,
                    status,
                    start + timedelta(days=_h(line_id) % 30),
                )
            )
    lines_df = spark.createDataFrame(
        lines,
        schema=StructType(
            [
                StructField("line_id", StringType(), False),
                StructField("line_name", StringType(), False),
                StructField("plant_id", StringType(), False),
                StructField("product_type", StringType(), False),
                StructField("industry", StringType(), False),
                StructField("status", StringType(), False),
                StructField("install_date", DateType(), False),
            ]
        ),
    )

    operators = []
    for n in range(400):
        oid = f"OP-{n+1:04d}"
        plant = PLANTS[n % 6][0]
        operators.append(
            (
                oid,
                _pick(oid + "f", FIRST_NAMES),
                _pick(oid + "l", LAST_NAMES),
                plant,
                SHIFTS[n % 3],
                (n % 12) + 1,
            )
        )
    operators_df = spark.createDataFrame(
        operators,
        schema=StructType(
            [
                StructField("operator_id", StringType(), False),
                StructField("first_name", StringType(), False),
                StructField("last_name", StringType(), False),
                StructField("home_plant_id", StringType(), False),
                StructField("shift", StringType(), False),
                StructField("tenure_years", LongType(), False),
            ]
        ),
    )

    line_ids = [row[0] for row in lines]
    line_plant = {row[0]: row[2] for row in lines}
    op_ids = [row[0] for row in operators]
    events = []
    for i in range(50_000):
        seed = f"evt-{i}"
        line_id = line_ids[_h(seed + "l") % len(line_ids)]
        plant_id = line_plant[line_id]
        op = op_ids[_h(seed + "o") % len(op_ids)]
        day = start + timedelta(days=_h(seed + "d") % days)
        hour = _h(seed + "h") % 24
        minute = _h(seed + "m") % 60
        ts = datetime(day.year, day.month, day.day, hour, minute)
        roll = _h(seed + "r") % 100
        if roll < 72:
            etype = "unit_produced"
        elif roll < 84:
            etype = "defect_detected"
        elif roll < 90:
            etype = "scrap"
        elif roll < 96:
            etype = "rework_completed"
        else:
            etype = "downtime"
        defect = _pick(seed, DEFECT_CODES) if etype in {"defect_detected", "scrap"} else None
        serial = f"APX{day:%y%m%d}{_h(seed) % 10_000_000:07d}"
        events.append(
            (
                f"EV-{i+1:06d}",
                plant_id,
                line_id,
                op,
                etype,
                defect,
                serial,
                day,
                ts,
                float((_h(seed + "dt") % 40) + 5) if etype == "downtime" else None,
            )
        )
    events_df = spark.createDataFrame(
        events,
        schema=StructType(
            [
                StructField("event_id", StringType(), False),
                StructField("plant_id", StringType(), False),
                StructField("production_line_id", StringType(), False),
                StructField("operator_id", StringType(), False),
                StructField("event_type", StringType(), False),
                StructField("defect_code", StringType(), True),
                StructField("unit_serial", StringType(), False),
                StructField("event_date", DateType(), False),
                StructField("event_ts", TimestampType(), False),
                StructField("downtime_minutes", DoubleType(), True),
            ]
        ),
    )

    quality = []
    for line in lines:
        line_id, line_name, plant_id, product, industry, status, _install = line
        for d_off in range(days):
            d = start + timedelta(days=d_off)
            seed = f"{line_id}-{d.isoformat()}"
            units = 400 + (_h(seed + "u") % 250)
            defects = _h(seed + "x") % 18
            scrap = _h(seed + "s") % 8
            downtime = float(_h(seed + "n") % 90)
            oee = round(0.62 + (_h(seed + "o") % 35) / 100.0, 4)
            fpy = round(0.88 + (_h(seed + "f") % 12) / 100.0, 4)
            quality.append((plant_id, line_id, d, units, defects, scrap, downtime, oee, fpy))
    quality_df = spark.createDataFrame(
        quality,
        schema=StructType(
            [
                StructField("plant_id", StringType(), False),
                StructField("production_line_id", StringType(), False),
                StructField("date", DateType(), False),
                StructField("units_produced", LongType(), False),
                StructField("defects_found", LongType(), False),
                StructField("scrap_count", LongType(), False),
                StructField("downtime_minutes", DoubleType(), False),
                StructField("oee_score", DoubleType(), False),
                StructField("first_pass_yield", DoubleType(), False),
            ]
        ),
    )

    incidents = []
    for i in range(40):
        seed = f"inc-{i}"
        line = lines[_h(seed) % len(lines)]
        day = start + timedelta(days=_h(seed + "d") % days)
        sev = _pick(seed, ["Minor", "Major", "Critical"])
        incidents.append(
            (
                f"SI-{i+1:03d}",
                day,
                line[2],
                line[0],
                sev,
                f"{sev} near-miss on {line[1]}",
                _pick(seed, ["Guard missing", "Lockout skipped", "Wet floor", "Tool wear"]),
                "Retrain and inspect",
            )
        )
    incidents_df = spark.createDataFrame(
        incidents,
        schema=StructType(
            [
                StructField("incident_id", StringType(), False),
                StructField("incident_date", DateType(), False),
                StructField("plant_id", StringType(), False),
                StructField("production_line_id", StringType(), False),
                StructField("severity", StringType(), False),
                StructField("description", StringType(), False),
                StructField("root_cause", StringType(), False),
                StructField("corrective_action", StringType(), False),
            ]
        ),
    )

    feedback = []
    for i in range(100):
        seed = f"fb-{i}"
        line = lines[_h(seed) % len(lines)]
        op = operators[_h(seed + "o") % len(operators)]
        day = start + timedelta(days=_h(seed + "d") % days)
        ok = bool(_h(seed) % 5)
        feedback.append(
            (
                f"FB-{i+1:03d}",
                day,
                line[0],
                op[0],
                ok,
                _pick(seed, ["Vibration", "Heat", "Noise", "Cycle time drift", "Sensor lag"]),
                f"Operator note {i+1}",
            )
        )
    feedback_df = spark.createDataFrame(
        feedback,
        schema=StructType(
            [
                StructField("feedback_id", StringType(), False),
                StructField("feedback_date", DateType(), False),
                StructField("production_line_id", StringType(), False),
                StructField("operator_id", StringType(), False),
                StructField("equipment_ok", BooleanType(), False),
                StructField("symptom", StringType(), False),
                StructField("notes", StringType(), False),
            ]
        ),
    )

    tables = {
        "plants": plants_df,
        "production_lines": lines_df,
        "operators": operators_df,
        "production_events": events_df,
        "quality_metrics_daily": quality_df,
        "safety_incidents": incidents_df,
        "equipment_feedback": feedback_df,
    }
    counts: dict[str, int] = {}
    for name, df in tables.items():
        path = f"{cfg.volume_path}/{name}"
        df.write.mode("overwrite").parquet(path)
        (
            spark.read.parquet(path)
            .write.mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(cfg.table(name))
        )
        counts[name] = spark.table(cfg.table(name)).count()
    _apply_comments_and_keys(spark, cfg)
    return counts


def _apply_comments_and_keys(spark: SparkSession, cfg: WorkshopConfig) -> None:
    spark.sql(f"COMMENT ON TABLE {cfg.table('plants')} IS 'Apex plants. Six sites across automotive components, industrial pumps, and electronics assembly.'")
    spark.sql(f"COMMENT ON TABLE {cfg.table('production_lines')} IS 'Four lines per plant. status is a static Active or Maintenance flag, not a time series.'")
    spark.sql(f"COMMENT ON TABLE {cfg.table('operators')} IS 'Operators with home plant and shift. Shift is Morning, Afternoon, or Night.'")
    spark.sql(f"COMMENT ON TABLE {cfg.table('production_events')} IS 'Event grain production log. unit_serial is a unit traceability id.'")
    spark.sql(f"COMMENT ON TABLE {cfg.table('quality_metrics_daily')} IS 'Daily line metrics. oee_score and first_pass_yield are 0 to 1. Multiply by 100 for percent.'")
    spark.sql(f"COMMENT ON TABLE {cfg.table('safety_incidents')} IS 'Safety incidents with severity Critical, Major, or Minor.'")
    spark.sql(f"COMMENT ON TABLE {cfg.table('equipment_feedback')} IS 'Operator equipment notes.'")
    statements = [
        f"ALTER TABLE {cfg.table('plants')} ALTER COLUMN plant_id SET NOT NULL",
        f"ALTER TABLE {cfg.table('production_lines')} ALTER COLUMN line_id SET NOT NULL",
        f"ALTER TABLE {cfg.table('operators')} ALTER COLUMN operator_id SET NOT NULL",
        f"ALTER TABLE {cfg.table('production_events')} ALTER COLUMN event_id SET NOT NULL",
        f"ALTER TABLE {cfg.table('plants')} DROP CONSTRAINT IF EXISTS plants_pk",
        f"ALTER TABLE {cfg.table('production_lines')} DROP CONSTRAINT IF EXISTS lines_pk",
        f"ALTER TABLE {cfg.table('operators')} DROP CONSTRAINT IF EXISTS operators_pk",
        f"ALTER TABLE {cfg.table('production_events')} DROP CONSTRAINT IF EXISTS events_pk",
        f"ALTER TABLE {cfg.table('plants')} ADD CONSTRAINT plants_pk PRIMARY KEY (plant_id)",
        f"ALTER TABLE {cfg.table('production_lines')} ADD CONSTRAINT lines_pk PRIMARY KEY (line_id)",
        f"ALTER TABLE {cfg.table('operators')} ADD CONSTRAINT operators_pk PRIMARY KEY (operator_id)",
        f"ALTER TABLE {cfg.table('production_events')} ADD CONSTRAINT events_pk PRIMARY KEY (event_id)",
        f"ALTER TABLE {cfg.table('production_lines')} DROP CONSTRAINT IF EXISTS lines_plant_fk",
        f"ALTER TABLE {cfg.table('production_lines')} ADD CONSTRAINT lines_plant_fk FOREIGN KEY (plant_id) REFERENCES {cfg.table('plants')}(plant_id)",
        f"ALTER TABLE {cfg.table('production_events')} DROP CONSTRAINT IF EXISTS events_line_fk",
        f"ALTER TABLE {cfg.table('production_events')} ADD CONSTRAINT events_line_fk FOREIGN KEY (production_line_id) REFERENCES {cfg.table('production_lines')}(line_id)",
    ]
    for sql in statements:
        try:
            spark.sql(sql)
        except Exception as exc:
            print("constraint skipped:", sql.split(" ADD ", 1)[0][-40:], type(exc).__name__)
