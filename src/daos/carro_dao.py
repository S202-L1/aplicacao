from neo4j import GraphDatabase
from typing import List, Optional
from models.carro import Carro
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

class CarroDAO:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def criar_carro(self, carro: Carro) -> int:
        """Cria um novo carro no Neo4j e retorna seu ID"""
        with self.driver.session() as session:
            return session.execute_write(self._criar_carro)

    def _criar_carro(self, tx) -> int:
        """Cria um carro no Neo4j e retorna seu ID"""
        query = "CREATE (c:Carro) RETURN id(c) as id"
        result = tx.run(query)
        return result.single()["id"]

    def buscar_carro(self, carro_id: int) -> Optional[Carro]:
        """Busca um carro pelo ID no Neo4j"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_carro, carro_id)

    def _buscar_carro(self, tx, carro_id: int) -> Optional[Carro]:
        """Busca um carro pelo ID no Neo4j"""
        query = "MATCH (c:Carro) WHERE id(c) = $id RETURN id(c) as id"
        result = tx.run(query, id=carro_id)
        record = result.single()
        if record:
            return Carro(id=record["id"])
        return None

    def buscar_todos_carros(self) -> List[Carro]:
        """Retorna todos os carros do Neo4j"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_todos_carros)

    def _buscar_todos_carros(self, tx) -> List[Carro]:
        """Retorna todos os carros do Neo4j"""
        query = "MATCH (c:Carro) RETURN id(c) as id"
        result = tx.run(query)
        return [Carro(id=record["id"]) for record in result]

    def remover_carro(self, carro_id: int) -> bool:
        """Remove um carro pelo ID do Neo4j"""
        with self.driver.session() as session:
            return session.execute_write(self._remover_carro, carro_id)

    def _remover_carro(self, tx, carro_id: int) -> bool:
        """Remove um carro pelo ID do Neo4j"""
        query = "MATCH (c:Carro) WHERE id(c) = $id DETACH DELETE c"
        result = tx.run(query, id=carro_id)
        return result.consume().counters.nodes_deleted > 0

    def buscar_concessionaria_do_carro(self, carro_id: int) -> Optional[int]:
        """Busca a concessionária que possui o carro"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_concessionaria_do_carro, carro_id)

    def _buscar_concessionaria_do_carro(self, tx, carro_id: int) -> Optional[int]:
        """Busca a concessionária que possui o carro"""
        query = """
        MATCH (c:Carro)<-[:POSSUI]-(conc:Concessionaria)
        WHERE id(c) = $carro_id
        RETURN id(conc) as id
        """
        result = tx.run(query, carro_id=carro_id)
        record = result.single()
        return record["id"] if record else None

    def atualizar_carro(self, carro_id: int, carro_update):
        # Este método precisa ser implementado conforme a lógica de atualização no MongoDB
        # Aqui só um placeholder para não quebrar o CLI
        return False 