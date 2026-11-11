"""Classe BaseConhecimento: guarda todas as orientações e faz a busca por pontuação."""

import json

from orientacao import Orientacao

# Dicionário para trocar letras com acento por letras sem acento
ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c",
           "º": "o", "ª": "a"}  # "º" e "ª" para que "13º" vire "13o"

# Campos que toda orientação precisa ter no JSON
CAMPOS = ("id", "categoria", "titulo", "palavras_chave", "resposta",
          "documentos", "onde", "fonte", "verificado_em")

# Regras de pontuação (mesmos valores do enunciado)
PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
TAMANHO_MINIMO_PALAVRA = 4


def normalizar(texto):
    """Deixa o texto em minúsculas, sem acentos e sem pontuação.

    Coloca um espaço no começo e no fim para que " sus " não seja
    encontrado dentro de outra palavra (por exemplo, "susto").
    """
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()\"'":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def registro_completo(registro):
    """Confere se um registro do JSON tem todos os campos obrigatórios."""
    if type(registro) != dict:
        return False
    for campo in CAMPOS:
        if campo not in registro:
            return False
    return True


class BaseConhecimento:
    """Lê o JSON, lista as categorias e busca a melhor orientação."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []  

    def carregar(self):
        """Lê o JSON e cria um objeto Orientacao para cada registro.

        Devolve True se deu certo e False se houve algum problema.
        """
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"Erro: o arquivo {self.caminho} não foi encontrado.")
            return False
        except json.JSONDecodeError:
            print(f"Erro: o arquivo {self.caminho} está corrompido (JSON inválido).")
            return False

        if type(dados) != list:
            print("Erro: a base de conhecimento deve ser uma lista de orientações.")
            return False

        self.orientacoes = []
        for registro in dados:
            if not registro_completo(registro):
                print("Aviso: uma orientação incompleta foi ignorada.")
                continue
            orientacao = Orientacao(
                registro["id"],
                registro["categoria"],
                registro["titulo"],
                registro["palavras_chave"],
                registro["resposta"],
                registro["documentos"],
                registro["onde"],
                registro["fonte"],
                registro["verificado_em"],
            )
            self.orientacoes.append(orientacao)

        if len(self.orientacoes) == 0:
            print("Erro: nenhuma orientação válida foi encontrada na base.")
            return False
        return True

    def categorias(self):
        """Devolve a lista de categorias, sem repetir, na ordem do JSON."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        """Devolve só as orientações de uma categoria."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria == categoria:
                lista.append(orientacao)
        return lista

    def pontuar(self, pergunta_normalizada, orientacao):
        """Calcula os pontos de uma orientação para a pergunta.

        +3 para cada palavra-chave que aparece na pergunta.
        +1 para cada palavra da pergunta (4 letras ou mais) que aparece no título.
        """
        pontos = 0

        for chave in orientacao.palavras_chave:
            if normalizar(chave) in pergunta_normalizada:
                pontos += PONTOS_PALAVRA_CHAVE

        palavras_titulo = normalizar(orientacao.titulo).split()
        palavras_pergunta = set(pergunta_normalizada.split())  
        for palavra in palavras_pergunta:
            if len(palavra) >= TAMANHO_MINIMO_PALAVRA and palavra in palavras_titulo:
                pontos += PONTOS_TITULO

        return pontos

    def buscar(self, pergunta):
        """Devolve uma lista de tuplas (pontos, orientacao), da maior para a menor.

        Só entram as orientações com pelo menos 1 ponto.
        """
        pergunta_normalizada = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta_normalizada, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))  
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados
