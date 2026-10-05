# Level 2: Genie Performance Lab

4 hour path for data engineers and SAs.

## What you get

Complex Apex tables, three metric views, an A vs B scorecard (accuracy and p50/p95), a Workbench IQ Scan lab, and a reference Ask + Test Lab app.

## How to run

1. Point widgets at your Level 2 schema. Default telemetry is 10 million rows.
2. Run `10_complex_data` through `14_performance_tuning` on serverless.
3. Follow `workbench/README.md` for IQ Scan and Quick Fix.
4. Deploy `app/` or vibe-code from `vibe/PROMPT.md`.

Set `telemetry_rows` to `50000000` only if you have time and a Medium warehouse.

## Auto-Optimize

Not in this level. IQ Scan and Quick Fix are required. Auto-Optimize is an optional Level 3 module.

## Files

| File | Use |
|---|---|
| `10_complex_data` | Telemetry, SCD2, BOM, work orders |
| `11_metric_views` | OEE, FPY, MTBF YAML 1.1 |
| `12_agent_v2` | Agent A tables vs agent B metric views |
| `13_accuracy_and_latency` | 25-question scorecard |
| `14_performance_tuning` | Clustering and warehouse levers |
| `metric_views/` | YAML sources |
| `benchmarks/` | Golden, paraphrase, adversarial |
| `app/` | Reference app |
| `vibe/PROMPT.md` | Generate your own app |
