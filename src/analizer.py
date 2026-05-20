import pandas as pd
import os

class Analizer():
	def __init__(self):
		self._columns_dict = {}
		self._seen_archives = 0

		# Diretório com os arquivos CSV (respeita a estrutura do workspace)
		self.FILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datasus_dbc', 'resultados'))

	def _save_columns(columns_dict: dict, column_name: str):
		columns_dict[column_name] = columns_dict.get(column_name, 0) + 1
		return columns_dict

	def list_columns(self):
		for archive in os.listdir(self.FILES_DIR):
			if archive.lower().endswith('csv'):
				csv_path = os.path.join(self.FILES_DIR, archive)
				try:
					if not os.path.exists(csv_path):
						raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

					df = pd.read_csv(csv_path, nrows=1)
					columns = df.columns

					for column_name in columns:
						self._save_columns(self._columns_dict, column_name)
					
					self._seen_archives += 1

				except Exception as e:
					print(f"Erro ao processar colunas no arquivo {archive}: {e}")
				
		sorted_columns = dict(sorted(self._columns_dict.items(), key=lambda item: item[1]))

		print(f"Arquivos análisados: {self._seen_archives}\n")
		print(f"Colunas:\n{sorted_columns}")
	
    