"""Chart: what share of customers came back for a 2nd order within N months
of their first order? Saves reports/figures/retention_curve.png.
"""
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "olist.db"
OUT_PATH = ROOT / "reports" / "figures" / "retention_curve.png"
MAX_MONTHS = 12

# --- 1. Load orders and number the months (same idea as cohort_retention.py) --
con = sqlite3.connect(DB_PATH)
orders = pd.read_sql(
    "SELECT customer_unique_id, purchased_at FROM orders_clean",
    con,
    parse_dates=["purchased_at"],
)
con.close()

orders["month_num"] = orders["purchased_at"].dt.year * 12 + orders["purchased_at"].dt.month
orders["cohort_num"] = orders.groupby("customer_unique_id")["month_num"].transform("min")
orders["months_since"] = orders["month_num"] - orders["cohort_num"]
last_month = orders["month_num"].max()

# --- 2. One row per customer: when did they first come back (if ever)? ---------
customers = orders.groupby("customer_unique_id").agg(cohort_num=("cohort_num", "first"))
first_return = orders[orders["months_since"] > 0].groupby("customer_unique_id")["months_since"].min()
customers["first_return"] = first_return  # customers who never came back get NaN
customers["months_observed"] = last_month - customers["cohort_num"]

# --- 3. For each N, % of customers who came back within N months ---------------
# Only count customers we could watch for at least N months; otherwise
# recent customers would drag the number down unfairly (the "short window" problem).
rows = []
for n in range(1, MAX_MONTHS + 1):
    eligible = customers[customers["months_observed"] >= n]
    came_back = (eligible["first_return"] <= n).sum()
    rows.append({"months": n, "pct": 100 * came_back / len(eligible), "customers": len(eligible)})
curve = pd.DataFrame(rows)
print(curve.round(2).to_string(index=False))

# --- 4. Draw it ------------------------------------------------------------
LINE = "#2a78d6"
TEXT = "#0b0b0b"
TEXT_MUTED = "#52514e"
GRID = "#e4e2dc"

fig, ax = plt.subplots(figsize=(7, 3.6), dpi=200)
ax.plot(curve["months"], curve["pct"], color=LINE, linewidth=2)
ax.plot(curve["months"], curve["pct"], "o", color=LINE, markersize=4)

# Label only the end point, so the key number is on the chart.
end = curve.iloc[-1]
ax.annotate(f"{end['pct']:.1f}%", (end["months"], end["pct"]),
            xytext=(6, 0), textcoords="offset points", va="center", fontsize=11, color=TEXT)

# Y axis from 0, so the line's height is honest; a little headroom above.
ax.set_ylim(0, max(5, curve["pct"].max() * 1.6))
ax.set_xlim(0.5, MAX_MONTHS + 1.2)
ax.set_xticks(range(1, MAX_MONTHS + 1))
ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
ax.set_xlabel("Months after first order", fontsize=9, color=TEXT_MUTED)

# Light horizontal grid only; no box.
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for side in ["top", "right", "left"]:
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(length=0, labelsize=9, labelcolor=TEXT_MUTED)

fig.text(0.02, 0.94, f"Only {end['pct']:.1f}% of customers came back within {MAX_MONTHS} months",
         fontsize=13, fontweight="bold", color=TEXT, ha="left")
fig.text(0.02, 0.87,
         "Customers with a 2nd order within N months of their first "
         "(each point uses only customers we could follow for N months)",
         fontsize=8, color=TEXT_MUTED, ha="left")

fig.subplots_adjust(left=0.08, right=0.95, top=0.80, bottom=0.14)
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PATH, facecolor="white")
print(f"Saved chart to {OUT_PATH}")
