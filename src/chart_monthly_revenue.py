"""Chart: monthly revenue, Jan 2017 - Aug 2018.
Saves reports/figures/monthly_revenue.png.
"""
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "olist.db"
OUT_PATH = ROOT / "reports" / "figures" / "monthly_revenue.png"

# --- 1. Monthly revenue (same SQL as sql/06_monthly_revenue.sql) --------------
query = """
WITH order_revenue AS (
    SELECT order_id, SUM(payment_value) AS revenue
    FROM payments
    GROUP BY order_id
)
SELECT o.purchase_month, SUM(r.revenue) AS revenue
FROM orders_clean AS o
LEFT JOIN order_revenue AS r ON r.order_id = o.order_id
GROUP BY o.purchase_month
ORDER BY o.purchase_month
"""
con = sqlite3.connect(DB_PATH)
df = pd.read_sql(query, con)
con.close()

# Turn '2017-01' text into real dates so the x-axis spaces months properly.
df["month"] = pd.to_datetime(df["purchase_month"] + "-01")
df["revenue_k"] = df["revenue"] / 1000  # show R$ thousands, easier to read

# --- 2. Numbers for the title: Q1 2017 vs Q1 2018 average ----------------------
q1_2017 = df[df["purchase_month"].isin(["2017-01", "2017-02", "2017-03"])]["revenue"].mean()
q1_2018 = df[df["purchase_month"].isin(["2018-01", "2018-02", "2018-03"])]["revenue"].mean()
growth = q1_2018 / q1_2017
peak = df.loc[df["revenue"].idxmax()]  # the row with the highest revenue
print(f"Q1 2017 avg: R${q1_2017:,.0f} | Q1 2018 avg: R${q1_2018:,.0f} | {growth:.1f}x")
print(f"Peak month: {peak['purchase_month']} (R${peak['revenue']:,.0f})")

# --- 3. Draw it ------------------------------------------------------------
LINE = "#2a78d6"
TEXT = "#0b0b0b"
TEXT_MUTED = "#52514e"
GRID = "#e4e2dc"

fig, ax = plt.subplots(figsize=(7, 3.6), dpi=200)
ax.plot(df["month"], df["revenue_k"], color=LINE, linewidth=2)

# Mark and label the peak month.
ax.plot(peak["month"], peak["revenue_k"], "o", color=LINE, markersize=5)
ax.annotate(f"Nov 2017 (Black Friday)\nR${peak['revenue'] / 1e6:.2f}M",
            (peak["month"], peak["revenue_k"]),
            xytext=(-10, 12), textcoords="offset points", ha="right",
            fontsize=8.5, color=TEXT)

ax.set_ylim(0, df["revenue_k"].max() * 1.2)
ax.yaxis.set_major_formatter(lambda v, _: f"R${v:,.0f}K")
# Show every 3rd month on the x-axis as 'Jan 2017', 'Apr 2017', ...
ticks = df["month"].iloc[::3]
ax.set_xticks(ticks)
ax.set_xticklabels([d.strftime("%b %Y") for d in ticks])

ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for side in ["top", "right", "left"]:
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(length=0, labelsize=8.5, labelcolor=TEXT_MUTED)

fig.text(0.02, 0.94, f"Revenue grew {growth:.1f}x in a year, then leveled off in 2018",
         fontsize=13, fontweight="bold", color=TEXT, ha="left")
fig.text(0.02, 0.87,
         "Monthly revenue (payments) from delivered Olist orders, Jan 2017 - Aug 2018; "
         "growth compares Q1 2017 with Q1 2018",
         fontsize=8, color=TEXT_MUTED, ha="left")

fig.subplots_adjust(left=0.11, right=0.97, top=0.80, bottom=0.10)
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PATH, facecolor="white")
print(f"Saved chart to {OUT_PATH}")
