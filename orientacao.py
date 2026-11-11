"""Classe Orientacao: representa UM registro da base de conhecimento (um item do JSON)."""


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        # Cada campo do JSON vira um atributo do objeto (self = o próprio objeto)
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave  # lista de strings
        self.resposta = resposta
        self.documentos = documentos          # lista de strings
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self):
        """Mostra a orientação completa, sempre com fonte, data e aviso."""
        print()
        print(f">> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        print()  # linha em branco para separar as partes
        if len(self.documentos) > 0:  # só mostra se a lista não estiver vazia
            print("Documentos necessários:")
            for documento in self.documentos:
                print(f"  - {documento}")
            print()
        print(f"Onde: {self.onde}")
        print()
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print()
        print("Aviso: este assistente NÃO é um canal oficial. Confirme no site do órgão.")
