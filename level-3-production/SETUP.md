# SETUP

How to use the Level 3 bundle for your own Apex-style Genie agent.

## Prerequisites

- Databricks CLI 1.17 or later
- `databricks auth login --profile YOUR_PROFILE --host https://<your-workspace>.azuredatabricks.net`
- Unity Catalog catalog you can write
- A serverless or Pro SQL warehouse you can use
- A GitHub repo if you want the Actions workflows

## Customize

1. Copy this folder (`level-3-production/`) so `databricks.yml` is at the project root.
2. Replace `YOUR_CATALOG`, `YOUR_SCHEMA_DEV`, `YOUR_WAREHOUSE_ID`, and `YOUR_USER` in `databricks.yml`.
3. Set `workshop_root` to the workspace folder that contains `shared/` (the imported three-level workshop). The metric-views and accuracy-alert jobs need it.
4. Replace `YOUR_CATALOG.YOUR_SCHEMA` in `src/genie/apex_l2b.geniespace.json` with the same catalog and schema. Table identifiers must stay sorted. Instruction ids must stay lowercase 32-hex UUIDs with no hyphens.
5. Copy Level 2 metric view YAML into `src/metric_views/` if this folder is used alone.
6. Deploy in this order: pipeline `apex_gold`, job `deploy_metric_views`, then the Genie space. The space cannot be created until the metric views exist.
7. `databricks bundle validate --strict --target dev`
8. `databricks bundle deploy -t dev --var catalog=... --var schema=... --var warehouse_id=... --var parent_path=... --var workshop_root=...`

## GitHub Actions (dev only)

Workflows use Entra ID workload identity federation. Set GitHub environment secrets for Azure client id, tenant id, and subscription id. Do not store a PAT.

`pr.yml` runs validate and payload tests. `deploy-dev.yml` deploys the `dev` target after merge.

## Known limitations

- Resource YAML paths are relative to `resources/`, so notebooks, pipeline files, the app, and the Genie export use `../src/...`.
- Bundle variables do not rewrite strings inside `.geniespace.json`. Replace `YOUR_CATALOG.YOUR_SCHEMA` per target before deploy. Table identifiers must be sorted. Instruction and benchmark ids must be lowercase 32-hex UUIDs with no hyphens.
- The gold pipeline now writes `fct_line_shift` and `maintenance_work_orders`. Deploy the Genie space only after `deploy_metric_views` succeeds.
- Metric view materialization and entity matching cannot be used with row filters, column masks, or ABAC.
- `genie-iq-score-lite` is not on PyPI. IQ Scan runs in Workbench, or you vendor a scorer.
- Auto-Optimize needs Prompt Registry (workspace Beta). Skip it if that preview is off. MaxGenie is archived; use Workbench instead.
- Service principal Genie usage is billed. Keep CI eval-runs small.
- Staging and prod are not deployed by Actions. Use `PROMOTION.md`.
- Apps need `GENIE_SPACE_ID` after the first agent deploy.
