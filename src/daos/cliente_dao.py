from neo4j import GraphDatabase
from typing import List, Optional
from models.cliente import Cliente
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

class ClienteDAO:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def criar_cliente(self, cliente: Cliente) -> int:
        """Cria um novo cliente no Neo4j e retorna seu ID"""
        with self.driver.session() as session:
            return session.execute_write(self._criar_cliente)

    def _criar_cliente(self, tx) -> int:
        """Cria um cliente no Neo4j e retorna seu ID"""
        query = "CREATE (c:Cliente) RETURN id(c) as id"
        result = tx.run(query)
        return result.single()["id"]

    def buscar_cliente(self, cliente_id: int) -> Optional[Cliente]:
        """Busca um cliente pelo ID no Neo4j"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_cliente, cliente_id)

    def _buscar_cliente(self, tx, cliente_id: int) -> Optional[Cliente]:
        """Busca um cliente pelo ID no Neo4j"""
        query = "MATCH (c:Cliente) WHERE id(c) = $id RETURN id(c) as id"
        result = tx.run(query, id=cliente_id)
        record = result.single()
        if record:
            return Cliente(id=record["id"])
        return None

    def buscar_todos_clientes(self) -> List[Cliente]:
        """Retorna todos os clientes do Neo4j"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_todos_clientes)

    def _buscar_todos_clientes(self, tx) -> List[Cliente]:
        """Retorna todos os clientes do Neo4j"""
        query = "MATCH (c:Cliente) RETURN id(c) as id"
        result = tx.run(query)
        return [Cliente(id=record["id"]) for record in result]

    def remover_cliente(self, cliente_id: int) -> bool:
        """Remove um cliente pelo ID do Neo4j"""
        with self.driver.session() as session:
            return session.execute_write(self._remover_cliente, cliente_id)

    def _remover_cliente(self, tx, cliente_id: int) -> bool:
        """Remove um cliente pelo ID do Neo4j"""
        query = "MATCH (c:Cliente) WHERE id(c) = $id DETACH DELETE c"
        result = tx.run(query, id=cliente_id)
        return result.consume().counters.nodes_deleted > 0

    def buscar_carros_do_cliente(self, cliente_id: int) -> List[int]:
        """Busca os IDs dos carros que o cliente possui"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_carros_do_cliente, cliente_id)

    def _buscar_carros_do_cliente(self, tx, cliente_id: int) -> List[int]:
        """Busca os IDs dos carros que o cliente possui"""
        query = """
        MATCH (c:Cliente)-[:POSSUI]->(car:Carro)
        WHERE id(c) = $cliente_id
        RETURN id(car) as id
        """
        result = tx.run(query, cliente_id=cliente_id)
        return [record["id"] for record in result]

    def vincular_carro_ao_cliente(self, cliente_id: int, carro_id: int) -> bool:
        """Vincula um carro a um cliente"""
        with self.driver.session() as session:
            return session.execute_write(self._vincular_carro_ao_cliente, cliente_id, carro_id)

    def _vincular_carro_ao_cliente(self, tx, cliente_id: int, carro_id: int) -> bool:
        """Vincula um carro a um cliente"""
        query = """
        MATCH (c:Cliente), (car:Carro)
        WHERE id(c) = $cliente_id AND id(car) = $carro_id
        CREATE (c)-[:POSSUI]->(car)
        """
        result = tx.run(query, cliente_id=cliente_id, carro_id=carro_id)
        return result.consume().counters.relationships_created > 0

    def desvincular_carro_do_cliente(self, cliente_id: int, carro_id: int) -> bool:
        """Remove a relação entre um cliente e um carro"""
        with self.driver.session() as session:
            return session.execute_write(self._desvincular_carro_do_cliente, cliente_id, carro_id)

    def _desvincular_carro_do_cliente(self, tx, cliente_id: int, carro_id: int) -> bool:
        """Remove a relação entre um cliente e um carro"""
        query = """
        MATCH (c:Cliente)-[r:POSSUI]->(car:Carro)
        WHERE id(c) = $cliente_id AND id(car) = $carro_id
        DELETE r
        """
        result = tx.run(query, cliente_id=cliente_id, carro_id=carro_id)
        return result.consume().counters.relationships_deleted > 0

    def atualizar_cliente(self, cliente_id: int, cliente_update):
        # Este método precisa ser implementado conforme a lógica de atualização no MongoDB
        # Aqui só um placeholder para não quebrar o CLI
        return False 