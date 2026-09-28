import mysql.connector
from mysql.connector import pooling
from flask import current_app

_pool = None

def init_db(app):
    global _pool
    # Pool is created lazily; this keeps the app importable before MySQL is configured.
    _pool = None

def get_connection():
    global _pool
    if _pool is None:
        cfg = current_app.config
        _pool = pooling.MySQLConnectionPool(
            pool_name="asset_pool",
            pool_size=5,
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            autocommit=False
        )
    return _pool.get_connection()

def query(sql, params=(), fetch="all", commit=False):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        result = cur.fetchall() if fetch == "all" else (cur.fetchone() if fetch == "one" else cur.lastrowid)
        if commit:
            conn.commit()
        return result
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def execute_many(sql, rows):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.executemany(sql, rows)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
