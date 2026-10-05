# Level 1: Genie Foundations

2 hour path for first-time Genie authors.

## What you get

A curated Apex Precision Manufacturing agent on seven tables, 10 benchmarks, and a blank vs curated comparison.

## How to run

1. Run `shared/00_config` and `shared/00_prereq_check`.
2. Run `01_config_and_data` on serverless.
3. Create the agent in the Genie UI (see `FACILITATOR_GUIDE.md`), then run `02_create_agent`.
4. Run `03_benchmarks`. Use the UI Benchmarks tab if eval-runs is off.
5. Run `04_basic_tests`.

Set widgets to your catalog, schema, and warehouse id. Do not commit those values.

## Files

| File | Use |
|---|---|
| `01_config_and_data` | Load seven tables |
| `02_create_agent` | Blank and curated agents |
| `03_benchmarks` | 10 ground-truth questions |
| `04_basic_tests` | A/B and sneaky questions |
| `templates/` | Catalog-parameterized JSON |
| `FACILITATOR_GUIDE.md` | Talk track and click path |
