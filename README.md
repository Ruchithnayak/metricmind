# MetricMind NOVA — Decision Intelligence Platform

> Turn business metrics into explainable decisions, scenarios, forecasts, actions, and governed insight.

## What is NOVA?

MetricMind NOVA is the upgraded decision-intelligence layer of MetricMind. It is designed to go beyond a conventional BI dashboard by connecting **what happened → why it happened → what could happen → what to do next**.

### Core experience

- **Command Center** — executive KPIs, target gap, decision confidence, signals, market and category performance.
- **AI Analyst** — governed natural-language business questions with a visible local reasoning trace.
- **Scenario Lab** — test price, discount and volume assumptions before making a business move.
- **Action Board** — prioritized next-best actions based on detected business pressure.
- **Root Cause Map** — trace weak performance from KPI → region → discount/profit evidence → action.
- **Forecast Studio** — transparent baseline forecast with explicit guardrails instead of pretending a simple baseline is ML.
- **Signal Radar** — early-warning view ranked by margin and discount risk.
- **Data Trust Center** — schema, completeness, duplicates, numeric integrity and formula validation.
- **Metric Lineage** — visible definitions for Revenue, Profit, Margin and Discount Leakage.
- **Audit Trail** — local session history of analysis, scenarios, filters and exports.

## Architecture

```text
Raw Data
   ↓
Validation / Semantic Layer
   ↓
Governed Metrics
   ↓
Decision Engine
   ├── Explain
   ├── Predict
   ├── Simulate
   ├── Detect Risk
   └── Recommend
          ↓
    Executive Command Center
```

## Offline demo

The NOVA web application is designed to run locally without a network dependency.

```powershell
python run_offline.py
```

Then open:

`http://127.0.0.1:8080`

Or open `web/index.html` directly for the browser-only demo experience.

### Demo login

- Email: `admin@metricmind.ai`
- Password: `metricmind`

## Repository structure

```text
metricmind/
├── backend/                 # semantic/analytics engine
├── data/                    # canonical transaction dataset
├── metricmind_global/       # global pricing standalone module
├── semantic_layer/          # governed metric definitions
├── web/                     # MetricMind NOVA interface
│   ├── index.html
│   └── styles.css
├── run_offline.py           # local offline web server
├── ARCHITECTURE.md
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## Canonical data

`data/sales_data.csv` remains the repository's canonical original transaction dataset. The NOVA interface also contains a bundled browser demo dataset so the UI can start immediately without a backend.

For a production deployment, the next integration step is to make the NOVA decision engine consume the canonical `data/sales_data.csv` through the existing semantic layer rather than relying on demo-embedded records.

## Design principles

1. **Explainability first** — every important recommendation should have an evidence path.
2. **Scenario before action** — allow management to test assumptions before changing targets.
3. **Trust is visible** — data quality should be part of the decision screen, not hidden infrastructure.
4. **Forecast honestly** — distinguish a transparent baseline from a validated predictive model.
5. **Local-first operation** — the demo should remain usable without external services.

## Roadmap

- Connect NOVA directly to the canonical 72-row semantic dataset.
- Add historical backtesting and forecast accuracy metrics.
- Add persistent user accounts and role-based access.
- Add database-backed audit history.
- Add real company data connectors and scheduled refresh.
- Add production-grade authentication and secrets management.

## Author

Ruchith Nayak — [@Ruchithnayak](https://github.com/Ruchithnayak)
