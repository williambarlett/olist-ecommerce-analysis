"""Cohort retention: of the customers who first bought in a given month,
what share came back in later months?

Output:
  - prints a summary table (one row per cohort)
  - saves the full retention table to data/processed/cohort_retention.csv
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "olist.db"
OUT_PATH = ROOT / "data" / "processed" / "cohort_retention.csv"

# --- 1. Pull the orders we need from SQL into a pandas DataFrame --------------
# One row per order: who bought it and when. parse_dates turns the text
# dates into real datetime values pandas can do math on.
con = sqlite3.connect(DB_PATH)
orders = pd.read_sql(
    "SELECT customer_unique_id, purchased_at FROM orders_clean",
    con,
    parse_dates=["purchased_at"],
)
con.close()

# --- 2. Give every order a month number ---------------------------------------
# year * 12 + month turns a date into a single counting number of months,
# so subtracting two of them gives "how many months apart".
orders["month_num"] = orders["purchased_at"].dt.year * 12 + orders["purchased_at"].dt.month

# --- 3. Find each customer's cohort (the month of their FIRST order) -----------
# groupby(...).transform("min") finds each customer's earliest value and
# writes it back onto every one of that customer's rows.
orders["cohort_num"] = orders.groupby("customer_unique_id")["month_num"].transform("min")
orders["cohort"] = (
    orders.groupby("customer_unique_id")["purchased_at"].transform("min").dt.to_period("M")
)

# How many months after their first order was this order placed?
# 0 = their first month, 1 = the month after, and so on.
orders["months_since"] = orders["month_num"] - orders["cohort_num"]

# --- 4. Build the retention table ---------------------------------------------
# Count distinct customers for each (cohort, months_since) pair, then
# unstack() turns months_since into columns: one row per cohort.
counts = (
    orders.groupby(["cohort", "months_since"])["customer_unique_id"]
    .nunique()
    .unstack(fill_value=0)
)
cohort_size = counts[0]  # month 0 = everyone in the cohort
# Divide every column by the cohort size (axis=0 means "row by row") -> percent.
retention = counts.div(cohort_size, axis=0) * 100

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
retention.round(2).to_csv(OUT_PATH)

# --- 5. Summary: what share of each cohort EVER came back? ---------------------
returned = (
    orders[orders["months_since"] > 0]
    .groupby("cohort")["customer_unique_id"]
    .nunique()
    .reindex(cohort_size.index, fill_value=0)  # cohorts with 0 returners get 0
)
last_month = orders["month_num"].max()

summary = pd.DataFrame({
    "customers": cohort_size,
    "came_back": returned,
    "pct_came_back": (100 * returned / cohort_size).round(1),
    # how many later months this cohort had to come back in
    "months_to_return": last_month - counts.index.map(lambda p: p.year * 12 + p.month),
})

print(summary.to_string())
print()
print(f"Saved full retention table to {OUT_PATH}")
