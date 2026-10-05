# Apex Genie Lab

Databricks App with two tabs:

- **Ask:** send a question to your Genie agent and show the reply
- **Test Lab:** read `scorecard_runs` and show pass/fail plus latency

Throttle: one question every 13 seconds (about 5 questions per minute).

Set environment variables in the app resource: `DATABRICKS_WAREHOUSE_ID`, `GENIE_SPACE_ID`, `WORKSHOP_CATALOG`, `WORKSHOP_SCHEMA`.
