"""
3_api_server.py - REST API per la consultazione del Framework GRC
Esecuzione: uvicorn 3_api_server:app --reload
"""

import sqlite3
import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI(
    title="API Framework Nazionale Cybersecurity 2025",
    version="2.1.0"
)

DB_PATH = "fncdp_2025.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/controlli")
def lista_controlli(funzione: Optional[str] = None, cerca: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()

    query = """
    SELECT s.id, s.descrizione, c.codice as categoria, c.codice_funzione as funzione
    FROM sottocategorie s
    JOIN categorie c ON s.codice_categoria = c.codice
    WHERE 1=1
    """
    params = []

    if funzione:
        query += " AND c.codice_funzione = ?"
        params.append(funzione.upper())

    if cerca:
        query += " AND (s.descrizione LIKE ? OR s.id LIKE ?)"
        params.append(f"%{cerca}%")
        params.append(f"%{cerca}%")

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return {"totale": len(rows), "dati": rows}


@app.get("/controlli/{id_controllo}")
def dettaglio_controllo(id_controllo: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sottocategorie WHERE id = ?", (id_controllo.upper(),))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Controllo non trovato")

    cursor.execute("SELECT riferimento FROM riferimenti_normativi WHERE id_sottocategoria = ?", (id_controllo.upper(),))
    riferimenti = [r["riferimento"] for r in cursor.fetchall()]

    risultato = dict(row)
    risultato["riferimenti_normativi"] = riferimenti
    conn.close()

    return risultato

    

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="127.0.0.1", port=8000, reload=True)