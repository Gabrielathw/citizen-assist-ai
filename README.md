# Unus IA —  Assistente para Jovens no Primeiro Emprego

**Unus IA** é um assistente de terminal, em Python, que orienta jovens, que vão começar a trabalhar, sobre: **documentos, trabalho e direitos**, sempre com fonte oficial, data de verificação e aviso de que **não é um canal oficial**.

> Global Solution 2026.2 · 1CCPY · Pensamento Computacional e Automação com Python 

## Integrantes

| Nome completo | RM |
|---|---|
| Gabriela Campos | 572738 |
| Laura Pícari | 569914 |
| Lucas Neves | 572679 |

## Público e problema

**Público:** Jovens de 14 a 24 anos em busca do primeiro emprego (aprendiz, estágio ou primeiro registro).

**Problema:** Para começar a trabalhar, o jovem precisa de vários documentos (CPF, identidade, Carteira de Trabalho Digital, título de eleitor, alistamento) e de informações sobre direitos (estágio, Jovem Aprendiz, FGTS, 13º). A informação está espalhada em vários sites do governo, em linguagem técnica, e há sites falsos ou pagos que imitam os oficiais. O assistente reúne essas orientações em linguagem simples, com fonte oficial.

## ODS relacionados (Objetivos de Desenvolvimento Sustentável)

- **ODS 8 — Trabalho decente e crescimento econômico** (meta 8.6: reduzir a proporção de jovens sem emprego, educação ou formação)
- **ODS 4 — Educação de qualidade** (aprendizagem profissional e estágio ligados à escola)
- **ODS 16 — Paz, justiça e instituições eficazes** (acesso à informação sobre serviços públicos)

## Como executar

No terminal: 

```bash
python main.py
```

Menu principal:

```
1. Fazer uma pergunta
2. Navegar por categorias
3. Ver indicadores
4. Exportar atendimentos (CSV)
0. Sair
```

## Estrutura do projeto

```
citizen-assist-ai/
├── README.md
├── main.py                 
├── orientacao.py           
├── base_conhecimento.py    
├── assistente.py           
└── data/
    ├── base_conhecimento.json   
    ├── historico.json          
    └── atendimentos.csv         
```

**Composição das classes:**

```
Assistente
└── tem uma BaseConhecimento (atributo base)
    └── que tem uma lista de 17 objetos Orientacao (atributo orientacoes), um para cada registro do JSON: CPF, Identidade, Título de eleitor...
```

| Classe | Atributos | Métodos |
|---|---|---|
| `Orientacao` | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `exibir()` |
| `BaseConhecimento` | caminho, orientacoes | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()` |
| `Assistente` | nome, base, historico, caminho_historico, caminho_csv | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`, `pedir_facilidade()` |

## Regra de pontuação usada

A pergunta, as palavras-chave e o título são comparados **sem acentos, sem pontuação e em minúsculas** (função `normalizar()`). Além das letras do enunciado, `º` e `ª` viram `o` e `a`, para que "13º" seja entendido como "13o".

**Regra e Pontos:**

O assistente não “entende” a pergunta como uma IA. Ele compara palavras e dá uma nota a cada uma das 17 orientações:

 Palavra-chave da orientação que aparece na pergunta = +3 
Palavra da pergunta (4 letras ou mais) que aparece no título = +1 

| Melhor pontuação | Resultado |
|---|---|
| 6 ou mais | Confiança **ALTA** |
| 3 a 5 | Confiança **MÉDIA** |
| menos de 3 | "Não encontrei" + sugestão de categorias |


**Exemplo:** "Como tiro o título de eleitor?"
-> palavras-chave `titulo de eleitor` (+3) e `eleitor` (+3); palavras do título `titulo` (+1) e `eleitor` (+1) = **8 pontos, confiança ALTA**.

## Regras de atendimento

- **Navegação:** categorias e orientações numeradas, com "0 para voltar" em todas as telas.
- **Entradas inválidas:** letras no lugar de número, número fora da faixa, resposta vazia e s/n inválido nunca encerram o programa.
- **Dados pessoais:** perguntas com 8 ou mais dígitos ou com **@** são recusadas e não são registradas. O assistente nunca pede nome, CPF, telefone ou e-mail.
- **Outras entradas:** texto sem nenhuma letra, ex.: "???" ou com mais de 200 caracteres, recebe uma mensagem amigável.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos:** base JSON ausente ou corrompida mostra uma mensagem e encerra sem erro. Histórico ausente ou corrompido começa um histórico novo.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json`:

| Campo | Significado |
|---|---|
| data | data e hora do atendimento |
| origem | `pergunta` ou `categoria` |
| pergunta | texto digitado (ou título escolhido na navegação) |
| id_orientacao | id da orientação mostrada (vazio se não encontrou) |
| encontrou / ajudou | `true` ou `false` |
| tentativas | quantas perguntas a pessoa fez até resolver ou desistir |
| tempo_segundos | `round(time.time() - inicio, 1)` |
| facilidade | nota de 1 a 5 dada ao sair (aplicada a todos os atendimentos da sessão) |

**Como visualizar o CSV em formato de tabela:**

- **Excel:** abra o arquivo `data/atendimentos.csv` com dois cliques.
- **VS Code com a extensão Edit CSV:** instale em Extensões, abra o arquivo clicando com botão direito em *Edit csv* no canto superior direito para vê-lo como planilha.

## Fontes consultadas


| ID | Orientação | Fonte oficial | Data |
|---|---|---|---|
| 1 | CPF | https://www.gov.br/pt-br/servicos/inscrever-no-cpf | 09/11/2026 |
| 2 | Carteira de Identidade Nacional | https://www.gov.br/governodigital/pt-br/identidade/cin | 09/11/2026 |
| 3 | Título de eleitor | https://www.tse.jus.br/servicos-eleitorais/titulo-eleitoral/autoatendimento-eleitoral | 11/11/2026 |
| 4 | Alistamento militar | https://www.gov.br/pt-br/servicos/alistar-se-no-servico-militar-obrigatorio | 11/11/2026 |
| 5 | Carteira de Trabalho Digital | https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho | 05/11/2026 |
| 6 | Jovem Aprendiz | https://www.gov.br/trabalho-e-emprego/pt-br/noticias-e-conteudo/2026/julho/aprendizagem-profissional-regras-direitos-e-funcionamento-do-contrato-de-aprendizagem | 05/11/2026 |
| 7 | Estágio (Lei 11.788/2008) | https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/lei/l11788.htm | 06/11/2026 |
| 8 | Vagas do Sine | https://www.gov.br/trabalho-e-emprego/pt-br/noticias-e-conteudo/2025/janeiro/vagas-de-emprego-do-sine-podem-ser-visualizadas-na-carteira-de-trabalho-digital | 11/11/2026 |
| 9 | FGTS | https://www.fgts.gov.br/Paginas/trabalhador/app-fgts.aspx |10/11/2026 |
| 10 | Seguro-desemprego | https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego | 13/11/2026 |
| 11 | 13º salário (Lei 4.090/1962) | https://www.planalto.gov.br/ccivil_03/leis/l4090.htm | 15/11/2026 |


### Fontes de apoio (consultadas para decidir o que entra ou não na base):

- eSocial — desativação da consulta de qualificação cadastral on-line (10/02/2025): https://www.gov.br/esocial/pt-br/noticias/desativacao-da-consulta-da-qualificacao-cadastral-on-line
- eSocial — qualificação cadastral (responsabilidade do empregador): https://www.gov.br/esocial/pt-br/empresas/consulta-qualificacao-cadastral
- CIN — onde emitir e documentos: https://www.gov.br/governodigital/pt-br/identidade/cin/duvidas-frequentes-sobre-a-cin-campanha

## Resultado do teste com usuários

| Indicador | Resultado |
|---|---|
| Atendimentos | 20 (17 por pergunta e 3 pela navegação por categorias) |
| Resposta encontrada | 90,0% |
| Taxa de acerto (ajudou) | 85,0% |
| Facilidade de uso (1 a 5) | 4,1 |

- **Dúvidas sem solução (até enttão):**
 - "como funciona a clt?" (não encontrada)
  - "conta no gov é obrigatório?" (não encontrada)
  - "tenho direito a vale transporte?" (encontrada, mas a pessoa respondeu que não ajudou)

**Melhoria feita a partir do teste:**
1. Ampliamos as palavras-chave das 17 orientações com palavras mais gerais e sinônimos. Por exemplo, `clt` na Carteira de Trabalho, `gov` e `senha` na conta gov.br, `perdi o emprego` no seguro-desemprego, `mulher` e `exercito` no alistamento feminino. Logo após essa melhoria, as duas perguntas não encontradas passaram a ser respondidas: "como funciona a clt?" vai para a Carteira de Trabalho Digital e "conta no gov é obrigatório?" vai para a conta gov.br.
2. Quando a pessoa digita um texto no lugar de s/n, o assistente agora explica: "Para fazer outra pergunta, primeiro responda s ou n aqui."


## Limitações

- A busca é por palavras: perguntas com sinônimos que, mesmo com melhoias, não estão nas palavras-chave podem não ser encontradas.
- O assistente não entende erros de digitação (ex.: "esttagio").
- Regras que mudam por estado (como a Carteira de Identidade) são apresentadas de forma geral; a pessoa precisa conferir no site do seu estado.
- As informações valem para a data de verificação; leis e prazos podem mudar.
- Não consulta dados da pessoa, não agenda atendimentos e não confirma direitos: só orienta.

## Vídeo técnico

Link: ...
