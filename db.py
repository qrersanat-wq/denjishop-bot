import sqlite3
from datetime import datetime
from typing import Optional, Tuple, List
from config import DB_PATH

DDL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS orders (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  tg_user_id    INTEGER NOT NULL,
  product_code  TEXT    NOT NULL,
  product_title TEXT    NOT NULL,
  base_price    INTEGER NOT NULL,
  uniq_amount   INTEGER NOT NULL,
  game_id       TEXT    NOT NULL,
  game_server   TEXT    NOT NULL,
  status        TEXT    NOT NULL DEFAULT 'WAITING_PAYMENT',
  created_at    TEXT    NOT NULL,
  updated_at    TEXT    NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_uniq_amount_wait
  ON orders(uniq_amount)
  WHERE status = 'WAITING_PAYMENT';
"""

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as c:
        for stmt in DDL.strip().split(";\n\n"):
            if stmt.strip():
                c.execute(stmt)

def insert_order(tg_user_id: int, product_code: str, product_title: str,
                 base_price: int, uniq_amount: int, game_id: str, game_server: str) -> int:
    now = datetime.utcnow().isoformat()
    with get_conn() as c:
        cur = c.execute(
            """INSERT INTO orders (tg_user_id, product_code, product_title, base_price, uniq_amount,
                                   game_id, game_server, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'WAITING_PAYMENT', ?, ?)""",
            (tg_user_id, product_code, product_title, base_price, uniq_amount, game_id, game_server, now, now)
        )
        return cur.lastrowid

def list_pending_orders(tg_user_id: int) -> List[sqlite3.Row]:
    with get_conn() as c:
        cur = c.execute(
            "SELECT id, product_title, base_price, uniq_amount, created_at FROM orders "
            "WHERE tg_user_id=? AND status='WAITING_PAYMENT' ORDER BY id DESC",
            (tg_user_id,)
        )
        return cur.fetchall()

def get_open_amounts() -> set:
    with get_conn() as c:
        cur = c.execute("SELECT uniq_amount FROM orders WHERE status='WAITING_PAYMENT'")
        return {r["uniq_amount"] for r in cur.fetchall()}

def mark_paid_by_amount(amount: int) -> Optional[int]:
    """Заготовка на будущее (матчинг по сумме). Вернёт order_id или None."""
    with get_conn() as c:
        cur = c.execute(
            "SELECT id FROM orders WHERE uniq_amount=? AND status='WAITING_PAYMENT'",
            (amount,)
        )
        row = cur.fetchone()
        if not row:
            return None
        order_id = row["id"]
        c.execute(
            "UPDATE orders SET status='PAID', updated_at=? WHERE id=?",
            (datetime.utcnow().isoformat(), order_id)
        )
        return order_id
