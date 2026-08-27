📌 CRYPTO PROJECT ROADMAP (8 weeks)

ROLES:
AI/ML — [Saw Htet Arkar]: indicators, ML model, backtesting logic
Full-Stack — [Htet Naing Zaw]: dashboard, charts, backtest results UI, frontend-backend integration
Cloud/Infra (Data & Backend) — [Kaung Khant Lwin]: data pipeline, database, backend API
Cloud/Infra (MLOps + Deploy + Integration) — [Zwe Htet Aung]: CI/CD, deployment, retraining pipeline, coordination

TIMELINE (4 sprints, 2 weeks each):

Sprint 0 (Week 1): SETUP
Repo, board, API contract, dev environments ready
Goal: everyone can run something locally and push code

Sprint 1 (Week 2-3): CORE BUILD PART 1
ML: pull real data, build 2-3 indicators, rough baseline model
Backend: data pipeline pulling live Binance data into DB
Frontend: scaffold dashboard, connect to mock/fake API
Infra: repo CI running, basic deployment skeleton live

⭐ CHECKPOINT (end of week 4 / start of Sprint 2): 
THIN END-TO-END VERSION WORKING — even if ugly. Real data → 
DB → fake/simple model output → dashboard shows something. 
This is the most important date on the whole calendar.

Sprint 2 (Week 4-5): CORE BUILD PART 2
ML: real model training, backtesting logic
Backend: full API endpoints, historical data for backtesting
Frontend: real charts, indicator overlays, signal display
Infra: retraining pipeline automated, logging in place

Sprint 3 (Week 6-7): INTEGRATION + POLISH
Connect all real pieces together (not mocks anymore)
Fix data format mismatches, bugs
Backtesting results shown properly on dashboard
Deploy the real, connected version

Sprint 4 (Week 8): FINAL PREP
Bug fixes only, no new features after mid-week
Report writing
Presentation/demo prep and rehearsal

WORKFLOW:
Daily 1-2 line update in ⁠daily-updates (what you're doing today)
Weekly 30-min call — let's pick a time now
Code discussion → GitHub issues/PRs, not Discord
Task board: [https://github.com/users/zwecodes/projects/1] — update your own cards