"""
load_db.py
Loads sales_data_clean.csv into a SQLite database (sales.db) so the
project has a real SQL layer, not just pandas.

Run: python load_db.py
Output: sales.db
"""

import sqlite3
import pandas as pd

df = pd.read_csv("../data/sales_data_clean.csv")

conn = sqlite3.connect("sales.db")
df.to_sql("sales", conn, if_exists="replace", index=False)

conn.execute("CREATE INDEX IF NOT EXISTS idx_region ON sales(region)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON sales(category)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_month ON sales(order_month)")

conn.commit()
conn.close()
print(f"Loaded {len(df)} rows into sales.db (table: sales)")
