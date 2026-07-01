import psycopg2

db_url = "postgresql://voyagentdb_user:PRVWEUDOu6041Pno3x4mhnTLTEkqAEj8@dpg-d8t0eun7f7vs73bkrdng-a.oregon-postgres.render.com/voyagentdb"

def wipe_db():
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        print("Dropping public schema...")
        cursor.execute("DROP SCHEMA public CASCADE;")
        print("Creating public schema...")
        cursor.execute("CREATE SCHEMA public;")
        print("Database wiped successfully. Ready for fresh migrations.")
    except Exception as e:
        print(f"Error wiping database: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    wipe_db()
