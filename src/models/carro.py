class Carro:
    def __init__(self, id: int = None, modelo: str = None, ano: int = None, 
                 fabricante: str = None, crlv: str = None):
        self.id = id
        self.modelo = modelo
        self.ano = ano
        self.fabricante = fabricante
        self.crlv = crlv

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