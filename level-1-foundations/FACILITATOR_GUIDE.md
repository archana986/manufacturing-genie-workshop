# Level 1 facilitator guide

2 hour classroom path. Attendees do not need to write Python. You run notebooks on serverless or pre-run 01.

## Timing

| Min | What |
|---|---|
| 0-10 | Prereq notebook. Anyone red stays with you. |
| 10-25 | Notebook 01. Point at the seven tables. |
| 25-45 | Create the agent in the **Genie UI**. Then run notebook 02. |
| 45-65 | Instructions tab. Teach: one example SQL beats ten paragraphs. |
| 65-95 | Benchmarks. Run 10, fix failures, rerun. |
| 95-110 | Blank vs curated plus sneaky questions. |
| 110-120 | Shift-start briefing. Share the agent. Show Genie One. |

## UI click path (create agent)

1. New > Genie > Agent.
2. Title: Apex L1 Curated.
3. Add the seven tables from `<catalog>.<schema>`.
4. Pick the class SQL warehouse.
5. Save. Then let notebook 02 PATCH instructions if you want the API path.

## Shift-start briefing script

Ask, in order:

1. What were the top scrap lines yesterday?
2. What defect codes drove that scrap?
3. Which shift had the most defects?
4. How does that compare to the prior seven days?

Confirm numbers against `quality_metrics_daily` and `production_events`.

## Scoring

TIMEOUT, NO_ANSWER, and ERROR are FAIL. Do not coach attendees to accept a wrong grain.

## Optional take-home

Genie Code skill in `legacy/skill/` if you still want a prompt pack. Level 2 vibe prompt is the supported path.
