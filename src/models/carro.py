class Carro:
    def __init__(self, identificacao: int = None, modelo: str = None, ano: int = None, 
                 fabricante: str = None, crlv: str = None):
        self.identificacao = identificacao  # Neo4j identificacao
        self.modelo = modelo  # Will be stored in MongoDB
        self.ano = ano  # Will be stored in MongoDB
        self.fabricante = fabricante  # Will be stored in MongoDB
        self.crlv = crlv  # Will be stored in MongoDB

    def to_dict(self):
        return {
            "identificacao": self.identificacao,
            "modelo": self.modelo,
            "ano": self.ano,
            "fabricante": self.fabricante,
            "crlv": self.crlv
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            identificacao=data.get("identificacao"),
            modelo=data.get("modelo"),
            ano=data.get("ano"),
            fabricante=data.get("fabricante"),
            crlv=data.get("crlv")
        ) 