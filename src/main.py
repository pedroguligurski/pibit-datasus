from datasus import DataSUSCollector
from conversor import DataConversor

def main():
    collector = DataSUSCollector()
    
    collector.get_files()
    
    conversor = DataConversor()

    conversor.convertAll()


if __name__ == "__main__":
    main()