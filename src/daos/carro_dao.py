from neo4j import GraphDatabase
from typing import List, Optional
from models.carro import Carro
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, MONGO_URI
from config.database import Database

class CarroDAO:
    def __init__(self):
        self.database = Database(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, MONGO_URI)
        self.driver = self.database.driver
        self.mongo_collection = self.database.mongo_db["carros"]

    def close(self):
        self.database.close()

    def criar_carro(self, carro: Carro) -> int:
        """Cria um novo carro no Neo4j e no MongoDB, retorna seu ID"""
        with self.driver.session() as session:
            carro_id = session.execute_write(self._criar_carro)
            # Salvar dados completos no MongoDB
            carro_data = carro.to_dict()
            carro_data["_id"] = carro_id  # Usar o ID do Neo4j como _id no MongoDB
            self.mongo_collection.insert_one(carro_data)
            return carro_id

    def _criar_carro(self, tx) -> int:
        """Cria um carro no Neo4j e retorna seu ID"""
        query = "CREATE (c:Carro) RETURN id(c) as id"
        result = tx.run(query)
        return result.single()["id"]

    def buscar_carro(self, carro_id: int) -> Optional[Carro]:
        """Busca um carro pelo ID no Neo4j e MongoDB"""
        with self.driver.session() as session:
            neo4j_result = session.execute_read(self._buscar_carro, carro_id)
            if neo4j_result:
                # Buscar dados completos no MongoDB
                mongo_data = self.mongo_collection.find_one({"_id": carro_id})
                if mongo_data:
                    return Carro.from_dict(mongo_data)
            return None

    def _buscar_carro(self, tx, carro_id: int) -> Optional[Carro]:
        """Busca um carro pelo ID no Neo4j"""
        query = "MATCH (c:Carro) WHERE id(c) = $id RETURN id(c) as id"
        result = tx.run(query, id=carro_id)
        record = result.single()
        if record:
            return Carro(id=record["id"])
        return None

    def buscar_todos_carros(self) -> List[Carro]:
        """Retorna todos os carros do Neo4j e MongoDB"""
        with self.driver.session() as session:
            neo4j_carros = session.execute_read(self._buscar_todos_carros)
            carros = []
            for carro in neo4j_carros:
                mongo_data = self.mongo_collection.find_one({"_id": carro.id})
                if mongo_data:
                    carros.append(Carro.from_dict(mongo_data))
            return carros

    def _buscar_todos_carros(self, tx) -> List[Carro]:
        """Retorna todos os carros do Neo4j"""
        query = "MATCH (c:Carro) RETURN id(c) as id"
        result = tx.run(query)
        return [Carro(id=record["id"]) for record in result]

    def remover_carro(self, carro_id: int) -> bool:
        """Remove um carro pelo ID do Neo4j e MongoDB"""
        with self.driver.session() as session:
            success = session.execute_write(self._remover_carro, carro_id)
            if success:
                self.mongo_collection.delete_one({"_id": carro_id})
            return success

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

    def atualizar_carro(self, carro_id: int, carro_update: Carro) -> bool:
        """Atualiza os dados de um carro no MongoDB"""
        carro_data = carro_update.to_dict()
        carro_data["_id"] = carro_id
        result = self.mongo_collection.replace_one({"_id": carro_id}, carro_data)
        return result.matched_count > 0