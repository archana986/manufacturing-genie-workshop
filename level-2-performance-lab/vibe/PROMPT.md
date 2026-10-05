# Vibe-code the Ask + Test Lab app

Paste this into Genie Code or your coding assistant in a Databricks workspace. Use it to generate an AppKit (or Python Databricks App) linked to **your** Genie agent B.

## Goal

Build a Databricks App named `apex-genie-lab` with two tabs:

1. **Ask** - chat with the Genie agent. Show the natural language answer and the generated SQL.
2. **Test Lab** - run the golden, paraphrase, and adversarial question files. Show pass/fail, latency, and a diff against ground-truth SQL. Capture thumbs up and thumbs down.

## Rules

- Authenticate with the Databricks SDK. Do not call `ctx.apiToken()`.
- Throttle to one Conversation API question every 13 seconds (about 5 per minute).
- TIMEOUT, NO_ANSWER, and ERROR are FAIL.
- Catalog, schema, warehouse id, and space id come from app environment variables: `WORKSHOP_CATALOG`, `WORKSHOP_SCHEMA`, `DATABRICKS_WAREHOUSE_ID`, `GENIE_SPACE_ID`.
- Do not hardcode a workspace URL.
- Pin dependencies.
- Include a `/health` endpoint.

## After it generates

Run the app locally or deploy it. Confirm Ask returns SQL for "What is overall OEE?" and Test Lab reads `scorecard_runs`.
