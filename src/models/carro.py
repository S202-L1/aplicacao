class Carro:
    def __init__(self, id: int = None, modelo: str = None, ano: int = None, 
                 fabricante: str = None, crlv: str = None):
        self.id = id  # Neo4j ID
        self.modelo = modelo  # Will be stored in MongoDB
        self.ano = ano  # Will be stored in MongoDB
        self.fabricante = fabricante  # Will be stored in MongoDB
        self.crlv = crlv  # Will be stored in MongoDB

    def to_dict(self):
        return {
            "id": self.id,
            "modelo": self.modelo,
            "ano": self.ano,
            "fabricante": self.fabricante,
            "crlv": self.crlv
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            modelo=data.get("modelo"),
            ano=data.get("ano"),
            fabricante=data.get("fabricante"),
            crlv=data.get("crlv")
        ) 