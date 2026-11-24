"""Chart: share of 1-2 star reviews for on-time vs late orders.
Saves reports/figures/late_vs_reviews.png (for the README).
"""
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "olist.db"
OUT_PATH = ROOT / "reports" / "figures" / "late_vs_reviews.png"

# --- 1. Get the numbers with SQL (same logic as sql/10_late_vs_reviews.sql) ---
query = """
SELECT
    CASE WHEN o.is_late = 1 THEN 'Late' ELSE 'On time' END AS delivery,
    COUNT(*) AS orders,
    100.0 * AVG(CASE WHEN rv.review_score <= 2 THEN 1 ELSE 0 END) AS pct_bad
FROM orders_clean AS o
JOIN reviews_clean AS rv ON rv.order_id = o.order_id
WHERE o.is_late IS NOT NULL
GROUP BY delivery
"""
con = sqlite3.connect(DB_PATH)
df = pd.read_sql(query, con).set_index("delivery")
con.close()

on_time = df.loc["On time", "pct_bad"]
late = df.loc["Late", "pct_bad"]
ratio = late / on_time

# --- 2. Colors and text styles ---------------------------------------------
# Late gets the strong color (it's the point of the chart);
# on time is a quiet gray so it reads as the comparison.
LATE_COLOR = "#2a78d6"
ON_TIME_COLOR = "#b9b7b0"
TEXT = "#0b0b0b"
TEXT_MUTED = "#52514e"

# --- 3. Draw a horizontal bar chart ----------------------------------------
fig, ax = plt.subplots(figsize=(7, 2.6), dpi=200)

labels = ["On time", "Late"]
values = [on_time, late]
colors = [ON_TIME_COLOR, LATE_COLOR]
ax.barh(labels, values, color=colors, height=0.35)

# Put each value at the end of its bar, so no axis is needed.
for y, v in enumerate(values):
    ax.text(v + 1, y, f"{v:.1f}%", va="center", fontsize=11, color=TEXT)

# Title states the finding, subtitle says exactly what was measured.
fig.text(0.02, 0.93, f"Late orders were {ratio:.1f}x more likely to get a 1-2 star review",
         fontsize=13, fontweight="bold", color=TEXT, ha="left")
fig.text(0.02, 0.84,
         f"Share of orders with a 1-2 star review, Olist delivered orders Jan 2017 - Aug 2018 "
         f"(n = {int(df['orders'].sum()):,})",
         fontsize=8.5, color=TEXT_MUTED, ha="left")

# Strip the clutter: no box, no x-axis (values are written on the bars).
for side in ["top", "right", "bottom", "left"]:
    ax.spines[side].set_visible(False)
ax.set_xticks([])
ax.tick_params(axis="y", length=0, labelsize=11, labelcolor=TEXT)
ax.set_xlim(0, max(values) * 1.15)

fig.subplots_adjust(left=0.13, right=0.97, top=0.75, bottom=0.08)
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PATH, facecolor="white")
print(f"On time: {on_time:.1f}% bad reviews | Late: {late:.1f}% | {ratio:.1f}x")
print(f"Saved chart to {OUT_PATH}")
