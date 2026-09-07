"""
app.py
Flask backend for the Sales Analytics Dashboard.

Serves aggregated + raw sales data as JSON so the frontend (web/index.html)
becomes a real client that fetches from an API, instead of embedding a
static JSON blob at build time.

Run:  python app.py
API base: http://localhost:5000/api

Endpoints:
  GET /api/kpis                          -> headline KPIs
  GET /api/monthly?region=&category=     -> monthly revenue trend
  GET /api/regions                       -> region-wise summary
  GET /api/categories                    -> category-wise summary
  GET /api/reps?region=                  -> sales rep leaderboard
  GET /api/orders?region=&category=&limit=50&offset=0  -> paginated raw orders
  GET /api/filters                       -> distinct regions/categories for dropdowns
"""

import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, g

DB_PATH = Path(__file__).parent.parent / "sql" / "sales.db"

app = Flask(__name__)


# ---------------------------------------------------------------------------
# CORS (hand-rolled, no external dependency needed)
# ---------------------------------------------------------------------------
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def rows_to_dicts(rows):
    return [dict(r) for r in rows]


def build_where(region, category):
    clauses, params = [], []
    if region and region != "all":
        clauses.append("region = ?")
        params.append(region)
    if category and category != "all":
        clauses.append("category = ?")
        params.append(category)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where, params


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/filters")
def filters():
    db = get_db()
    regions = [r["region"] for r in db.execute("SELECT DISTINCT region FROM sales ORDER BY region")]
    categories = [r["category"] for r in db.execute("SELECT DISTINCT category FROM sales ORDER BY category")]
    return jsonify({"regions": regions, "categories": categories})


@app.route("/api/kpis")
def kpis():
    region = request.args.get("region")
    category = request.args.get("category")
    where, params = build_where(region, category)

    db = get_db()
    row = db.execute(f"""
        SELECT
            COUNT(DISTINCT order_id)  AS total_orders,
            ROUND(SUM(net_sales), 2)  AS total_revenue,
            SUM(quantity)             AS total_units_sold,
            ROUND(SUM(net_sales) * 1.0 / COUNT(DISTINCT order_id), 2) AS avg_order_value,
            ROUND(SUM(discount_amount), 2) AS total_discount_given
        FROM sales {where}
    """, params).fetchone()
    return jsonify(dict(row))


@app.route("/api/monthly")
def monthly():
    region = request.args.get("region")
    category = request.args.get("category")
    where, params = build_where(region, category)

    db = get_db()
    rows = db.execute(f"""
        SELECT order_month, ROUND(SUM(net_sales), 2) AS revenue,
               COUNT(DISTINCT order_id) AS orders, SUM(quantity) AS units
        FROM sales {where}
        GROUP BY order_month
        ORDER BY order_month
    """, params).fetchall()
    return jsonify(rows_to_dicts(rows))


@app.route("/api/regions")
def regions():
    category = request.args.get("category")
    where, params = build_where(None, category)

    db = get_db()
    rows = db.execute(f"""
        SELECT region, ROUND(SUM(net_sales), 2) AS revenue,
               COUNT(DISTINCT order_id) AS orders,
               ROUND(AVG(net_sales), 2) AS avg_order_value
        FROM sales {where}
        GROUP BY region
        ORDER BY revenue DESC
    """, params).fetchall()
    return jsonify(rows_to_dicts(rows))


@app.route("/api/categories")
def categories():
    region = request.args.get("region")
    where, params = build_where(region, None)

    db = get_db()
    rows = db.execute(f"""
        SELECT category, ROUND(SUM(net_sales), 2) AS revenue, SUM(quantity) AS units_sold
        FROM sales {where}
        GROUP BY category
        ORDER BY revenue DESC
    """, params).fetchall()
    return jsonify(rows_to_dicts(rows))


@app.route("/api/reps")
def reps():
    region = request.args.get("region")
    category = request.args.get("category")
    where, params = build_where(region, category)

    db = get_db()
    rows = db.execute(f"""
        SELECT sales_rep, region, ROUND(SUM(net_sales), 2) AS revenue,
               COUNT(DISTINCT order_id) AS orders
        FROM sales {where}
        GROUP BY sales_rep, region
        ORDER BY revenue DESC
    """, params).fetchall()
    return jsonify(rows_to_dicts(rows))


@app.route("/api/orders")
def orders():
    region = request.args.get("region")
    category = request.args.get("category")
    limit = min(int(request.args.get("limit", 50)), 500)
    offset = int(request.args.get("offset", 0))
    where, params = build_where(region, category)

    db = get_db()
    total = db.execute(f"SELECT COUNT(*) AS c FROM sales {where}", params).fetchone()["c"]
    rows = db.execute(f"""
        SELECT order_id, order_date, region, sales_rep, product, category,
               quantity, net_sales, customer_segment, payment_mode
        FROM sales {where}
        ORDER BY order_date DESC
        LIMIT ? OFFSET ?
    """, params + [limit, offset]).fetchall()
    return jsonify({"total": total, "limit": limit, "offset": offset, "orders": rows_to_dicts(rows)})


if __name__ == "__main__":
    if not DB_PATH.exists():
        raise SystemExit(f"Database not found at {DB_PATH}. Run sql/load_db.py first.")
    app.run(debug=True, port=5000)
