# Promotion (staging and prod)

GitHub Actions deploys **dev** only. Staging and prod are manual, same gates, different schema (or workspace).

## Pre-flight

1. `databricks bundle validate --strict --target staging` (or `prod`)
2. Run payload tests: `python tests/test_payload_lint.py`
3. IQ Scan floor in Workbench (example: 10 of 12). Record the score.
4. Confirm row filters and masks still match `src/governance/`.
5. Confirm Auto-Optimize is **off** unless Prompt Registry is on and the CoE accepted Beta.

## Deploy

```bash
databricks bundle deploy -t staging
```

or

```bash
databricks bundle deploy -t prod
```

Run as the CI service principal, not a personal user, when this is a customer CoE.

## Post-deploy gates

1. Eval-run or Conversation API suite. Threshold: 95% pass. TIMEOUT / NO_ANSWER / ERROR = FAIL.
2. Optional MLflow GenAI judges for Agent mode answers.
3. Hit the app `/health` endpoint.
4. Record the bundle revision in your change log.

## Rollback

Deploy the previous revision of this bundle. Restore the previous `.geniespace.json` if the agent file changed.

## Separate workspaces

If staging or prod is another workspace, change `databricks.yml` target `workspace.host` to `https://<your-workspace>.azuredatabricks.net` and authenticate with a profile for that host. Schemas stay variables.
