import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS poi;")
    conn.commit()
    print("Successfully deleted the 'poi' table from Neon DB to start fresh.")
    cur.close()
    conn.close()
except Exception as e:
    print("Error:", e)
