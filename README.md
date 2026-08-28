# Crypto Analysis Project

AI-powered Bitcoin trading analysis platform for a Software Engineering 
final project. The system collects real BTC market data, computes technical 
indicators, generates BUY/HOLD/SELL signals using a machine learning model, 
offers AI-explained trading strategies, sends email alerts when strategy 
conditions are met, and evaluates strategies through backtesting — 
presented via a web dashboard.

**Note:** This project analyzes and simulates trading strategies for 
educational purposes. It does not execute real trades or handle real funds.

## Features
- Sign up / login (Supabase Auth)
- Live BTC price chart with technical indicator overlays
- AI-assisted strategy picker (predefined strategies, AI explains pros/cons)
- Email alerts when a chosen strategy's condition is met
- ML-based BUY/HOLD/SELL signal model
- Strategy backtesting against historical BTC data

## Architecture

Binance API (BTC data)
↓
Database (Supabase) — price history, indicators, users, alert state
↓
Backend API
↓
┌─────────────┬──────────────────────┐
ML Model AI Strategy Explainer
(BUY/HOLD/SELL) (pros/cons via LLM)
↓ ↓
Backtesting Strategy Selection
↓ ↓
Dashboard (charts, signals, strategy picker)
↓
Background alert job → Email (SMTP) when criteria met


## Team & Roles

| Role | Owner | Responsibilities |
|---|---|---|
| AI/ML Engineer | [Saw Htet Arkar] | Indicators, feature engineering, ML model, backtesting logic, AI strategy explainer |
| Full-Stack Developer | [Htet Naing Zaw] | Auth screens, dashboard, strategy picker UI, backtest results UI, alert settings UI |
| Cloud/Infra — Data & Backend + Coordination | [Zwe Htet Aung] | Database, data pipeline, backend API, API contract, security, sprint coordination |
| Cloud/Infra — MLOps & Deployment | [Kaung Khant Lwin] | Deployment, CI/CD, retraining pipeline, alert job, email sending, monitoring |

## Tech Stack
*To be finalized — see `docs/tech-stack.md`*

## Project Structure

/frontend → Dashboard, auth UI, strategy picker (React/Next.js)
/backend → API, data pipeline, database logic
/ml → Models, indicators, backtesting, AI strategy explainer
/infra → Deployment configs, CI/CD, retraining & alert jobs
/docs → Architecture notes, API contract, roadmap


## Roadmap
See [`docs/roadmap.md`](docs/roadmap.md) for the sprint-by-sprint plan.

## Status
🚧 In development — Sprint 0 (project setup)

## Project Board
[GitHub Project Board](https://github.com/users/zwecodes/projects/1)