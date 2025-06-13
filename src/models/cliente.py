from datetime import datetime

class Cliente:
    def __init__(self, identificacao: int = None, cpf: str = None, nome: str = None, 
                 nacionalidade: str = None, data_nascimento: datetime = None):
        self.identificacao = identificacao  # Neo4j identificacao
        self.cpf = cpf  # Will be stored in MongoDB
        self.nome = nome  # Will be stored in MongoDB
        self.nacionalidade = nacionalidade  # Will be stored in MongoDB
        self.data_nascimento = data_nascimento  # Will be stored in MongoDB

    def to_dict(self):
        return {
            "identificacao": self.identificacao,
            "cpf": self.cpf,
            "nome": self.nome,
            "nacionalidade": self.nacionalidade,
            "data_nascimento": self.data_nascimento.isoformat() if self.data_nascimento else None
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            identificacao=data.get("identificacao"),
            cpf=data.get("cpf"),
            nome=data.get("nome"),
            nacionalidade=data.get("nacionalidade"),
            data_nascimento=datetime.fromisoformat(data["data_nascimento"]) if data.get("data_nascimento") else None
        ) 