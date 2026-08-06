from rich.console import Console
from rich.panel import Panel
from rich.align import Align
import questionary

console = Console()


def titulo():
    console.clear()

    console.print()

    console.print(
        Panel.fit(
            "[bold cyan]ETL DataSUS[/bold cyan]\n"
            "[white]Download • Conversão • Limpeza[/white]",
            border_style="cyan",
        ),
        justify="center",
    )

    console.print()


def menu_principal():

    titulo()

    return questionary.select(
        "Escolha uma opção:",
        choices=[
            "📥 Baixar arquivos do DATASUS",
            "🔄 Converter arquivos (.dbc → .csv)",
            "🧹 Limpar arquivos convertidos",
            "🚪 Sair",
        ],
    ).ask()


def selecionar_multiplos(arquivos, titulo_menu):

    titulo()

    return questionary.checkbox(
        titulo_menu,
        choices=arquivos,
        validate=lambda x: True if x else "Selecione pelo menos um arquivo.",
    ).ask()

def menu_continuar(opcoes):

    titulo()

    return questionary.select(
        "Próxima etapa:",
        choices=opcoes + ["⬅ Voltar ao menu principal"],
    ).ask()