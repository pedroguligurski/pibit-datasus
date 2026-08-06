import os
import pandas as pd
from dbctodbf import DBCDecompress
from dbfread import DBF


class DataConversor:

    def __init__(self):
        self.DIR = "datasus_dbc"
        self.OUTPUT_DIR = os.path.join(self.DIR, "resultados")
        self.dbc = DBCDecompress()
        self.remover_nulos = True  # valor padrão, perguntado em limpar_arquivos
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

    def _carregar_colunas_desejadas(self):
        caminho_config = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "colunas_desejadas.txt"
            )
        )

        colunas = []
        if os.path.exists(caminho_config):
            with open(caminho_config, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.strip()
                    if linha and not linha.startswith("#"):
                        colunas.append(linha)
        return colunas

    def _perguntar_remover_nulos(self):
        print("\n" + "=" * 64)
        print("--------------  Remoção de linhas com valores nulos  --------------")
        print("=" * 64)
        print("1. Sim, remover linhas com valores nulos/vazios")
        print("2. Não, manter todas as linhas (nulos ficam como NaN/vazio)")

        while True:
            choice = input("\nDigite o número correspondente (1 ou 2): ").strip()
            if choice == "1":
                self.remover_nulos = True
                print("-> Remoção de nulos ATIVADA.")
                return
            elif choice == "2":
                self.remover_nulos = False
                print("-> Remoção de nulos DESATIVADA. Linhas com nulos serão mantidas.")
                return
            print("Opção inválida. Escolha 1 ou 2.")

    def limpar_e_filtrar(self, df):
        """
        Aplica a lógica de filtragem de colunas e limpeza de registros de forma segura.
        """
        colunas_desejadas = self._carregar_colunas_desejadas()
        usando_filtro_colunas = False
        colunas_existentes = []

        if colunas_desejadas:
            colunas_existentes = [col for col in colunas_desejadas if col in df.columns]
            colunas_nao_encontradas = set(colunas_desejadas) - set(colunas_existentes)

            if colunas_nao_encontradas:
                print(f"   ⚠️ Algumas colunas solicitadas não existem neste arquivo: {list(colunas_nao_encontradas)}")

            if colunas_existentes:
                df = df[colunas_existentes]
                usando_filtro_colunas = True
                print(f"   ➔ Mantidas {len(colunas_existentes)} colunas selecionadas.")
            else:
                print("   ⚠️ Nenhuma das colunas listadas foi encontrada no arquivo. Mantendo todas por segurança.")
        else:
            print("   ℹ Nenhuma coluna especificada em 'colunas_desejadas.txt'. Mantendo todas as colunas originais.")

        total_inicial = len(df)

        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(r'^\s*$', pd.NA, regex=True)

        if self.remover_nulos:
            if usando_filtro_colunas:
                df = df.dropna(subset=colunas_existentes, how='any')
            else:
                df = df.dropna(how='all')
        else:
            print("   ℹ Remoção de nulos desativada. Linhas com valores vazios serão mantidas.")

        total_final = len(df)
        removidos = total_inicial - total_final
        if removidos > 0:
            print(f"   ➔ Limpeza: {removidos} linhas vazias ou inválidas foram removidas ({total_final} restantes).")
        else:
            print(f"   ➔ Limpeza: Nenhuma linha foi removida ({total_final} registros mantidos).")

        return df

    def convert_files(self, file_list=None):
        """Converte arquivos .dbc para .csv, SEM aplicar limpeza (conversão bruta)."""
        arquivos_para_processar = (
            file_list if file_list is not None else os.listdir(self.DIR)
        )

        if not arquivos_para_processar:
            print("Nenhum arquivo para processar.")
            return []

        print(f"\nIniciando conversão de {len(arquivos_para_processar)} arquivos...")
        convertidos = []

        for archive in arquivos_para_processar:
            if archive.lower().endswith(".dbc"):
                try:
                    dbc_path = os.path.join(self.DIR, archive)
                    dbf_path = os.path.join(self.OUTPUT_DIR, archive.replace(".dbc", ".dbf"))
                    csv_path = os.path.join(self.OUTPUT_DIR, archive.replace(".dbc", ".csv"))
                    csv_name = os.path.basename(csv_path)

                    if os.path.exists(csv_path):
                        print(f"Pulando, já existe: {csv_path}")
                        convertidos.append(csv_name)
                        continue

                    print(f"Processando: {archive}")

                    self.dbc.decompressFile(dbc_path, dbf_path)

                    table = DBF(dbf_path, encoding="latin1")
                    df = pd.DataFrame(iter(table))

                    df.to_csv(csv_path, index=False)

                    os.remove(dbf_path)

                    print(f"✔ OK: {csv_path}")
                    convertidos.append(csv_name)
                except Exception as e:
                    print(f"✖ Erro em {archive}: {e}")

        print("Conversão concluída.")
        return convertidos

    def limpar_arquivos(self, file_list=None):
        """Aplica filtragem de colunas e limpeza de nulos em .csv já convertidos (sobrescreve o arquivo)."""
        arquivos_para_processar = (
            file_list if file_list is not None else os.listdir(self.OUTPUT_DIR)
        )
        arquivos_para_processar = [f for f in arquivos_para_processar if f.lower().endswith(".csv")]

        if not arquivos_para_processar:
            print("Nenhum arquivo .csv para limpar.")
            return

        self._perguntar_remover_nulos()

        print(f"\nIniciando limpeza de {len(arquivos_para_processar)} arquivos...")

        for archive in arquivos_para_processar:
            try:
                csv_path = os.path.join(self.OUTPUT_DIR, archive)

                if not os.path.exists(csv_path):
                    print(f"✖ Arquivo não encontrado: {csv_path}")
                    continue

                print(f"Limpando: {archive}")

                df = pd.read_csv(csv_path, low_memory=False)
                df_limpo = self.limpar_e_filtrar(df)
                df_limpo.to_csv(csv_path, index=False)

                print(f"✔ OK: {csv_path}")
            except Exception as e:
                print(f"✖ Erro em {archive}: {e}")

        print("Limpeza concluída.")


if __name__ == "__main__":
    pass