class Concessionaria:
    def __init__(self, identificacao: int = None, nome: str = None):
        self.identificacao = identificacao  # Neo4j identificacao
        self.nome = nome  # Will be stored in MongoDB

    def to_dict(self):
        return {
            "identificacao": self.identificacao,
            "nome": self.nome
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            identificacao=data.get("identificacao"),
            nome=data.get("nome")
        ) 