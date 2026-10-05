# RUNBOOK

Operate the Apex Genie agent after the first deploy.

## Deploy

```bash
databricks bundle validate --strict --target dev
databricks bundle deploy -t dev
```

Staging and prod: `PROMOTION.md`.

## Rollback

Redeploy the previous bundle revision. Restore the previous `.geniespace.json` if instructions changed.

## Rotate the service principal

1. Create a new Entra app registration with federated credentials for GitHub.
2. Grant USE CATALOG / USE SCHEMA / CREATE TABLE on the workshop schemas only.
3. Grant CAN_MANAGE on the Genie agent.
4. Point GitHub environment variables at the new client id.
5. Disable the old principal.

## Onboard a new plant

1. Insert the plant and lines in gold.
2. Add the plant group used by `src/governance/row_filter.sql`.
3. Add sample questions for the new plant name.
4. Open a pull request. Do not PATCH prod by hand.

## Add a benchmark

1. Add the question and ground-truth SQL to the serialized agent file.
2. Run it in the UI. TIMEOUT, NO_ANSWER, and ERROR are FAIL.
3. Open a pull request. CI eval-run must stay above the threshold in `tests/test_benchmarks_gate.py`.

## Incident triage

1. Check `src/monitoring/genie_audit.sql` on `system.access.audit` (`aibiGenie`).
2. Check warehouse health and 429s (5 questions per minute on the free Conversation API tier).
3. If thumbs-down spikes, add candidates to the review queue. Humans approve. Nothing auto-pushes to prod.

## Optional Auto-Optimize

If Prompt Registry is on, you may run Workbench Auto-Optimize against **staging** with train / validation / holdout and rollback. Do not enable it on prod as a required control. If the preview is off, use this runbook's pull request loop.

MaxGenie is archived. Do not install it as a second optimizer.
