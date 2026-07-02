import os
from ftplib import FTP
from tqdm import tqdm

class DataSUSCollector():
    def __init__(self):
        self.HOST = "ftp.datasus.gov.br"
        self.DIR_SIM = "/dissemin/publicos/SIM/CID10/DORES"
        self.DIR_SIH = "/dissemin/publicos/SIHSUS/200801_/Dados"

        self.OUT = "./datasus_dbc"
        
        self.REGIONS = {
            "Brasil" : "BR", "Acre" : "AC", "Alagoas": "AL", "Amapá" : "AP", 
            "Amazonas" : "AM", "Bahia": "BA", "Ceará" : "CE", "Distrito Federal" : "DF",
            "Espírito Santo" : "ES", "Goiás": "GO", "Maranhão" : "MA", "Mato Grosso" : "MT",
            "Mato Grosso do Sul" : "MS", "Minas Gerais" : "MG", "Pará" : "PA", 
            "Paraíba" : "PB", "Paraná" : "PR", "Pernambuco" : "PE", "Piauí" : "PI",
            "Rio de Janeiro" : "RJ", "Rio Grande do Norte" : "RN", "Rio Grande do Sul" : "RS",
            "Rondônia" : "RO", "Roraima" : "RR", "Santa Catarina": "SC", "São Paulo": "SP",
            "Sergipe" : "SE", "Tocantins" : "TO"
        }
        
        self.ftp = None
        self.selected_system = None
        self.selected_uf = None
        self.start_date = None
        self.end_date = None
        
        os.makedirs(self.OUT, exist_ok=True)

    def _select_system(self):
        print("\n" + "=" * 64)
        print("--------------         Selecione o Sistema         --------------")
        print("=" * 64)
        print("1. SIM (Sistema de Informações sobre Mortalidade)")
        print("2. SIH (Sistema de Informações Hospitalares - RD / AIH Reduzidas)")
        
        while True:
            choice = input("\nDigite o número correspondente (1 ou 2): ").strip()
            if choice == "1":
                self.selected_system = "SIM"
                return
            elif choice == "2":
                self.selected_system = "SIH"
                return
            print("Opção inválida. Escolha 1 ou 2.")

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

        print("\n" + "=" * 64)
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
                self.selected_uf = self.REGIONS[selected_name]
                print(f"\nRegião selecionada: {selected_name} ({self.selected_uf})")
                print("-" * 42)
                return

            print("Numero fora do intervalo. Tente novamente.")

    def _get_date_range(self):
        print("\n" + "=" * 64)
        print("--------------       Defina o Range de Datas       --------------")
        print("=" * 64)
        print("Use o formato AAAAMM (Exemplo: 202201 para Janeiro de 2022)")
        
        while True:
            start = input("Data INICIAL (AAAAMM): ").strip()
            end = input("Data FINAL (AAAAMM): ").strip()
            
            if (len(start) == 6 and start.isdigit()) and (len(end) == 6 and end.isdigit()):
                if int(start) <= int(end):
                    self.start_date = start
                    self.end_date = end
                    return
                else:
                    print("Erro: A data inicial não pode ser maior que a data final.")
            else:
                print("Formato inválido! Certifique-se de digitar exatamente 6 números (AAAAMM).")

    def _connect(self):
        if self.ftp is None:
            self.ftp = FTP(self.HOST)
        self.ftp.login()
        
        target_dir = self.DIR_SIM if self.selected_system == "SIM" else self.DIR_SIH
        self.ftp.cwd(target_dir)
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

    def _filter_files(self, files):
        prefix = "DO" if self.selected_system == "SIM" else "RD"
        
        start_year = int(self.start_date[:4])
        start_month = int(self.start_date[4:])
        end_year = int(self.end_date[:4])
        end_month = int(self.end_date[4:])
        
        # Lista de todas as UFs reais (removendo o 'BR')
        valid_ufs = [v for v in self.REGIONS.values() if v != "BR"]
        
        filtered = []
        for f in files:
            f_upper = f.upper()
            if not f_upper.endswith(".DBC") or not f_upper.startswith(prefix):
                continue
            
            # Tratamento especial para a opção "Brasil"
            if self.selected_uf == "BR":
                if self.selected_system == "SIM":
                    if not f_upper.startswith("DOBR"):
                        continue
                    date_part = f_upper[4:-4] # Ex: DOBR2022.dbc -> 2022
                else: # SIH
                    # Para o SIH Brasil, aceita arquivos de qualquer UF válida (RDSP, RDRJ...)
                    uf_found = None
                    for uf in valid_ufs:
                        if f_upper.startswith(f"RD{uf}"):
                            uf_found = uf
                            break
                    if not uf_found:
                        continue
                    date_part = f_upper[2 + len(uf_found):-4] # Ex: RDSP2201.dbc -> 2201
            else:
                # Filtragem por UF específica selecionada
                target_prefix = f"{prefix}{self.selected_uf}".upper()
                if not f_upper.startswith(target_prefix):
                    continue
                date_part = f_upper[len(target_prefix):-4]
            
            # Validação do Range de Datas
            if self.selected_system == "SIH":
                # Formato SIH: YYMM (Ex: 2201)
                if len(date_part) >= 4 and date_part[:4].isdigit():
                    yy = int(date_part[:2])
                    mm = int(date_part[2:4])
                    yyyy = 2000 + yy if yy < 70 else 1900 + yy
                    
                    file_val = yyyy * 100 + mm
                    start_val = start_year * 100 + start_month
                    end_val = end_year * 100 + end_month
                    
                    if start_val <= file_val <= end_val:
                        filtered.append(f)
            else:
                # Formato SIM: AAAA (Ex: 2022)
                if len(date_part) >= 4 and date_part[:4].isdigit():
                    file_year = int(date_part[:4])
                elif len(date_part) >= 2 and date_part[:2].isdigit():
                    yy = int(date_part[:2])
                    file_year = 2000 + yy if yy < 70 else 1900 + yy
                else:
                    continue
                
                if start_year <= file_year <= end_year:
                    filtered.append(f)
                    
        return filtered

    def get_files(self):
        self._select_system()
        self._select_region()
        self._get_date_range()
        
        ftp = self._connect()

        print("\nListando arquivos no servidor...")
        files = ftp.nlst()

        files = self._filter_files(files)

        print(f"Total de arquivos encontrados: {len(files)}")
        if len(files) == 0:
            print("Nenhum arquivo corresponde aos critérios selecionados.")
            ftp.quit()
            return
            
        print("Iniciando download...\n")

        for f in files:
            self._download(f)

        ftp.quit()
        print("\n✅ DOWNLOAD FINALIZADO")

        return files

if __name__ == "__main__":
    collector = DataSUSCollector()
    collector.get_files()