"""
generate_data.py
Creates a realistic, reproducible retail sales dataset for the
Sales Analytics Dashboard project (Jan 2024 - Dec 2025).

Run: python generate_data.py
Output: ../data/sales_data.csv
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# ---- Reference dimensions -------------------------------------------------

regions = ["North", "South", "East", "West", "Central"]

products = [
    ("Wireless Mouse",        "Electronics", 699),
    ("Mechanical Keyboard",   "Electronics", 2499),
    ("USB-C Hub",             "Electronics", 1299),
    ("Bluetooth Speaker",     "Electronics", 1899),
    ("Office Chair",          "Furniture",   6499),
    ("Standing Desk",         "Furniture",  12999),
    ("Desk Lamp",             "Furniture",   1099),
    ("Notebook Set",          "Stationery",   249),
    ("Whiteboard",            "Stationery",  1499),
    ("Fountain Pen",          "Stationery",   399),
    ("Yoga Mat",              "Fitness",      899),
    ("Dumbbell Set",          "Fitness",     3499),
    ("Water Bottle",          "Fitness",      349),
    ("Backpack",              "Accessories", 1799),
    ("Laptop Sleeve",         "Accessories",  899),
]

sales_reps = [
    ("Aarav Shah", "North"), ("Isha Verma", "North"),
    ("Rohan Mehta", "South"), ("Priya Nair", "South"),
    ("Karan Malhotra", "East"), ("Sneha Roy", "East"),
    ("Vikram Singh", "West"), ("Ananya Iyer", "West"),
    ("Devika Rao", "Central"), ("Arjun Kapoor", "Central"),
]

customer_segments = ["Retail", "Corporate", "Online"]

payment_modes = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash"]

# ---- Generate transactions -------------------------------------------------

start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)
date_range = (end_date - start_date).days

n_rows = 6000
rows = []

for i in range(n_rows):
    day_offset = np.random.randint(0, date_range + 1)
    order_date = start_date + timedelta(days=day_offset)

    # seasonal boost: Oct-Dec (festive/holiday season) sells more
    month = order_date.month
    seasonal_multiplier = 1.6 if month in (10, 11, 12) else (1.2 if month in (3, 4) else 1.0)

    product_name, category, unit_price = products[np.random.randint(len(products))]
    rep_name, rep_region = sales_reps[np.random.randint(len(sales_reps))]

    qty = max(1, int(np.random.poisson(3) * seasonal_multiplier))
    discount_pct = np.random.choice([0, 0, 0, 5, 10, 15, 20], p=[0.35, 0.15, 0.1, 0.15, 0.15, 0.07, 0.03])
    gross = qty * unit_price
    discount_amt = round(gross * discount_pct / 100, 2)
    net_sales = round(gross - discount_amt, 2)

    segment = np.random.choice(customer_segments, p=[0.45, 0.30, 0.25])
    payment = np.random.choice(payment_modes, p=[0.35, 0.25, 0.15, 0.15, 0.10])

    rows.append({
        "order_id": f"ORD{100000+i}",
        "order_date": order_date.strftime("%Y-%m-%d"),
        "region": rep_region,
        "sales_rep": rep_name,
        "product": product_name,
        "category": category,
        "unit_price": unit_price,
        "quantity": qty,
        "discount_pct": discount_pct,
        "gross_sales": gross,
        "discount_amount": discount_amt,
        "net_sales": net_sales,
        "customer_segment": segment,
        "payment_mode": payment,
    })

df = pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)

# introduce a few realistic messy values so cleaning has something to do
messy_idx = np.random.choice(df.index, size=25, replace=False)
df.loc[messy_idx[:10], "discount_pct"] = np.nan
df.loc[messy_idx[10:15], "customer_segment"] = None
df.loc[messy_idx[15:20], "quantity"] = df.loc[messy_idx[15:20], "quantity"] * -1  # bad data
df = pd.concat([df, df.iloc[[0, 1]]], ignore_index=True)  # duplicate rows

df.to_csv("../data/sales_data.csv", index=False)
print(f"Generated {len(df)} rows -> ../data/sales_data.csv")
