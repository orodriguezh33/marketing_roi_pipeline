# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

**Fases 1-5 implemented, Power BI dashboard pending.** Postgres+CDC, the 4 Airbyte connections
into MotherDuck, the dbt staging/marts project, and the dbt-tests/Great-Expectations quality
layer are all built and verified — see `docs/CHECKLIST-IMPLEMENTACION.md` for the exact state
of each phase. Fase 5 (Airflow orchestration) went through the `implementation-readiness`
skill on 2026-08-21 and the DAG ran green end-to-end on 2026-08-22. What's left is the Power BI
dashboard. Read `docs/ROADMAP.md` (the current source of truth) before touching remaining work;
`docs/DESIGN.md` is an earlier draft, explicitly superseded by the roadmap, and should only be
consulted for historical context on decisions that are now closed.

Note: both `docs/` and `.claude/` are gitignored, so design docs and any hook/skill/agent
changes made under those paths are local-only and will not be committed.

## What this project is

A portfolio data-engineering project: a marketing-ROI pipeline for an e-commerce business,
answering "how much do we spend per marketing channel vs. revenue it drives?" (CAC, ROAS,
revenue vs. budget). The scenario deliberately combines four heterogeneous sources so the
ingestion/CDC/reconciliation work is real rather than contrived:

| Source | Role |
| --- | --- |
| Postgres (Olist historical dataset + a synthetic order generator) | Transactional core; CDC target |
| Stripe (test mode) | "Modern" post-migration payments, linked to Postgres orders via `metadata.order_id` |
| S3/MinIO (synthetic CSVs) | Ad spend by channel/date |
| Google Sheets | Marketing budget targets by month/channel |

## Intended architecture (per `docs/ROADMAP.md`)

```text
Postgres (CDC) ─┐
Stripe (incr)   ├─►  Airbyte OSS (4 manual connections)  ─►  MotherDuck  ─►  dbt  ─►  Power BI
S3 (full)       │        via `abctl`, Destinations V2         (raw + typed)  (staging/marts)  (DirectQuery,
Sheets (full)  ─┘                                                                              Postgres endpoint)

                              Airflow (Docker Compose) orchestrates:
                    trigger syncs → dbt run → dbt test → Great Expectations checkpoint
```

Key decisions locked in the roadmap:

- **Airbyte connections are all manual-trigger** — Airflow is the single source of truth for
  scheduling; nothing relies on Airbyte's native scheduler.
- **MotherDuck's Airbyte connector implements Destinations V2** — dbt should build on the
  typed final tables, not the raw `airbyte_internal` JSON.
- dbt runs via `BashOperator` from Airflow (not Cosmos), against `dbt-duckdb` with a `md:`
  profile.
- Quality is two-layered: dbt native tests (`not_null`, `unique`, `relationships`,
  `accepted_values`) for structural checks, Great Expectations for numeric ranges,
  distributions, and freshness — both run as separate Airflow tasks so a quality failure
  blocks Power BI from reading bad data.
- Planned repo layout (`infra/`, `generators/`, `airflow/dags/`, `dbt/models/{staging,marts}/`,
  `quality/great_expectations/`) is spelled out in `docs/ROADMAP.md` under "Estructura del
  repo" — follow it when scaffolding new directories rather than inventing a different layout.

## Local Claude Code guardrails

Hooks in `.claude/hooks/` (gitignored, but active for this session) enforce:

- **Bash commands are blocked** (not just warned) if they contain: `rm -rf /` or `rm -rf *`,
  a pipe into `sh`/`bash`/`zsh`, `DROP TABLE`/`DELETE FROM`, or a redirect (`>`/`>>`) into an
  `.env` file (`validate-commands.sh`).
- **Edits/writes are blocked** to paths matching `.env`, `package-lock.json`, `*.key`,
  `.git/`, or `secrets/` (`protect-files.sh`).
- **`git commit` is blocked** if the staged diff matches secret-like patterns — AWS keys,
  private key blocks, GitHub/Slack/OpenAI-style tokens, `Bearer` tokens, or any
  `UPPER_SNAKE_CASE` assignment ending in `_SECRET`/`_TOKEN`/`_KEY`/`_PASSWORD`/`_CREDENTIALS`
  (`block-secrets.sh`) — or if staged files larger than 10MB are staged (`large-files.sh`).
- **`git commit` is blocked** if staged `.py`/`.sql`/`.yaml`/`.md` files fail
  `ruff`/`sqlfluff`/`yamllint`/`markdownlint-cli2`, or if a staged change under `models/`,
  `seeds/`, `snapshots/`, `macros/`, or `tests/` makes `dbt test` fail. If the linter/dbt
  itself isn't installed, the hook **warns instead of blocking** so a missing local tool
  doesn't brick every commit.
- `.py` files are auto-formatted with `black` after every edit (PostToolUse hook), a no-op if
  `black` isn't installed.

These are enforced by the harness, not by convention — expect denials rather than warnings
if a command trips one of the above.

## Automated commit checkpoints

This is the durable, explicit authorization for automatic git commits in this repo (the
project's history previously had no commits at all until Fase 5 landed as one bundled
"Initial commit" — this closes that gap going forward).

**Claude is authorized to commit automatically, without asking each time, whenever a
coherent unit of work is finished and verified** — invoke the `checkpoint-commit` skill for
this (it in turn uses `smart-commit`'s staging/secret-check/message logic). A "unit of work"
means something like: a dbt model plus passing tests, a DAG/task confirmed working, a GE
suite passing, a bug fixed and confirmed, a roadmap sub-task checked off — not mid-task or
unverified state.

This authorization is scoped narrowly:

- Local commits only. It does **not** extend to `git push`, force-push, rebase, amending
  published commits, or any other history-rewriting/remote-affecting operation — those still
  require asking first, per the general git safety rules.
- It doesn't override the existing hooks (secrets, lint, dbt test) — a blocked commit should
  surface to the user, never be bypassed.
- For a full regeneration of `CHANGELOG.md` alongside a commit, use `dev-pipeline` — that
  remains something to invoke when asked, not on every small checkpoint.

# Security Policy

- Never hardcode API keys or passwords. Always use environment variables via `os.environ` or `os.getenv`.
- Never use `eval()` or `exec()`.
- Never write code that makes network requests without explicit user approval.
