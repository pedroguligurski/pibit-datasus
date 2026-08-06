import os
import questionary
from rich.console import Console
from rich.panel import Panel

from ui import selecionar_multiplos
from ui import menu_principal
from ui import menu_continuar

from datasus import DataSUSCollector
from conversor import DataConversor

# Inicializa o console do Rich para impressões coloridas e painéis
console = Console()

class Menu:
    def __init__(self):
        self.collector = DataSUSCollector()
        self.conversor = DataConversor()

    # ------------------------------------------------------------------
    # Utilitário de seleção de arquivos (agora com Checkbox)
    # ------------------------------------------------------------------
    def _selecionar_arquivos(self, diretorio, extensao, rotulo):

        if not os.path.isdir(diretorio):
            print("Diretório inexistente.")
            return []

        arquivos = sorted(
            f for f in os.listdir(diretorio)
            if f.lower().endswith(extensao)
        )

        if not arquivos:
            print("Nenhum arquivo encontrado.")
            return []

        return selecionar_multiplos(
            arquivos,
            f"Selecione os {rotulo}:"
        )

    # ------------------------------------------------------------------
    # Sub-menu de continuação (aparece após cada etapa)
    # ------------------------------------------------------------------
    def _perguntar_proxima_etapa(self, opcoes):

        nomes = [x[0] for x in opcoes]

        escolha = menu_continuar(nomes)

        if escolha == "⬅ Voltar ao menu principal":
            return

        for nome, callback in opcoes:
            if nome == escolha:
                callback()
                return

    # ------------------------------------------------------------------
    # Fluxos principais
    # ------------------------------------------------------------------
    def _fluxo_download(self):
        arquivos_baixados = self.collector.get_files()

        if not arquivos_baixados:
            console.print("\n[bold yellow]Nenhum arquivo novo ou filtrado para conversão.[/bold yellow]")
            input("\nPressione Enter para voltar ao menu...")
            return

        self._perguntar_proxima_etapa([
            ("Converter agora os arquivos baixados", lambda: self._fluxo_conversao(arquivos_baixados)),
        ])

    def _fluxo_conversao(self, arquivos=None):
        if arquivos is None:
            arquivos = self._selecionar_arquivos(self.conversor.DIR, ".dbc", "arquivos .dbc")
            if not arquivos:
                return

        convertidos = self.conversor.convert_files(arquivos)

        if not convertidos:
            input("\nPressione Enter para voltar ao menu...")
            return

        # Coloca a pausa aqui para você ver o resultado da conversão se não quiser limpar direto
        self._perguntar_proxima_etapa([
            ("Limpar agora os arquivos convertidos", lambda: self._fluxo_limpeza(convertidos)),
        ])

    def _fluxo_limpeza(self, arquivos=None):
        if arquivos is None:
            arquivos = self._selecionar_arquivos(self.conversor.OUTPUT_DIR, ".csv", "arquivos .csv")
            if not arquivos:
                return

        self.conversor.limpar_arquivos(arquivos)
        console.print("\n[bold green]Processo de limpeza finalizado![/bold green]")
        input("\nPressione Enter para voltar ao menu principal...")
    # ------------------------------------------------------------------
    # Menu principal
    # ------------------------------------------------------------------
    def executar(self):

        while True:

            escolha = menu_principal()

            if escolha.startswith("📥"):
                self._fluxo_download()

            elif escolha.startswith("🔄"):
                self._fluxo_conversao()

            elif escolha.startswith("🧹"):
                self._fluxo_limpeza()

            elif escolha.startswith("🚪"):
                break


if __name__ == "__main__":
    Menu().executar()