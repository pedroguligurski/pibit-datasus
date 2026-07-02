import os
import pandas as pd
from dbctodbf import DBCDecompress
from dbfread import DBF


class DataConversor:

    def __init__(self):
        self.DIR = "datasus_dbc"
        self.OUTPUT_DIR = os.path.join(self.DIR, "resultados")
        self.dbc = DBCDecompress()
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

    def limpar_e_filtrar(self, df):
        """
        Aplica a lógica de filtragem de colunas e limpeza de registros de forma segura.
        """
        # 1. Filtragem de Colunas
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

        # 2. Limpeza de Registros
        total_inicial = len(df)

        # A) Tratamento de strings e remoção de espaços em branco adicionais
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(r'^\s*$', pd.NA, regex=True)

        # B) Remoção inteligente de linhas contendo valores nulos/vazios
        if usando_filtro_colunas:
            # Se você escolheu colunas específicas, remove a linha se faltar dado em QUALQUER uma delas
            df = df.dropna(subset=colunas_existentes, how='any')
        else:
            # Se você está trazendo o arquivo completo (sem filtros), só remove se a linha INTEIRA for nula
            # Isso impede que uma coluna opcional vazia apague os dados do arquivo todo
            df = df.dropna(how='all')

        total_final = len(df)
        removidos = total_inicial - total_final
        if removidos > 0:
            print(f"   ➔ Limpeza: {removidos} linhas vazias ou inválidas foram removidas ({total_final} restantes).")
        else:
            print(f"   ➔ Limpeza: Nenhuma linha foi removida ({total_final} registros mantidos).")
        
        return df

    def convert_files(self, file_list=None):
        """Modificado para aceitar uma lista específica de arquivos da execução atual."""
        # Se nenhuma lista for passada, varre o diretório por padrão
        arquivos_para_processar = (
            file_list if file_list is not None else os.listdir(self.DIR)
        )

        if not arquivos_para_processar:
            print("Nenhum arquivo para processar.")
            return

        print(
            f"\nIniciando conversão de {len(arquivos_para_processar)} arquivos..."
        )

        for archive in arquivos_para_processar:
            if archive.lower().endswith(".dbc"):
                try:
                    dbc_path = os.path.join(self.DIR, archive)
                    dbf_path = os.path.join(
                        self.OUTPUT_DIR, archive.replace(".dbc", ".dbf")
                    )
                    csv_path = os.path.join(
                        self.OUTPUT_DIR, archive.replace(".dbc", ".csv")
                    )

                    if os.path.exists(csv_path):
                        print(f"Pulando, já existe: {csv_path}")
                        continue

                    print(f"Processando: {archive}")

                    # 1. converter DBC -> DBF
                    self.dbc.decompressFile(dbc_path, dbf_path)

                    # 2. ler DBF
                    table = DBF(dbf_path, encoding="latin1")
                    df = pd.DataFrame(iter(table))

                    # 3. Limpar e filtrar dados em memória
                    df_limpo = self.limpar_e_filtrar(df)

                    # 4. salvar CSV
                    df_limpo.to_csv(csv_path, index=False)

                    # 5. remover DBF temporário
                    os.remove(dbf_path)

                    print(f"✔ OK: {csv_path}")
                except Exception as e:
                    print(f"✖ Erro em {archive}: {e}")

        print("Concluído.")


if __name__ == "__main__":
    pass