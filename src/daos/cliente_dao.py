from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from datetime import datetime

class Cliente:
    def __init__(self, cpf: str, nome: str, nacionalidade: str, data_nascimento: datetime):
        self.cpf = cpf
        self.nome = nome
        self.nacionalidade = nacionalidade
        self.data_nascimento = data_nascimento

    def to_dict(self):
        return {
            "cpf": self.cpf,
            "nome": self.nome,
            "nacionalidade": self.nacionalidade,
            "data_nascimento": self.data_nascimento.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            cpf=data["cpf"],
            nome=data["nome"],
            nacionalidade=data["nacionalidade"],
            data_nascimento=datetime.fromisoformat(data["data_nascimento"])
        )

class ClienteDAO:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def criar_cliente(self, cliente: Cliente):
        with self.driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(
                    """
                    CREATE (c:Cliente {
                        cpf: $cpf,
                        nome: $nome,
                        nacionalidade: $nacionalidade,
                        data_nascimento: $data_nascimento
                    })
                    RETURN id(c) as cliente_id
                    """,
                    cliente.to_dict()
                ).single()
            )
            cliente_id = result["cliente_id"]
            print(f"Cliente '{cliente.nome}' criado com id: {cliente_id}")
            return cliente_id

    def ler_cliente_por_id(self, cliente_id: int):
        with self.driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run(
                    """
                    MATCH (c:Cliente)
                    WHERE id(c) = $cliente_id
                    RETURN c
                    """,
                    cliente_id=cliente_id
                ).single()
            )
            
            if result:
                cliente_data = result["c"]
                print(f"Cliente encontrado.")
                return Cliente.from_dict(dict(cliente_data))
            else:
                print(f"Cliente com id {cliente_id} não encontrado.")
                return None

    def buscar_cliente_por_cpf(self, cpf: str):
        with self.driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run(
                    """
                    MATCH (c:Cliente)
                    WHERE c.cpf = $cpf
                    RETURN c
                    """,
                    cpf=cpf
                ).single()
            )
            
            if result:
                cliente_data = result["c"]
                print(f"Cliente encontrado.")
                return Cliente.from_dict(dict(cliente_data))
            else:
                print(f"Cliente com CPF {cpf} não encontrado.")
                return None

    def buscar_todos_os_clientes(self):
        with self.driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run(
                    """
                    MATCH (c:Cliente)
                    RETURN c
                    """
                ).data()
            )
            
            clientes = [Cliente.from_dict(dict(record["c"])) for record in result]
            print(f"Encontrado(s) {len(clientes)} cliente(s).")
            return clientes

    def atualizar_cliente(self, cliente_id: int, cliente_update: Cliente):
        with self.driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (c:Cliente)
                    WHERE id(c) = $cliente_id
                    SET c.cpf = $cpf,
                        c.nome = $nome,
                        c.nacionalidade = $nacionalidade,
                        c.data_nascimento = $data_nascimento
                    RETURN c
                    """,
                    cliente_id=cliente_id,
                    **cliente_update.to_dict()
                ).single()
            )
            
            if result:
                print(f"Cliente {cliente_id} atualizado com sucesso.")
                return True
            else:
                print(f"Cliente com id {cliente_id} não encontrado para atualização.")
                return False

    def apagar_cliente(self, cliente_id: int):
        with self.driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (c:Cliente)
                    WHERE id(c) = $cliente_id
                    DELETE c
                    RETURN count(c) as deleted
                    """,
                    cliente_id=cliente_id
                ).single()
            )
            
            if result["deleted"] > 0:
                print(f"Cliente {cliente_id} excluído com sucesso.")
                return True
            else:
                print(f"Cliente com id {cliente_id} não encontrado para exclusão.")
                return False 