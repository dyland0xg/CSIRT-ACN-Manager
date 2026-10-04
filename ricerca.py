"""
 Ricerca e Mappatura Normativa
"""

import pandas as pd
from fncdp_core import carica_framework


class MotoreRicercaFNCDP:
    def __init__(self, df):
        self.df = df

    def cerca_testo(self, testo):
        """Cerca una parola chiave nei dettagli dei controlli."""
        testo = testo.lower()
        maschera = self.df["sottocategoria_completa"].str.lower().str.contains(testo)
        return self.df[maschera][["id_sottocategoria", "descrizione_sottocategoria", "codice_funzione"]]

    def cerca_normativa(self, sigla_norma):
        """Filtra le sottocategorie legate a uno specifico standard (es: 'GDPR', 'ISO', 'SP 800-53')."""
        sigla = sigla_norma.lower()
        risultati = []

        for _, row in self.df.iterrows():
            match = [ref for ref in row["riferimenti_lista"] if sigla in ref.lower()]
            if match:
                risultati.append({
                    "id_sottocategoria": row["id_sottocategoria"],
                    "descrizione": row["descrizione_sottocategoria"],
                    "riferimenti_trovati": ", ".join(match)
                })

        return pd.DataFrame(risultati)


if __name__ == "__main__":
    df = carica_framework()
    motore = MotoreRicercaFNCDP(df)

    print("\n--- CONTROLLI LEGATI AL GDPR ---")
    risultati_gdpr = motore.cerca_normativa("GDPR")
    print(risultati_gdpr.head(5).to_string(index=False))