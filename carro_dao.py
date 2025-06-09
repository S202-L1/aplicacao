from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

class Carro:
    def __init__(self, modelo: str, ano: int, fabricante: str, crlv: str):
        self.modelo = modelo
        self.ano = ano
        self.fabricante = fabricante
        self.crlv = crlv

    def to_dict(self):
        return {
            "modelo": self.modelo,
            "ano": self.ano,
            "fabricante": self.fabricante,
            "crlv": self.crlv
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            modelo=data["modelo"],
            ano=data["ano"],
            fabricante=data["fabricante"],
            crlv=data["crlv"]
        )

class CarroDAO:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def criar_carro(self, carro: Carro):
        with self.driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(
                    """
                    CREATE (c:Carro {
                        modelo: $modelo,
                        ano: $ano,
                        fabricante: $fabricante,
                        crlv: $crlv
                    })
                    RETURN id(c) as carro_id
                    """,
                    carro.to_dict()
                ).single()
            )
            carro_id = result["carro_id"]
            print(f"Carro '{carro.modelo}' criado com id: {carro_id}")
            return carro_id

    def ler_carro_por_id(self, carro_id: int):
        with self.driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run(
                    """
                    MATCH (c:Carro)
                    WHERE id(c) = $carro_id
                    RETURN c
                    """,
                    carro_id=carro_id
                ).single()
            )
            
            if result:
                carro_data = result["c"]
                print(f"Carro encontrado.")
                return Carro.from_dict(dict(carro_data))
            else:
                print(f"Carro com id {carro_id} não encontrado.")
                return None

    def buscar_todos_os_carros(self):
        with self.driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run(
                    """
                    MATCH (c:Carro)
                    RETURN c
                    """
                ).data()
            )
            
            carros = [Carro.from_dict(dict(record["c"])) for record in result]
            print(f"Encontrado(s) {len(carros)} carro(s).")
            return carros

    def atualizar_carro(self, carro_id: int, carro_update: Carro):
        with self.driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (c:Carro)
                    WHERE id(c) = $carro_id
                    SET c.modelo = $modelo,
                        c.ano = $ano,
                        c.fabricante = $fabricante,
                        c.crlv = $crlv
                    RETURN c
                    """,
                    carro_id=carro_id,
                    **carro_update.to_dict()
                ).single()
            )
            
            if result:
                print(f"Carro {carro_id} atualizado com sucesso.")
                return True
            else:
                print(f"Carro com id {carro_id} não encontrado para atualização.")
                return False

    def apagar_carro(self, carro_id: int):
        with self.driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (c:Carro)
                    WHERE id(c) = $carro_id
                    DELETE c
                    RETURN count(c) as deleted
                    """,
                    carro_id=carro_id
                ).single()
            )
            
            if result["deleted"] > 0:
                print(f"Carro {carro_id} excluído com sucesso.")
                return True
            else:
                print(f"Carro com id {carro_id} não encontrado para exclusão.")
                return False 