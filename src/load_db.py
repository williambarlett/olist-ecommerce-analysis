import sqlite3
from pathlib import Path
import pandas as pd

RAW = Path("data/raw")
DB_PATH = Path("data/olist.db")

TABLES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

conn = sqlite3.connect(DB_PATH)

for table_name, file_name in TABLES.items():
    df = pd.read_csv(RAW / file_name)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Loaded {table_name}: {len(df):,} rows")

conn.close()
print("Done. Database saved to", DB_PATH)