"""Classe Assistente: conversa com o cidadão, guarda o histórico e calcula os indicadores."""

import csv
import json
import time
from datetime import datetime

# Limites de confiança (mesmos valores do enunciado)
CONFIANCA_ALTA = 6
CONFIANCA_MEDIA = 3

TAMANHO_MAXIMO_PERGUNTA = 200
MINIMO_DIGITOS_DADO_PESSOAL = 8

# Colunas do histórico e do CSV
CAMPOS_HISTORICO = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
                    "ajudou", "tentativas", "tempo_segundos", "facilidade"]


def ler_texto(mensagem):
    """Lê o que a pessoa digitou. Se ela apertar Ctrl+C, vira "0" (voltar/sair)."""
    try:
        return input(mensagem).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "0"


def ler_opcao(mensagem, minimo, maximo):
    """Pede um número inteiro entre minimo e maximo, até a pessoa digitar certo."""
    while True:
        texto = ler_texto(mensagem)
        try:
            opcao = int(texto)
        except ValueError:
            print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")
            continue
        if minimo <= opcao <= maximo:
            return opcao
        print(f"Opção fora da faixa. Digite um número de {minimo} a {maximo}.")


def ler_sim_nao(mensagem):
    """Pede "s" ou "n" até a resposta ser válida. Devolve True para "s"."""
    while True:
        resposta = ler_texto(mensagem).lower()
        if resposta == "s" or resposta == "sim":
            return True
        if resposta == "n" or resposta == "nao" or resposta == "não" or resposta == "0":
            return False
        print("Resposta inválida. Digite só s (sim) ou n (não).")
        if len(resposta) > 3:
            # Parece que a pessoa digitou uma nova pergunta no lugar do s/n
            print("Para fazer outra pergunta, primeiro responda s ou n aqui.")


def contem_dado_pessoal(texto):
    """True se o texto parece ter CPF, telefone, CEP ou e-mail.

    Regra do enunciado: 8 ou mais dígitos OU o símbolo @.
    Contamos todos os dígitos da frase, então "123.456.789-00" também é bloqueado.
    """
    if "@" in texto:
        return True
    digitos = 0
    for caractere in texto:
        if caractere.isdigit():
            digitos += 1
    return digitos >= MINIMO_DIGITOS_DADO_PESSOAL


def tem_letra(texto):
    """True se o texto tem pelo menos uma letra (bloqueia entradas como "???")."""
    for caractere in texto:
        if caractere.isalpha():
            return True
    return False


def nivel_confianca(pontos):
    """Transforma a pontuação em nível de confiança."""
    if pontos >= CONFIANCA_ALTA:
        return "ALTA"
    if pontos >= CONFIANCA_MEDIA:
        return "MÉDIA"
    return None  # menos de 3 pontos: não encontrou


class Assistente:
    """Faz o atendimento, guarda o histórico e calcula os indicadores."""

    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base                  # objeto BaseConhecimento (composição)
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.historico = self.carregar_historico()
        # Posição onde começam os atendimentos desta vez que o programa foi aberto
        self.inicio_sessao = len(self.historico)

    def carregar_historico(self):
        """Lê o histórico salvo. Se não existir ou estiver corrompido, começa vazio."""
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if type(dados) == list:
                return dados
            print("Aviso: histórico em formato inesperado. Começando um histórico novo.")
        except FileNotFoundError:
            pass  # primeira vez que o programa roda: ainda não existe histórico
        except json.JSONDecodeError:
            print("Aviso: o histórico estava corrompido. Começando um histórico novo.")
        return []

    def salvar_historico(self):
        """Grava a lista de atendimentos no arquivo historico.json."""
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            print("Aviso: não foi possível salvar o histórico.")

    def perguntar(self):
        """Atendimento por pergunta em texto livre, usando a busca por pontuação."""
        print("\nDica: não digite nome, CPF, telefone, e-mail ou endereço.")
        while True:
            inicio = time.time()
            tentativas = 0
            ultima_pergunta = ""
            encontrou = False
            id_orientacao = None

            while True:  # um atendimento pode ter várias tentativas
                pergunta = ler_texto("\nDigite sua dúvida (0 para voltar): ")

                if pergunta == "0":
                    # Se a pessoa já tentou e desistiu, conta como dúvida não resolvida
                    if tentativas > 0:
                        self.registrar("pergunta", ultima_pergunta, id_orientacao,
                                       encontrou, False, tentativas, inicio)
                    return
                if pergunta == "":
                    print("Você não digitou nada. Escreva sua dúvida, por exemplo: como tiro o CPF?")
                    continue
                if contem_dado_pessoal(pergunta):
                    # Não guarda, não repete e não registra o que foi digitado
                    print("Atenção: não digite CPF, telefone, e-mail ou outros dados pessoais. Reescreva.")
                    continue
                if len(pergunta) > TAMANHO_MAXIMO_PERGUNTA:
                    print(f"Sua pergunta ficou muito longa. Use até {TAMANHO_MAXIMO_PERGUNTA} caracteres.")
                    continue
                if not tem_letra(pergunta):
                    print("Não entendi. Escreva sua dúvida com palavras, por exemplo: carteira de trabalho.")
                    continue

                tentativas += 1
                ultima_pergunta = pergunta
                resultados = self.base.buscar(pergunta)
                if len(resultados) > 0:
                    melhor_pontos = resultados[0][0]
                else:
                    melhor_pontos = 0
                confianca = nivel_confianca(melhor_pontos)

                if confianca is None:
                    encontrou = False
                    id_orientacao = None
                    print("\nNão encontrei uma orientação para essa dúvida.")
                    print("Tente outras palavras ou veja as categorias: "
                          + ", ".join(self.base.categorias()) + ".")
                    if ler_sim_nao("Quer tentar com outras palavras? (s/n): "):
                        continue
                    self.registrar("pergunta", pergunta, None, False, False, tentativas, inicio)
                    break

                encontrou = True
                pontos, melhor = resultados[0]  # desempacota a tupla (pontos, orientacao)
                id_orientacao = melhor.id
                print(f"\nConfiança da resposta: {confianca} ({pontos} pontos)")
                melhor.exibir()

                # Mostra até duas alternativas que também tenham 3 pontos ou mais
                alternativas = []
                for pontos_alt, orientacao_alt in resultados[1:3]:
                    if pontos_alt >= CONFIANCA_MEDIA:
                        alternativas.append((pontos_alt, orientacao_alt))
                if len(alternativas) > 0:
                    print("\nOutras orientações que podem ajudar:")
                    for pontos_alt, orientacao_alt in alternativas:
                        print(f"  - {orientacao_alt.titulo} [{orientacao_alt.categoria}] ({pontos_alt} pontos)")

                if ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                    self.registrar("pergunta", pergunta, id_orientacao, True, True, tentativas, inicio)
                    break
                if ler_sim_nao("Quer reformular a pergunta? (s/n): "):
                    continue
                self.registrar("pergunta", pergunta, id_orientacao, True, False, tentativas, inicio)
                break

    def navegar(self):
        """Atendimento por categorias numeradas, com 0 para voltar em todas as telas."""
        while True:
            inicio = time.time()
            categorias = self.base.categorias()
            print("\n=== Categorias ===")
            numero = 1
            for categoria in categorias:
                print(f"{numero}. {categoria}")
                numero += 1
            print("0. Voltar")
            escolha = ler_opcao("Escolha uma categoria: ", 0, len(categorias))
            if escolha == 0:
                return
            categoria = categorias[escolha - 1]

            while True:
                orientacoes = self.base.por_categoria(categoria)
                print(f"\n=== {categoria} ===")
                numero = 1
                for orientacao in orientacoes:
                    print(f"{numero}. {orientacao.titulo}")
                    numero += 1
                print("0. Voltar")
                escolha = ler_opcao("Escolha uma orientação: ", 0, len(orientacoes))
                if escolha == 0:
                    break
                orientacao = orientacoes[escolha - 1]
                orientacao.exibir()
                ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
                self.registrar("categoria", orientacao.titulo, orientacao.id,
                               True, ajudou, 1, inicio)
                inicio = time.time()  # o próximo atendimento começa agora

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, inicio):
        """Guarda um atendimento no histórico (lista de dicionários) e salva o JSON."""
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(time.time() - inicio, 1),
            "facilidade": None,  # preenchida quando a pessoa sai e dá a nota
        }
        self.historico.append(atendimento)
        self.salvar_historico()

    def pedir_facilidade(self):
        """Ao sair, pede uma nota de 1 a 5 e grava nos atendimentos desta sessão."""
        atendimentos_sessao = self.historico[self.inicio_sessao:]
        if len(atendimentos_sessao) == 0:
            return  # ninguém foi atendido agora: não há o que avaliar
        nota = ler_opcao("\nDe 1 a 5, quão fácil foi usar o assistente? (0 para pular) ", 0, 5)
        if nota == 0:
            return  # a pessoa preferiu não dar nota
        for atendimento in atendimentos_sessao:
            atendimento["facilidade"] = nota
        self.salvar_historico()

    def indicadores(self):
        """Calcula e mostra os indicadores. Devolve um dicionário com os valores."""
        total = len(self.historico)
        print("\n=== Indicadores ===")
        if total == 0:
            print("Ainda não há atendimentos registrados.")
            return {}

        # Um único for soma tudo o que precisamos
        encontrados = 0
        ajudaram = 0
        soma_tempo = 0
        soma_tentativas = 0
        notas = []
        sem_solucao = []
        for atendimento in self.historico:
            if atendimento["encontrou"]:
                encontrados += 1
            if atendimento["ajudou"]:
                ajudaram += 1
            else:
                sem_solucao.append(atendimento["pergunta"])
            soma_tempo += atendimento["tempo_segundos"]
            soma_tentativas += atendimento["tentativas"]
            if atendimento["facilidade"] is not None:
                notas.append(atendimento["facilidade"])

        resultado = {
            "total": total,
            "encontrada_pct": round(encontrados / total * 100, 1),
            "ajudou_pct": round(ajudaram / total * 100, 1),
            "tempo_medio": round(soma_tempo / total, 1),
            "tentativas_media": round(soma_tentativas / total, 1),
            "facilidade": None,
            "sem_solucao": sem_solucao,
        }
        if len(notas) > 0:
            resultado["facilidade"] = round(sum(notas) / len(notas), 1)

        print(f"Total de atendimentos:        {total}")
        print(f"Resposta encontrada:          {resultado['encontrada_pct']}%")
        print(f"Taxa de acerto (ajudou):      {resultado['ajudou_pct']}%")
        print(f"Tempo médio para encontrar:   {resultado['tempo_medio']} s")
        print(f"Tentativas por atendimento:   {resultado['tentativas_media']}")
        if resultado["facilidade"] is None:
            print("Facilidade de uso (1 a 5):    sem notas ainda")
        else:
            print(f"Facilidade de uso (1 a 5):    {resultado['facilidade']}")
        print("Dúvidas sem solução:")
        if len(sem_solucao) > 0:
            for pergunta in sem_solucao:
                print(f"  - {pergunta}")
        else:
            print("  (nenhuma)")
        return resultado

    def exportar_csv(self):
        """Exporta todos os atendimentos para CSV usando csv.DictWriter."""
        try:
            # encoding "utf-8-sig" e delimiter ";" fazem o Excel abrir com acentos e colunas certas
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_HISTORICO, delimiter=";")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
            print(f"Atendimentos exportados para {self.caminho_csv}.")
        except OSError:
            print("Não foi possível exportar o CSV. Feche o arquivo se ele estiver aberto no Excel.")
