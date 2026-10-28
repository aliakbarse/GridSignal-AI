# GridSignal AI — Project Memory & Continuity Notes

> **Purpose:** This file is the durable handover note for future ChatGPT sessions. Read it before proposing new work.
> **Last updated:** 2026-10-25
> **Rule:** Treat the code and data in this repository as the source of truth. This note summarizes the checkpoint known at the date above; update it as the project changes.

## 1. Project purpose

GridSignal AI is a portfolio project exploring Germany's electricity market, with a focus on day-ahead electricity prices, negative-price hours, and selected renewable generation. The current foundation is a reproducible Python data-analysis pipeline using pandas and plotting/testing tools.

The goal is not merely to make code run. The user wants to understand the reasoning, own the implementation, and eventually build toward a credible AI-enabled project grounded in reliable analysis and evidence.

## 2. How to mentor the user

The user explicitly prefers a **mentorship-first, beginner-friendly approach**:

- Work **one step at a time**; do not overwhelm them with a long task list.
- Explain **why** a step matters before asking them to do it.
- Explain why errors happen and how to diagnose them.
- Discuss alternatives when they are genuinely useful, without adding unnecessary complexity.
- Help the user understand and own the code: **AI-enabled, not AI-dependent**.
- Before significant actions, offer a brief optional mini Q&A when it helps learning, but do not derail progress.
- Check the existing project files and documentation before asking the user to repeat diagnostics or completed work.
- Distinguish facts supported by code/data from hypotheses and recommendations.
- Do not claim that correlation proves causation.
- At the end of each substantial session, prepare a concise session update that the user can save to this file or the session log.

## 3. Current project structure and implemented foundation

The uploaded project archive contained source code, data, docs, charts/outputs, and tests. Key areas include:

- `src/gridsignal/` — Python modules for data inspection, cleaning, validation, combining, and analysis.
- `data/` — raw and processed SMARD CSV data and derived outputs.
- `docs/findings.md` — documented analytical findings.
- `README.md` — project overview, setup, findings, and future roadmap.
- Automated tests — the reviewed archive contains 9 tests.

The pipeline uses UTC timestamps for matching/combining hourly records and `Europe/Berlin` local time for analyses where local calendar months and hour-of-day matter.

### Current script checkpoint

`src/gridsignal/analyze_prices.py` was run successfully from the project root:

```powershell
python .\src\gridsignal\analyze_prices.py
```

It reads:

`data/processed/germany_market_combined_2024_2025.csv`

and writes:

`data/processed/monthly_renewables_price_analysis.csv`

It reports monthly observed hours, negative-price hours and percentages, average prices, and comparisons of average wind, solar, and selected-renewables generation during negative-price versus nonnegative-price hours. It also prints absolute and relative differences. Months with no negative-price hours have unavailable category comparisons.

The latest terminal output shared in the conversation showed 2024–2025 monthly statistics and successful output generation. It showed, among other values, that June 2025 had 141 negative-price hours out of 720 observed hours (19.58%). The monthly comparison script's result is descriptive and does not establish causation.

## 4. Dataset checkpoint and data caveats

The reviewed project documentation describes 17,541 matched hourly records across 2024–2025: 8,784 for 2024 and 8,757 for 2025. The source dataset ends three hourly records short of a full 2025 calendar year; this is documented as a coverage limitation, not something to silently fill or treat as confirmed missing data without investigation.

Use the source files and scripts to verify these counts if data changes. Do not rerun already documented checks just for the sake of repeating them.

Before publishing claims, verify source definitions and units for the SMARD generation series and be precise about whether values refer to generation, installed capacity, or another measure.

## 5. Findings documented in the current README/docs

The uploaded project documentation records these descriptive findings:

1. Negative-price hours increased from 457 in 2024 to 573 in 2025 (+25.4%).
2. Negative-price frequency peaked at 19.58% of observed hours in June 2025.
3. Solar generation was higher on average during negative-price hours.
4. Most negative prices were relatively mild, although some very low prices occurred.
5. In the 13 monthly comparisons meeting the documented threshold of at least 30 negative-price hours, average solar generation was higher during negative-price hours.
6. Negative-price frequency was highest around midday, with the documented hourly peak at 14:00 in 2024 and 13:00 in 2025 (German local time).

Treat these as findings documented in the current project files, not universal causal conclusions. Re-check the source analysis and exact definitions before changing or publishing them.

## 6. Known limitations / questions to handle carefully

- These analyses are descriptive: association is not proof of causation.
- Monthly group comparisons can mix together time-of-day and seasonal effects. Demand, imports/exports, conventional generation, storage, and other market conditions may also matter.
- The 2025 dataset has three fewer hourly observations than a complete calendar year, according to current documentation.
- The solar comparison uses a threshold of at least 30 negative-price hours for one documented consistency finding; retain that qualification when describing it.
- Avoid silently filling missing observations or assuming why they are absent.
- Check that chart labels, units, local-time handling, and source definitions match the underlying data.

## 7. General roadmap (planned, not all implemented)

The README documents future directions including:

1. Expand and strengthen the analytical work; make assumptions and limitations explicit.
2. Consider a baseline forecasting task only after defining the target, baseline, split strategy, and evaluation metrics.
3. Add evidence retrieval so explanations can point back to trustworthy data or documentation.
4. Explore LangGraph orchestration only when a clear workflow needs it.
5. Add evaluation, an API, and observability as justified by the design.

Do not assume these future features already exist. Prefer the simplest useful next step over adding AI frameworks prematurely.

## 8. Working protocol for future sessions

At the start of a new session:

1. Read this file, `README.md`, `docs/findings.md`, and relevant source code before suggesting work.
2. Ask the user for new terminal output or files only when needed; do not ask them to repeat completed diagnostics.
3. State the current checkpoint briefly.
4. Explain the purpose of the single next step and wait for the user to complete it before moving on.

At the end of a substantial session:

1. Record what changed, why it changed, and how it was verified.
2. Record new findings, decisions, caveats, and unresolved questions.
3. Update the current checkpoint and next step.
4. Give the user the complete updated file or updated project ZIP, and explain how to replace/copy it into their local project.
5. Never say a local file has been updated unless the user has actually applied the update or a connected tool has modified that local file.

## 9. Session log

Append one dated entry at the end of each substantial session. Keep entries concise and specific.

### 2026-10-25 — Recovered project context and backup plan

- The user uploaded `02_GridSignal_AI.zip` so the project state could be reconstructed after accidental deletion of the prior ChatGPT conversation.
- Reviewed the project inventory and documentation; identified the existing analysis pipeline, outputs, tests, and documented findings.
- Confirmed from the user's terminal output that `src/gridsignal/analyze_prices.py` ran successfully and wrote `data/processed/monthly_renewables_price_analysis.csv`.
- Discussed preserving continuity outside ChatGPT with a project memory file, Git, chat archiving, and periodic data export.
- Agreed on the idea of maintaining a reusable project/session backup inside `02_GridSignal_AI`.
- **Next step:** copy this `docs/PROJECT_MEMORY.md` into the local project and commit it if the project uses Git. Continue by choosing one evidence-based analytical question; do not repeat the completed timestamp-coverage diagnostic without a reason.
