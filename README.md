# Crypto Analysis Project

AI-powered Bitcoin trading analysis platform for a Software Engineering final project (`CSC480`). The system ingests real BTC market data, computes technical indicators, generates `BUY`/`HOLD`/`SELL` signals via a machine learning model, provides strategy explanations, sends email alerts when strategy conditions flip, and evaluates strategies through historical backtesting — presented via a web dashboard.

**Note:** This project analyzes and simulates trading strategies for educational purposes. It does not execute real trades or handle real funds.

## Live Deployment & Links

- **Frontend:** https://crypto-analysis-ten.vercel.app (React / Vite on Vercel, auto-deployed from `main` with SPA rewrite in `frontend/vercel.json`)
- **Backend API:** https://crypto-analysis-x1y8.onrender.com (FastAPI on Render)
- **Auth & Database:** Supabase (PostgreSQL + Supabase Auth)
- **Project Board:** [GitHub Project Board](https://github.com/users/zwecodes/projects/1)

## Features

- **Authentication:** Sign up, login, logout, and session management via Supabase Auth
- **Live BTC Dashboard:** Real-time BTC price metrics, 24-hour price chart, technical indicators (RSI, MACD & signal line, SMA 20, SMA 50), and ML signal status
- **Strategy Picker:** Browse predefined trading strategies with backtest-backed pros/cons and select an active strategy for alerts
- **Strategy Backtesting:** Query historical performance metrics and trade history across stored date ranges (with graceful handling where backtests are not applicable, such as `ml_signal`)
- **Alert Settings & Email Notifications:** Manage active strategy subscriptions and receive automated email alerts from the project's Gmail account to every user who has a strategy selected when signal conditions flip (subject to a 6-hour per-user cooldown)

## Architecture

- **Market Data & Pipelines (GitHub Actions):**
  - Hourly prices and technical indicators pipeline (`data-api.binance.vision` mirror to avoid GitHub US runner HTTP 451 blocks, Python 3.12)
  - Daily backtesting job (`00:45 UTC`) storing closed-trade results across date ranges
  - Scheduled alert job (evaluates signal flips, sends email alerts via SMTP to users with a selected strategy, and records `last_alerted_at` in Supabase)
- **Database & API:** Supabase stores price history, indicators, strategies, backtest results, and user strategy selections; FastAPI serves contract-tested endpoints (`docs/api-contract.md`)
- **Frontend:** React/Vite single-page application deployed on Vercel

## Team & Roles

| Role | Owner | Responsibilities |
|---|---|---|
| AI/ML Engineer | Saw Htet Arkar| ID-6702721 | Indicators, feature engineering, ML model, backtesting logic, strategy explainer |
| Frontend Developer | Htet Naing Zaw | ID-6804494 | Auth screens, dashboard, strategy picker UI, backtest results UI, alert settings UI |
| Backend & Infra + Coordination | Zwe Htet Aung | ID-6703301 | Backend API, API contract, data/database integration, testing & verification, sprint coordination |
| MLOps & Deployment | Kaung Khant Lwin | ID-6703114 | Deployment, CI/CD, retraining pipeline, alert job, email sending, monitoring |

## Project Structure

- `/frontend` → React/Vite dashboard, auth UI, strategy picker, backtest UI, alert settings
- `/backend` → FastAPI application, data pipeline services, database access, tests
- `/ml` → Indicator computation, ML signal model, backtesting logic, strategy explainer
- `/.github/workflows` → Automated CI/CD, prices/indicators pipeline, daily backtests, alert job
- `/docs` → API contract, testing report, roadmap, project documentation

## Documentation & Milestones

- **API Contract:** [`docs/api-contract.md`](docs/api-contract.md)
- **Integration Testing Report:** [`docs/testing-report.md`](docs/testing-report.md)
- **Roadmap:** [`docs/roadmap.md`](docs/roadmap.md)
- **Final Report Submission:** November 27, 2026
- **Project Demo:** December 1, 2026

## Status

Integration testing and live alert verification are complete; preparing final report documentation for **November 27, 2026** submission and **December 1, 2026** demo.