# Genie Workbench lab (Level 2)

Use Workbench for **IQ Scan** and **Quick Fix** only in this level.

## You need

- Claude Sonnet on Foundation Model APIs
- CAN MANAGE on the two Level 2 agents
- A deployed Workbench app (your facilitator may host one)

## Steps

1. Open Workbench and select Apex L2 A, then Apex L2 B.
2. Run **IQ Scan**. Read all 12 checks.
3. Apply **Quick Fix** on failing checks. Rescan.
4. Rerun the scorecard notebook. Compare IQ score to measured accuracy.

## What this level does not include

**Auto-Optimize** is an optional Level 3 module. It clones the agent, proposes changes, and keeps them only if benchmarks improve on a holdout set. It needs Managed MLflow Prompt Registry (workspace Previews, Beta). If that preview is off, skip it. You still have IQ Scan, Quick Fix, and the Level 3 pull request loop.

MaxGenie was an earlier Databricks Solutions optimizer with the same clone-and-benchmark idea. Databricks archived it and folded that workflow into Workbench. Do not install MaxGenie for this lab.
