# Project Roadmap

8-week plan, split into 4 sprints of 2 weeks each.

## Product Scope

**In scope:**
- Bitcoin-only trading analysis platform
- Sign up / login (Supabase Auth)
- Live BTC price chart with technical indicators (RSI, MACD, Moving Averages)
- AI-assisted strategy picker — predefined strategies with AI-generated pros/cons
- Email alerts when a chosen strategy's condition is met
- ML-based BUY/HOLD/SELL signal model
- Strategy backtesting against historical BTC data

**Out of scope (for this timeline):**
- Multi-coin support
- User-created custom strategies
- Browser push notifications
- Real trading / real money handling

## Sprint 0 — Setup (Week 1)

**Goal:** Everyone has a working dev environment and the team agrees on the technical foundation.

- [x] Repo created, structured, README written
- [x] `.gitignore`, CI pipeline, branch protection set up
- [x] GitHub Projects board created
- [x] Discord channels set up
- [ ] Tech stack confirmed (frontend framework, backend language, database)
- [ ] API contract drafted (price data, indicators, signals, strategies, alerts endpoints)
- [ ] Each person's dev environment running locally
- [ ] Binance API access confirmed (sample data pull)

## Sprint 1 — Core Build Part 1 (Week 2-3)

**Goal:** Each piece exists independently, even if rough.

- **ML:** pull real BTC data, compute first 2-3 indicators, build a rough baseline model
- **Backend:** data pipeline pulling live BTC data into the database, initial schema built, first API endpoints returning real data
- **Frontend:** auth screens (sign up/login), dashboard scaffold connected to mock API data
- **Infra:** CI fully running, deployment skeleton live (empty apps deployed to confirm hosting works)

### ⭐ Checkpoint — End of Week 4
**Thin end-to-end version must work:** real BTC data flows from the pipeline → database → a basic signal → shown on the dashboard, even if it looks rough. This is the most important milestone — it proves all services can actually talk to each other before anyone polishes their piece.

## Sprint 2 — Core Build Part 2 (Week 4-5)

**Goal:** Real functionality replaces placeholders.

- **ML:** real model training + evaluation, backtesting logic for each predefined strategy, AI strategy explainer (LLM-generated pros/cons)
- **Backend:** full API endpoints complete, caching layer added, security hardening (rate limiting, input validation, CORS)
- **Frontend:** real charts with indicator overlays, strategy picker UI, backtest results UI, alert settings UI
- **Infra:** automated retraining pipeline built, alert background job built, email sending (SMTP) integrated

## Sprint 3 — Integration + Polish (Week 6-7)

**Goal:** All real pieces connected, mocks removed, bugs fixed.

- Swap all frontend mock data for real backend API calls
- End-to-end test the alert system (condition met → email sent)
- Fix data format mismatches and integration bugs
- UI polish pass
- Deploy the fully connected version to production

## Sprint 4 — Final Prep (Week 8)

**Goal:** Stable, demo-ready, documented.

- Bug fixes only after mid-week — no new features
- Final report writing
- Presentation and demo rehearsal
- Confirm deployed version is stable and accessible for the demo

## Workflow

- **Sprints:** 2 weeks each, with a short planning session at the start and a review at the end
- **Daily updates:** short async update in `#daily-updates` — what you're doing today
- **Weekly sync:** 30-min call, same time each week
- **Task tracking:** [GitHub Project Board](https://github.com/users/zwecodes/projects/1) — Backlog / To Do / In Progress / In Review / Done
- **Code workflow:** branch per task + pull request, no direct pushes to `main` (see git workflow guide in Discord)
- **Code discussion:** GitHub Issues/PRs, not Discord

## Roles

| Role | Responsibilities |
|---|---|
| AI/ML Engineer | Indicators, feature engineering, ML model, backtesting logic, AI strategy explainer |
| Full-Stack Developer | Auth screens, dashboard, strategy picker UI, backtest results UI, alert settings UI |
| Cloud/Infra — Data & Backend + Coordination | Database, data pipeline, backend API, API contract, security, sprint tracking |
| Cloud/Infra — MLOps & Deployment | Deployment, CI/CD, retraining pipeline, alert job, email sending, monitoring |