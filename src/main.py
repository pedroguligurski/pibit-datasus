from conversor import DataConversor
from datasus import DataSUSCollector


def main():
    collector = DataSUSCollector()

    # Captura a lista de arquivos validados e baixados nesta execução
    arquivos_baixados = collector.get_files()

    # Só inicializa o conversor se houver arquivos para processar
    if arquivos_baixados:
        conversor = DataConversor()
        conversor.convert_files(arquivos_baixados)
    else:
        print("\nNenhum arquivo novo ou filtrado para conversão.")


if __name__ == "__main__":
    main()