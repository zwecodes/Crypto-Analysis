# Project Roadmap

3-month (12-week) development plan across 4 phases/sprints for `CSC480` (Software Engineering Final Project), culminating in the **November 27, 2026** final report submission and **December 1, 2026** project demo.

## Live Deployment & Links

- **Frontend:** https://crypto-analysis-ten.vercel.app (React / Vite on Vercel)
- **Backend API:** https://crypto-analysis-x1y8.onrender.com (FastAPI on Render)
- **Auth & Database:** Supabase (PostgreSQL + Supabase Auth)
- **Task Tracking:** [GitHub Project Board](https://github.com/users/zwecodes/projects/1)

## Product Scope

**In scope:**
- Bitcoin-only trading analysis platform (educational simulation; does not execute real trades)
- Sign up / login / session management (Supabase Auth)
- Live BTC price chart with technical indicators (RSI, MACD & signal line, SMA 20, SMA 50)
- Predefined strategy picker with backtest-backed pros/cons
- Email alerts via Gmail SMTP when a chosen strategy's condition flips (with a 6-hour per-user cooldown)
- ML-based `BUY`/`HOLD`/`SELL` signal model
- Strategy backtesting against historical BTC data (closed-trade metrics and trade history)

**Out of scope (for this timeline):**
- Multi-coin support
- User-created custom strategies
- Browser push notifications
- Real trading / real money handling

## Phase 0 — Setup & Foundation (Weeks 1–2) ✅

**Goal:** Everyone has a working dev environment and the team agrees on the technical foundation.

- [x] Repository created, structured (`/frontend`, `/backend`, `/ml`, `/docs`, `/.github/workflows`), and initial `README.md` written
- [x] `.gitignore`, CI pipeline, and branch protection set up
- [x] GitHub Projects board and Discord communication channels set up
- [x] Tech stack confirmed (React/Vite, FastAPI, Supabase, GitHub Actions)
- [x] API contract drafted (`docs/api-contract.md` v1.2)
- [x] Local development environments configured across all team members
- [x] Binance market data access confirmed (`data-api.binance.vision` mirror to avoid GitHub US runner HTTP 451 blocks)

## Phase 1 — Core Build Part 1 (Weeks 3–5) ✅

**Goal:** Each architectural layer works independently and connects end-to-end.

- [x] **AI/ML:** Real BTC data ingestion, technical indicator computation (RSI, MACD, SMA 20, SMA 50), and baseline ML signal model
- [x] **Backend & Data:** Automated data pipeline pulling BTC prices into Supabase, initial database schema, and core FastAPI endpoints returning real data
- [x] **Frontend:** Auth screens (sign up/login/logout) and initial dashboard connected to backend endpoints
- [x] **MLOps & Deployment:** CI pipeline running and initial Vercel + Render deployments live

### ⭐ Mid-Project Checkpoint ✅
**Thin end-to-end slice verified:** Real BTC data flows from GitHub Actions → Supabase → indicator & ML signal computation → FastAPI → React/Vite dashboard.

## Phase 2 — Core Build Part 2 (Weeks 6–9) ✅

**Goal:** Full feature implementation replaces rough baselines and placeholders.

- [x] **AI/ML:** ML model training/evaluation, closed-trade backtesting logic across predefined strategies, and strategy explainer aligned to the latest backtest window (`PR #120`)
- [x] **Backend & Data:** Full API endpoints completed per `docs/api-contract.md`, input validation, CORS, and Supabase integration hardened
- [x] **Frontend:** Live BTC charts with indicator overlays, strategy picker UI, backtest results UI (with graceful handling for missing ranges and `ml_signal`, `PR #121`), and alert settings UI
- [x] **MLOps & Deployment:**
  - Prices & indicators pipeline running on Python 3.12 (`PR #117`, `PR #119`)
  - Daily backtesting workflow (`00:45 UTC`)
  - Automated retraining pipeline and alert job with labeled `[TEST]` mode (`PR #115`, `PR #118`)

## Phase 3 — Integration, Live Go-Live & Polish (Weeks 10–11) ✅

**Goal:** End-to-end verification, production stability, and bug fixes.

- [x] Vercel SPA rewrite configured so direct links and page refreshes work reliably (`PR #116`)
- [x] Frontend backtest loading and missing-range edge cases resolved (`PR #121`)
- [x] Scheduled alert job switched to `Mode: LIVE` (`PR #122`) and verified end-to-end on **November 25, 2026** (`BTC SELL alert: MACD Momentum` delivered to Gmail and `last_alerted_at` updated in Supabase)
- [x] Closed integration & bug issues (`#49`, `#74`, `#76`, `#77`)
- [x] Integration testing report documented and updated with live alert verification (`docs/testing-report.md`, `PR #123`, `PR #124`)

## Phase 4 — Final Documentation & Demo Prep (Week 12) 🔄

**Goal:** Feature freeze, complete project documentation, and deliver a smooth live demo.

- [x] Feature freeze active; `README.md` updated with live URLs, team roles/IDs, and milestones
- [ ] Update `docs/roadmap.md` on `main`
- [ ] Complete `CSC480` Final Project Report with annotated GUI screenshots (Due: **November 27, 2026**)
- [ ] Rehearse presentation & live demo with pre-warmed Render backend and mobile hotspot backup (Demo: **December 1, 2026**)

## Workflow

- **Cadence:** Iterative 3-month schedule with weekly syncs and async updates in Discord `#daily-updates`
- **Task tracking:** [GitHub Project Board](https://github.com/users/zwecodes/projects/1) — Backlog / To Do / In Progress / In Review / Done
- **Code workflow:** Feature branch per task + pull request into `main` (124+ PRs merged across the project)
- **Code discussion:** GitHub Issues/PRs for technical reviews, Discord for quick coordination

## Roles

| Role | Owner | Student ID | Responsibilities |
|---|---|---|---|
| AI/ML Engineer | Saw Htet Arkar | ID-6702721 | Indicators, feature engineering, ML model, backtesting logic, strategy explainer |
| Frontend Developer | Htet Naing Zaw | ID-6804494 | Auth screens, dashboard, strategy picker UI, backtest results UI, alert settings UI |
| Backend & Infra + Coordination | Zwe Htet Aung | ID-6703301 | Backend API, API contract, data/database integration, testing & verification, sprint coordination |
| MLOps & Deployment | Kaung Khant Lwin | ID-6703114 | Deployment, CI/CD, retraining pipeline, alert job, email sending, monitoring |