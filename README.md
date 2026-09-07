# Sales Analytics Dashboard

An end-to-end sales analytics project on two years of retail transaction data (2024–2025) — from raw, messy data to a cleaned dataset, SQL analysis, a formula-driven Excel report, and an interactive web dashboard.

**[Live Dashboard](#)** · **[Excel Report](excel/Sales_Report.xlsx)** · **[SQL Queries](sql/queries.sql)**

---

## What this project shows

| Layer | Tool | What it does |
|---|---|---|
| Data generation & cleaning | Python (`pandas`) | Builds a realistic 6,000-row sales dataset, fixes bad data (nulls, negative quantities, duplicates) |
| Analysis | Python (`pandas`) | Groupby aggregations for KPIs, monthly trend, region/category/rep performance |
| Relational analysis | SQL (`SQLite`) | Same business questions solved in SQL, including a window-function leaderboard query |
| Reporting | Excel (`openpyxl`) | A formula-driven report — every KPI is a live `SUM`/`COUNTA` formula, not a hardcoded number, with native charts |
| Backend API | Python (`Flask`) | REST API over the SQLite database — KPIs, trends, and leaderboards, all filterable by region/category |
| Frontend | HTML / CSS / Chart.js | Interactive dashboard. Talks to the Flask API when it's running; falls back to client-side aggregation over embedded data when it isn't (e.g. static hosting on GitHub Pages) — filtering works correctly either way |

## Key insights

- **₹4.74 crore** in total revenue across 6,000 orders (avg order value ≈ ₹7,900)
- **Furniture** drives ~56% of revenue despite being only ~20% of units sold — high ticket size, low volume
- **Festive season (Oct–Dec)** consistently outperforms the rest of the year across both years
- Revenue is evenly spread across regions (under 6% gap between the top and bottom region) — no single region is over-relied on

## Project structure

```
sales-analytics-dashboard/
├── data/
│   ├── sales_data.csv           # raw generated data (intentionally messy)
│   ├── sales_data_clean.csv     # cleaned dataset
│   ├── kpi_summary.csv          # headline KPIs
│   ├── monthly_trend.csv        # month-wise revenue/orders/units
│   ├── region_summary.csv       # region-wise performance
│   ├── category_summary.csv     # category-wise performance
│   ├── rep_leaderboard.csv      # sales rep leaderboard
│   └── dashboard_data.json      # aggregates packaged for the web dashboard
├── python/
│   ├── generate_data.py         # generates the raw dataset
│   └── analysis.py              # cleaning + all groupby analysis
├── sql/
│   ├── load_db.py               # loads clean data into SQLite
│   ├── queries.sql              # 8 business-question SQL queries
│   └── sales.db                 # SQLite database
├── excel/
│   ├── build_report.py          # builds the formula-driven Excel report
│   └── Sales_Report.xlsx        # final report with KPIs + charts
├── backend/
│   ├── app.py                    # Flask REST API over sales.db
│   └── requirements.txt
└── web/
    └── index.html                # interactive Chart.js dashboard (dual-mode: live API or static)
```

## How to run it yourself

```bash
# 1. Generate the raw dataset
cd python && python generate_data.py

# 2. Clean the data and compute all KPIs/summaries
python analysis.py

# 3. Load into SQLite and run the SQL queries
cd ../sql && python load_db.py
sqlite3 sales.db < queries.sql

# 4. Build the Excel report
cd ../excel && python build_report.py

# 5. Start the backend API (optional — the dashboard works without it too)
cd ../backend && pip install -r requirements.txt && python app.py
# API runs at http://localhost:5000/api — try http://localhost:5000/api/kpis

# 6. Open web/index.html in any browser
#    - if the backend is running, the dashboard fetches live filtered data from it
#    - if not, it falls back to embedded data and filters client-side instead
```

**Requirements:** `pandas`, `numpy`, `openpyxl`, `flask` (`pip install pandas numpy openpyxl flask`)

### Backend API reference

| Endpoint | Query params | Returns |
|---|---|---|
| `GET /api/health` | — | `{status: "ok"}` |
| `GET /api/filters` | — | distinct regions & categories |
| `GET /api/kpis` | `region`, `category` | headline KPIs |
| `GET /api/monthly` | `region`, `category` | monthly revenue/orders/units |
| `GET /api/regions` | `category` | region-wise summary |
| `GET /api/categories` | `region` | category-wise summary |
| `GET /api/reps` | `region`, `category` | sales rep leaderboard |
| `GET /api/orders` | `region`, `category`, `limit`, `offset` | paginated raw orders |

## Dataset

6,000 synthetic but realistic transactions spanning Jan 2024–Dec 2025: 5 regions, 10 sales reps, 15 products across 5 categories, 3 customer segments, and 5 payment modes. Seasonality is built in (festive-season boost in Oct–Dec), along with deliberately messy values (missing fields, bad entries, duplicates) so the cleaning step has real work to do.

## What I learned building this

- Structuring a `pandas` cleaning pipeline that's traceable (fix the source columns, then recompute derived money fields, rather than patching the derived fields directly)
- Writing SQL with window functions (`RANK() OVER PARTITION BY`) for per-group leaderboards
- Building Excel reports where every number is a **live formula** referencing the raw data sheet, not a pasted value — so the report recalculates if the underlying data changes
- Building a small REST API (Flask) over SQLite, with server-side filtering by region/category instead of shipping the whole dataset to the client
- Designing a frontend that degrades gracefully — genuinely functional whether it's talking to a live backend or running standalone as a static file

---

*Built by Pravin Jadhav — [LinkedIn](https://linkedin.com/in/) · [Portfolio](#)*
