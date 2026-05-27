"""
Gestor de base de datos SQLite
Crea las tablas y provee métodos CRUD para transacciones y categorías
"""

import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "economia.db")

CATEGORIAS_INGRESO = ["Sueldo", "Freelance", "Inversiones", "Alquiler cobrado", "Otros ingresos"]
CATEGORIAS_EGRESO  = ["Alimentación", "Alquiler", "Servicios", "Transporte", "Salud",
                      "Educación", "Entretenimiento", "Ropa", "Deudas", "Otros egresos"]


class DatabaseManager:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._crear_tablas()
        self._seed_categorias()

    # ─────────────────────────────────────────
    # Creación de tablas
    # ─────────────────────────────────────────

    def _crear_tablas(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS categorias (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre  TEXT    NOT NULL,
                tipo    TEXT    NOT NULL CHECK(tipo IN ('ingreso','egreso'))
            );

            CREATE TABLE IF NOT EXISTS transacciones (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha        TEXT    NOT NULL,
                monto        REAL    NOT NULL,
                tipo         TEXT    NOT NULL CHECK(tipo IN ('ingreso','egreso')),
                descripcion  TEXT,
                categoria_id INTEGER NOT NULL,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id)
            );
        """)
        self.conn.commit()

    def _seed_categorias(self):
        """Inserta categorías por defecto si la tabla está vacía."""
        cur = self.conn.cursor()
        if cur.execute("SELECT COUNT(*) FROM categorias").fetchone()[0] == 0:
            datos = (
                [(c, "ingreso") for c in CATEGORIAS_INGRESO] +
                [(c, "egreso")  for c in CATEGORIAS_EGRESO]
            )
            cur.executemany("INSERT INTO categorias (nombre, tipo) VALUES (?, ?)", datos)
            self.conn.commit()

    # ─────────────────────────────────────────
    # Categorías
    # ─────────────────────────────────────────

    def get_categorias(self, tipo: str) -> list[dict]:
        """Retorna lista de categorías filtradas por tipo ('ingreso' | 'egreso')."""
        cur = self.conn.cursor()
        rows = cur.execute(
            "SELECT id, nombre FROM categorias WHERE tipo = ? ORDER BY nombre",
            (tipo,)
        ).fetchall()
        return [dict(r) for r in rows]

    def add_categoria(self, nombre: str, tipo: str) -> int:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO categorias (nombre, tipo) VALUES (?, ?)", (nombre, tipo))
        self.conn.commit()
        return cur.lastrowid

    # ─────────────────────────────────────────
    # Transacciones
    # ─────────────────────────────────────────

    def add_transaccion(self, monto: float, tipo: str, descripcion: str,
                        categoria_id: int, fecha: str = None) -> int:
        if fecha is None:
            fecha = datetime.now().strftime("%Y-%m-%d")
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO transacciones (fecha, monto, tipo, descripcion, categoria_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (fecha, monto, tipo, descripcion, categoria_id)
        )
        self.conn.commit()
        return cur.lastrowid

    def delete_transaccion(self, trans_id: int):
        self.conn.execute("DELETE FROM transacciones WHERE id = ?", (trans_id,))
        self.conn.commit()

    def get_transacciones_mes(self, anio: int, mes: int) -> list[dict]:
        """Transacciones de un mes ordenadas por fecha DESC."""
        patron = f"{anio}-{mes:02d}-%"
        cur = self.conn.cursor()
        rows = cur.execute("""
            SELECT t.id, t.fecha, t.monto, t.tipo, t.descripcion, c.nombre AS categoria
            FROM transacciones t
            JOIN categorias c ON t.categoria_id = c.id
            WHERE t.fecha LIKE ?
            ORDER BY t.fecha DESC
        """, (patron,)).fetchall()
        return [dict(r) for r in rows]

    def get_resumen_mes(self, anio: int, mes: int) -> dict:
        """Retorna {ingresos, egresos, balance} del mes."""
        patron = f"{anio}-{mes:02d}-%"
        cur = self.conn.cursor()
        row = cur.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN tipo='ingreso' THEN monto ELSE 0 END), 0) AS ingresos,
                COALESCE(SUM(CASE WHEN tipo='egreso'  THEN monto ELSE 0 END), 0) AS egresos
            FROM transacciones
            WHERE fecha LIKE ?
        """, (patron,)).fetchone()
        ingresos = row["ingresos"]
        egresos  = row["egresos"]
        return {"ingresos": ingresos, "egresos": egresos, "balance": ingresos - egresos}

    def get_por_categoria_mes(self, anio: int, mes: int, tipo: str) -> list[dict]:
        """Agrupado por categoría para gráficos de torta."""
        patron = f"{anio}-{mes:02d}-%"
        cur = self.conn.cursor()
        rows = cur.execute("""
            SELECT c.nombre AS categoria, SUM(t.monto) AS total
            FROM transacciones t
            JOIN categorias c ON t.categoria_id = c.id
            WHERE t.fecha LIKE ? AND t.tipo = ?
            GROUP BY c.nombre
            ORDER BY total DESC
        """, (patron, tipo)).fetchall()
        return [dict(r) for r in rows]

    def get_resumen_ultimos_meses(self, n: int = 6) -> list[dict]:
        """Retorna ingresos y egresos de los últimos n meses para gráfico de barras."""
        cur = self.conn.cursor()
        rows = cur.execute("""
            SELECT
                strftime('%Y-%m', fecha) AS mes,
                COALESCE(SUM(CASE WHEN tipo='ingreso' THEN monto ELSE 0 END), 0) AS ingresos,
                COALESCE(SUM(CASE WHEN tipo='egreso'  THEN monto ELSE 0 END), 0) AS egresos
            FROM transacciones
            GROUP BY mes
            ORDER BY mes DESC
            LIMIT ?
        """, (n,)).fetchall()
        return list(reversed([dict(r) for r in rows]))

    # ─────────────────────────────────────────

    def close(self):
        self.conn.close()
