# Level 3: Genie at production scale

Full-day path. Copy **this folder** as the root of your project, then deploy with Databricks Asset Bundles.

## What you get

One bundle for the agent, metric views, gold pipeline, Ask + Test Lab app, jobs, and permissions. GitHub Actions validate pull requests and deploy **dev** on merge. Staging and prod stay manual (`PROMOTION.md`).

## How to run

1. Copy `level-3-production/` to its own repo or use it as the working directory.
2. Set bundle variables in `databricks.yml` for your catalog, schema, warehouse id, and parent path.
3. `databricks bundle validate --strict --target dev`
4. Open a pull request. CI runs validate and payload tests.
5. Merge deploys **dev** only.
6. Follow `PROMOTION.md` for staging and prod.

See `SETUP.md` for auth, OIDC, and known limits.

## Optional: Auto-Optimize

Workbench **Auto-Optimize** is optional. It clones the agent, proposes instruction or example-SQL changes, and promotes a clone only if benchmarks improve on train, validation, and holdout. It needs Managed MLflow Prompt Registry from workspace **Previews** (Beta, not a Public Preview). If that toggle is off, keep the thumbs-down to pull request loop in `RUNBOOK.md`.

IQ Scan and Quick Fix from Level 2 do not require Prompt Registry.

MaxGenie was an earlier Databricks Solutions skill for the same pattern. Databricks archived it. Use Workbench, not a second optimizer.

## Files

| File | Use |
|---|---|
| `databricks.yml` | Bundle and targets |
| `resources/` | Agent, app, jobs, pipeline |
| `src/` | Pipeline, notebooks, governance, app |
| `.github/workflows/` | PR checks and deploy-dev |
| `PROMOTION.md` | Staging and prod steps |
| `RUNBOOK.md` | Operate the agent |
| `SETUP.md` | Install, customize, limits |
