
import psycopg2
from config import DATABASE_PARAMS

def get_db_connection():
    try:
        conn = psycopg2.connect(**DATABASE_PARAMS)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
