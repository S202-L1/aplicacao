class Concessionaria:
    def __init__(self, id: int = None, nome: str = None):
        self.id = id
        self.nome = nome

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            nome=data.get("nome")
        ) 