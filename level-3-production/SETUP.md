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
3. Copy Level 2 metric view YAML into `src/metric_views/` if this folder is used alone.
4. After you curate an agent in a workspace, run `databricks bundle generate genie-space` and commit the generated `.geniespace.json`.
5. `databricks bundle validate --strict --target dev`
6. `databricks bundle deploy -t dev`

## GitHub Actions (dev only)

Workflows use Entra ID workload identity federation. Set GitHub environment secrets for Azure client id, tenant id, and subscription id. Do not store a PAT.

`pr.yml` runs validate and payload tests. `deploy-dev.yml` deploys the `dev` target after merge.

## Known limitations

- Bundle variables do not rewrite strings inside `.geniespace.json`. Generate per target or run a replace job before deploy.
- Metric view materialization and entity matching cannot be used with row filters, column masks, or ABAC.
- `genie-iq-score-lite` is not on PyPI. IQ Scan runs in Workbench, or you vendor a scorer.
- Auto-Optimize needs Prompt Registry (workspace Beta). Skip it if that preview is off. MaxGenie is archived; use Workbench instead.
- Service principal Genie usage is billed. Keep CI eval-runs small.
- Staging and prod are not deployed by Actions. Use `PROMOTION.md`.
- Apps need `GENIE_SPACE_ID` after the first agent deploy.
