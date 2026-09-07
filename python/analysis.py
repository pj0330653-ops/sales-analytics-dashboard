"""
analysis.py
Core data-cleaning + analysis script for the Sales Analytics Dashboard.

What this teaches:
  - reading & inspecting raw data with pandas
  - cleaning (nulls, duplicates, bad values)
  - groupby aggregations for business KPIs
  - exporting clean data + summary tables for the SQL / Excel / web steps

Run: python analysis.py
Inputs : ../data/sales_data.csv
Outputs: ../data/sales_data_clean.csv
         ../data/kpi_summary.csv
         ../data/monthly_trend.csv
         ../data/region_summary.csv
         ../data/category_summary.csv
         ../data/rep_leaderboard.csv
"""

import pandas as pd

RAW_PATH = "../data/sales_data.csv"

# ---------------------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------------------
df = pd.read_csv(RAW_PATH, parse_dates=["order_date"])
print(f"Loaded {len(df)} raw rows")

# ---------------------------------------------------------------------------
# 2. CLEAN
# ---------------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates(subset="order_id")
print(f"Removed {before - len(df)} duplicate orders")

# negative/zero quantity is bad data entry -> fix by taking absolute value
bad_qty = df["quantity"] < 0
df.loc[bad_qty, "quantity"] = df.loc[bad_qty, "quantity"].abs()
print(f"Fixed {bad_qty.sum()} negative-quantity rows")

# missing discount -> assume 0% (no discount applied)
df["discount_pct"] = df["discount_pct"].fillna(0)

# missing customer_segment -> label explicitly instead of guessing
df["customer_segment"] = df["customer_segment"].fillna("Unspecified")

# recompute money fields after fixes, so they always match qty/discount
df["gross_sales"] = df["quantity"] * df["unit_price"]
df["discount_amount"] = (df["gross_sales"] * df["discount_pct"] / 100).round(2)
df["net_sales"] = (df["gross_sales"] - df["discount_amount"]).round(2)

# useful derived columns for time-based analysis
df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
df["order_year"] = df["order_date"].dt.year
df["weekday"] = df["order_date"].dt.day_name()

df.to_csv("../data/sales_data_clean.csv", index=False)
print(f"Clean dataset: {len(df)} rows -> ../data/sales_data_clean.csv")

# ---------------------------------------------------------------------------
# 3. HEADLINE KPIs
# ---------------------------------------------------------------------------
total_orders = df["order_id"].nunique()
total_revenue = df["net_sales"].sum()
total_units = df["quantity"].sum()
avg_order_value = df.groupby("order_id")["net_sales"].sum().mean()
total_discount_given = df["discount_amount"].sum()

kpi = pd.DataFrame([{
    "total_orders": total_orders,
    "total_revenue": round(total_revenue, 2),
    "total_units_sold": int(total_units),
    "avg_order_value": round(avg_order_value, 2),
    "total_discount_given": round(total_discount_given, 2),
    "unique_products": df["product"].nunique(),
    "unique_regions": df["region"].nunique(),
    "unique_sales_reps": df["sales_rep"].nunique(),
}])
kpi.to_csv("../data/kpi_summary.csv", index=False)
print("\n--- Headline KPIs ---")
print(kpi.T.rename(columns={0: "value"}))

# ---------------------------------------------------------------------------
# 4. MONTHLY REVENUE TREND
# ---------------------------------------------------------------------------
monthly = (
    df.groupby("order_month")
    .agg(revenue=("net_sales", "sum"), orders=("order_id", "nunique"), units=("quantity", "sum"))
    .reset_index()
    .sort_values("order_month")
)
monthly.to_csv("../data/monthly_trend.csv", index=False)

# ---------------------------------------------------------------------------
# 5. REGION-WISE SUMMARY
# ---------------------------------------------------------------------------
region_summary = (
    df.groupby("region")
    .agg(revenue=("net_sales", "sum"), orders=("order_id", "nunique"), avg_order_value=("net_sales", "mean"))
    .round(2)
    .sort_values("revenue", ascending=False)
    .reset_index()
)
region_summary.to_csv("../data/region_summary.csv", index=False)

# ---------------------------------------------------------------------------
# 6. CATEGORY-WISE SUMMARY
# ---------------------------------------------------------------------------
category_summary = (
    df.groupby("category")
    .agg(revenue=("net_sales", "sum"), units_sold=("quantity", "sum"))
    .round(2)
    .sort_values("revenue", ascending=False)
    .reset_index()
)
category_summary.to_csv("../data/category_summary.csv", index=False)

# ---------------------------------------------------------------------------
# 7. SALES REP LEADERBOARD
# ---------------------------------------------------------------------------
rep_leaderboard = (
    df.groupby(["sales_rep", "region"])
    .agg(revenue=("net_sales", "sum"), orders=("order_id", "nunique"))
    .round(2)
    .sort_values("revenue", ascending=False)
    .reset_index()
)
rep_leaderboard.to_csv("../data/rep_leaderboard.csv", index=False)

print("\nAll summary tables written to ../data/. Ready for SQL, Excel and the web dashboard.")
