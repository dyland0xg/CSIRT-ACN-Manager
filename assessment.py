"""
 Generazione Template di Valutazione e Calcolo Maturità
"""

import pandas as pd
from fncdp_core import carica_framework


def genera_excel_assessment(df, output_file="Assessment_Maturita.xlsx"):
    """Crea la scheda Excel da compilare per l'analisi di maturità (punteggi 0-5)."""
    df_export = df[[
        "codice_funzione", 
        "codice_categoria", 
        "id_sottocategoria", 
        "descrizione_sottocategoria"
    ]].copy()

    df_export["Maturita_Attuale (0-5)"] = 0
    df_export["Maturita_Target (0-5)"] = 3
    df_export["Owner"] = ""
    df_export["Note / Evidenze"] = ""

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_export.to_excel(writer, sheet_name="Assessment_FNCDP", index=False)
    
    print(f"File di assessment generato: {output_file}")


def calcola_sintesi_maturita(file_compilato="Assessment_Maturita.xlsx"):
    """Legge il file compilato e restituisce una tabella riepilogativa numerica."""
    df_compilato = pd.read_excel(file_compilato, sheet_name="Assessment_FNCDP")

    # Aggregazione delle medie per Funzione e Categoria
    riepilogo_funzioni = df_compilato.groupby("codice_funzione").agg(
        Media_Attuale=("Maturita_Attuale (0-5)", "mean"),
        Media_Target=("Maturita_Target (0-5)", "mean"),
        Totale_Controlli=("id_sottocategoria", "count")
    ).round(2).reset_index()

    return riepilogo_funzioni


if __name__ == "__main__":
    df = carica_framework()
    genera_excel_assessment(df)