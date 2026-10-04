"""
 Modulo Core per l'elaborazione del Framework FNCDP 2025 v2.1
"""

import pandas as pd
import sqlite3
import os

EXCEL_PATH = "FNCDP_-_Edizione_2025_v2.1_-_Core.xlsx"
DB_PATH = "fncdp_2025.db"


def carica_framework(filepath=EXCEL_PATH):
    """
    Legge il file Excel del Framework (saltando la riga di titolo)
    e ricostruisce la gerarchia completa per ogni sottocategoria.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File non trovato: {filepath}")

    # Mappatura delle colonne dell'Excel originale (riga 2)
    df_raw = pd.read_excel(filepath, skiprows=1)
    df_raw.columns = ['Function', 'Category', 'Subcategory', 'Informative References']

    funzione_corrente = ""
    categoria_corrente = ""
    dati = []

    for _, riga in df_raw.iterrows():
        fn = riga['Function']
        cat = riga['Category']
        sub = riga['Subcategory']
        ref = riga['Informative References']

        # Aggiorna la funzione o categoria corrente quando presente nella riga
        if pd.notna(fn):
            funzione_corrente = str(fn).strip()
        if pd.notna(cat):
            categoria_corrente = str(cat).strip()

        # Elabora la riga se contiene una sottocategoria (controllo)
        if pd.notna(sub):
            sub_str = str(sub).strip()

            # Estrazione ID e Descrizione (es: "GV.OC-01: La missione..." -> ID: "GV.OC-01")
            parts = sub_str.split(":", 1)
            sub_id = parts[0].strip() if len(parts) > 1 else sub_str
            sub_desc = parts[1].strip() if len(parts) > 1 else sub_str

            # Estrazione codici sintetici (es: "GV" da "GOVERN (GV)...")
            cod_fn = funzione_corrente.split("(")[1].split(")")[0] if "(" in funzione_corrente else "N/D"
            cod_cat = categoria_corrente.split("(")[1].split(")")[0] if "(" in categoria_corrente else "N/D"

            # Conversione dei riferimenti normativi in lista pulita
            riferimenti = [r.strip() for r in str(ref).split("\n") if r.strip()] if pd.notna(ref) else []

            dati.append({
                "codice_funzione": cod_fn,
                "funzione": funzione_corrente,
                "codice_categoria": cod_cat,
                "categoria": categoria_corrente,
                "id_sottocategoria": sub_id,
                "descrizione_sottocategoria": sub_desc,
                "sottocategoria_completa": sub_str,
                "riferimenti_lista": riferimenti,
                "riferimenti_str": ", ".join(riferimenti),
                "num_riferimenti": len(riferimenti)
            })

    return pd.DataFrame(dati)


def crea_database_sqlite(excel_path=EXCEL_PATH, db_path=DB_PATH):
    """Salva la struttura del framework in un database SQLite relazionale."""
    df = carica_framework(excel_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS funzioni (
        codice TEXT PRIMARY KEY,
        nome_completo TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS categorie (
        codice TEXT PRIMARY KEY,
        nome_completo TEXT NOT NULL,
        codice_funzione TEXT
    );
    CREATE TABLE IF NOT EXISTS sottocategorie (
        id TEXT PRIMARY KEY,
        descrizione TEXT NOT NULL,
        codice_categoria TEXT
    );
    CREATE TABLE IF NOT EXISTS riferimenti_normativi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_sottocategoria TEXT,
        riferimento TEXT NOT NULL
    );
    """)

    # Popolamento tabelle
    for cod, grp in df.groupby("codice_funzione"):
        cursor.execute("INSERT OR REPLACE INTO funzioni VALUES (?, ?)", (cod, grp["funzione"].iloc[0]))

    for cod, grp in df.groupby("codice_categoria"):
        cursor.execute("INSERT OR REPLACE INTO categorie VALUES (?, ?, ?)", 
                       (cod, grp["categoria"].iloc[0], grp["codice_funzione"].iloc[0]))

    for _, row in df.iterrows():
        cursor.execute("INSERT OR REPLACE INTO sottocategorie VALUES (?, ?, ?)", 
                       (row["id_sottocategoria"], row["descrizione_sottocategoria"], row["codice_categoria"]))
        for ref in row["riferimenti_lista"]:
            cursor.execute("INSERT INTO riferimenti_normativi (id_sottocategoria, riferimento) VALUES (?, ?)", 
                           (row["id_sottocategoria"], ref))

    conn.commit()
    conn.close()
    print(f"Database SQLite creato con successo: {db_path}")


if __name__ == "__main__":
    crea_database_sqlite()