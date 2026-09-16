# Tech Stack

**Status: Confirmed** — locked in as of Sprint 0/1.

## Frontend
- **React + Vite + TypeScript**
- Chosen over Next.js — the app uses client-side Supabase Auth and talks 
  to a separate backend API, so server-side rendering isn't needed. 
  Vite gives a faster, simpler dev setup for this architecture.
- Deployed via **Vercel**

## Backend
- **Python + FastAPI**
- Shares language with the ML layer, enabling shared utilities and easier 
  handoff between backend and ML work
- Deployed via **Render** (or Oracle Cloud free VM if needed)

## Database & Auth
- **Supabase (PostgreSQL)**
- Built-in Auth (sign up / login) — avoids building auth from scratch
- Row Level Security (RLS) enabled for user-specific data

## Machine Learning
- **scikit-learn + pandas**
- Simple, interpretable classifiers (logistic regression / random forest) 
  — not deep learning, to keep training/evaluation tractable within the 
  project timeline

## AI Strategy Explainer
- **Claude API or OpenAI API**
- Used to generate plain-language pros/cons for each predefined strategy
- Generated once via an internal script, cached in the database — not 
  called live per request

## Data Source
- **Binance public API** (`/api/v3/klines`) — no API key required
- **CoinGecko** as a secondary/backup source if needed

## CI/CD & Scheduling
- **GitHub Actions**
- Runs tests and builds on every push
- Scheduled workflows (cron) used for the ML retraining pipeline and the 
  alert-checking background job

## Email Alerts
- **SMTP (Gmail)** or **SendGrid**
- Sends alert emails when a user's selected strategy's condition is met

## Version Control & Collaboration
- **GitHub** — branch + pull request workflow, branch protection on `main`
- **GitHub Projects** — sprint board and issue tracking
- **Discord** — team communication, role-specific channels

---

*Last updated: Sprint 1 · Owner: Zwe Htet Aung (Cloud/Infra — Data & Backend + Coordination)*