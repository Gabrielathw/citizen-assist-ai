"""Unus IA: orientação para jovens no primeiro emprego.
"""

import os

from assistente import Assistente, ler_opcao
from base_conhecimento import BaseConhecimento

# Caminhos relativos à pasta deste arquivo, para funcionar de qualquer lugar
PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BASE = os.path.join(PASTA, "data", "base_conhecimento.json")
CAMINHO_HISTORICO = os.path.join(PASTA, "data", "historico.json")
CAMINHO_CSV = os.path.join(PASTA, "data", "atendimentos.csv")


NOME_ASSISTENTE = "Unus IA"


def main():
    print("=" * 60)
    print(f" {NOME_ASSISTENTE} - seu assistente virtual para o primeiro emprego")
    print(" Tire dúvidas sobre documentos, trabalho e direitos")
    print("-" * 60)
    print(" Aviso: Este assistente NÃO é um canal oficial.")
    print(" Aviso:Não digite dados pessoais (nome, CPF, telefone, e-mail).")
    print("=" * 60)

    base = BaseConhecimento(CAMINHO_BASE)
    if not base.carregar():
        print("Não foi possível iniciar o assistente sem a base de conhecimento.")
        print("Verifique o arquivo data/base_conhecimento.json e tente de novo.")
        return

    assistente = Assistente(NOME_ASSISTENTE, base, CAMINHO_HISTORICO, CAMINHO_CSV)

    while True:
        print("\n=== Menu principal ===")
        print("1. Fazer uma pergunta")
        print("2. Navegar por categorias")
        print("3. Ver indicadores")
        print("4. Exportar atendimentos (CSV)")
        print("0. Sair")
        opcao = ler_opcao("Escolha uma opção: ", 0, 4)

        if opcao == 1:
            assistente.perguntar()
        elif opcao == 2:
            assistente.navegar()
        elif opcao == 3:
            assistente.indicadores()
        elif opcao == 4:
            assistente.exportar_csv()
        else:
            assistente.pedir_facilidade()
            assistente.exportar_csv()
            print(f"Obrigado por usar o {NOME_ASSISTENTE}. Até logo!")
            break


if __name__ == "__main__":
    main()
