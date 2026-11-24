import sqlite3
import sys
import pandas as pd

sql_file = sys.argv[1]
with open(sql_file, encoding="utf-8") as f:
    query = f.read()

conn = sqlite3.connect("data/olist.db")
result = pd.read_sql_query(query, conn)
conn.close()

print(result.to_string(index=False))