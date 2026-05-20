import os
from ftplib import FTP
from tqdm import tqdm

class DataSUSCollector():
    def __init__(self):
        self.HOST = "ftp.datasus.gov.br"
        self.DIR = "/dissemin/publicos/SIM/CID10/DORES"
        self.OUT = "./datasus_dbc"
        self.REGIONS = {
            "Brasil" : "DOBR",
            "Acre" : "DOAC",
            "Alagoas": "DOAL", 
            "Amapá" : "DOAP", 
            "Amazonas" : "DOAM", 
            "Bahia": "DOBA",
            "Ceará" : "DOCE", 
            "Distrito Federal" : "DODF",
            "Espírito Santo" : "DOES",
            "Goiás": "DOGO",
            "Maranhão" : "DOMA",
            "Mato Grosso" : "DOMT",
            "Mato Grosso do Sul" : "DOMS",
            "Minas Gerais" : "DOMG",
            "Pará" : "DOPA",
            "Paraíba" : "DOPB",
            "Paraná" : "DOPR",
            "Pernambuco" : "DOPE",
            "Piauí" : "DOPI",
            "Rio de Janeiro" : "DORJ", 
            "Rio Grande do Norte" : "DORN",
            "Rio Grande do Sul" : "DORS",
            "Rondônia" : "DORO",
            "Roraima" : "DORR",
            "Santa Catarina": "DOSC",
            "São Paulo": "DOSP",
            "Sergipe" : "DOSE",
            "Tocantin" : "DOTO",
        }
        self.ftp = None
        os.makedirs(self.OUT, exist_ok=True)

    def _select_region(self):
        names = list(self.REGIONS.keys())

        items = [f"{idx:>2}. {name}" for idx, name in enumerate(names, start=1)]
        try:
            term_width = os.get_terminal_size().columns
        except OSError:
            term_width = 80

        col_width = max(len(item) for item in items) + 2
        max_cols = max(1, min(3, term_width // col_width))
        rows = (len(items) + max_cols - 1) // max_cols

        print("\n" + "=" * 64) #19
        print("--------------  Selecione a região dos registros  --------------")
        print("=" * 64)

        for row in range(rows):
            line = []
            for col in range(max_cols):
                idx = row + col * rows
                if idx < len(items):
                    line.append(items[idx].ljust(col_width))
            print("".join(line).rstrip())

        while True:
            choice = input("\nDigite o numero da regiao: ").strip()

            if not choice.isdigit():
                print("Entrada invalida. Use apenas numeros.")
                continue

            index = int(choice)
            if 1 <= index <= len(names):
                selected_name = names[index - 1]
                selected_code = self.REGIONS[selected_name]
                print(f"\nRegiao selecionada: {selected_name} ({selected_code})")
                print("-" * 42)
                return selected_code

            print("Numero fora do intervalo. Tente novamente.")

    def _connect(self):
        if self.ftp is None:
            # create and connect lazily
            self.ftp = FTP(self.HOST)
        self.ftp.login()
        self.ftp.cwd(self.DIR)
        return self.ftp
    
    def _download(self, filename):
        ftp = self.ftp
        local_path = os.path.join(self.OUT, filename)

        if os.path.exists(local_path):
            print(f"[SKIP] {filename}")
            return

        try:
            size = ftp.size(filename)

            with open(local_path, "wb") as f, tqdm(
                total=size,
                unit="B",
                unit_scale=True,
                desc=filename
            ) as bar:

                def callback(data):
                    f.write(data)
                    bar.update(len(data))

                ftp.retrbinary(f"RETR {filename}", callback)

            print(f"[OK] {filename}")

        except Exception as e:
            print(f"[ERRO] {filename} -> {e}")

    def get_files(self):
        ftp = self._connect()

        selected_prefix = self._select_region()

        print("\nListando arquivos no servidor...")
        files = ftp.nlst()

        # filtrar só .dbc
        files = [f for f in files if f.lower().endswith(".dbc")]
        files = [f for f in files if f.upper().startswith(selected_prefix)]

        print(f"Total de arquivos encontrados: {len(files)}")
        print("Iniciando download...\n")

        for f in files:
            self._download(f)

        ftp.quit()
        print("\n✅ DOWNLOAD FINALIZADO")

if __name__ == "__main__":
    # collector = DataSUSCollector()
    # collector.get_files()
    ...