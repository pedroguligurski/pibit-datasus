import pandas as pd
from dbctodbf import DBCDecompress
from dbfread import DBF
import os

class DataConversor():
    def __init__(self):
        self.DIR = "datasus_dbc"
        self.OUTPUT_DIR = os.path.join(self.DIR, "resultados")
        self.dbc = DBCDecompress()
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)


    def convertAll(self):
        for archive in os.listdir(self.DIR):
            if archive.lower().endswith('.dbc'):
                try:
                    dbc_path = os.path.join(self.DIR, archive)
                    dbf_path = os.path.join(self.OUTPUT_DIR, archive.replace(".dbc", ".dbf"))
                    csv_path = os.path.join(self.OUTPUT_DIR, archive.replace(".dbc", ".csv"))

                    if os.path.exists(csv_path):
                        print(f"Pulando, já existe: {csv_path}")
                        continue

                    print(f"Processando: {archive}")

                    # 1. converter DBC -> DBF
                    self.dbc.decompressFile(dbc_path, dbf_path)

                    # 2. ler DBF
                    table = DBF(dbf_path, encoding="latin1")
                    df = pd.DataFrame(iter(table))

                    # 3. salvar CSV
                    df.to_csv(csv_path, index=False)

                    # 4. remover DBF temporário
                    os.remove(dbf_path)

                    print(f"✔ OK: {csv_path}")
                except Exception as e: 
                    print(f"✖ Erro em {archive}: {e}")

        print("Concluído.")

if __name__ == "__main__":
    ...
