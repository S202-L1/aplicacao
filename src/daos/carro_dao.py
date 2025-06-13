from neo4j import GraphDatabase
from typing import List, Optional
from models.carro import Carro
import uuid
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, MONGO_URI
from config.database import Database

class CarroDAO:
    def __init__(self):
        self.database = Database(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, MONGO_URI)
        self.driver = self.database.driver
        self.mongo_collection = self.database.mongo_db["carros"]

    def close(self):
        self.database.close()

    def criar_carro(self, carro: Carro) -> str:
        """Cria um novo carro no Neo4j e MongoDB, retorna sua identificacao"""
        identificacao = str(uuid.uuid4())
        with self.driver.session() as session:
            session.execute_write(self._criar_carro, identificacao)
            # Salvar dados completos no MongoDB
            carro_data = carro.to_dict()
            carro_data["identificacao"] = identificacao
            self.mongo_collection.insert_one(carro_data)
            return identificacao

    def _criar_carro(self, tx, identificacao: str):
        """Cria um carro no Neo4j com a identificacao fornecida"""
        query = "CREATE (c:Carro {identificacao: $identificacao})"
        tx.run(query, identificacao=identificacao)

    def buscar_carro(self, identificacao: str) -> Optional[Carro]:
        """Busca um carro pela identificacao no Neo4j e MongoDB"""
        with self.driver.session() as session:
            neo4j_result = session.execute_read(self._buscar_carro, identificacao)
            if neo4j_result:
                # Buscar dados completos no MongoDB
                mongo_data = self.mongo_collection.find_one({"identificacao": identificacao})
                if mongo_data:
                    return Carro.from_dict(mongo_data)
            return None

    def _buscar_carro(self, tx, identificacao: str) -> Optional[Carro]:
        """Busca um carro pela identificacao no Neo4j"""
        query = "MATCH (c:Carro) WHERE c.identificacao = $identificacao RETURN c.identificacao as identificacao"
        result = tx.run(query, identificacao=identificacao)
        record = result.single()
        if record:
            return Carro(identificacao=record["identificacao"])
        return None

    def buscar_todos_carros(self) -> List[Carro]:
        """Retorna todos os carros do Neo4j e MongoDB"""
        with self.driver.session() as session:
            neo4j_carros = session.execute_read(self._buscar_todos_carros)
            carros = []
            for car in neo4j_carros:
                mongo_data = self.mongo_collection.find_one({"identificacao": car.identificacao})
                if mongo_data:
                    carros.append(Carro.from_dict(mongo_data))
            return carros

    def _buscar_todos_carros(self, tx) -> List[Carro]:
        """Retorna todos os carros do Neo4j"""
        query = "MATCH (c:Carro) RETURN c.identificacao as identificacao"
        result = tx.run(query)
        return [Carro(identificacao=record["identificacao"]) for record in result]

    def remover_carro(self, identificacao: str) -> bool:
        """Remove um carro pela identificacao do Neo4j e MongoDB"""
        with self.driver.session() as session:
            success = session.execute_write(self._remover_carro, identificacao)
            if success:
                self.mongo_collection.delete_one({"identificacao": identificacao})
            return success

    def _remover_carro(self, tx, identificacao: str) -> bool:
        """Remove um carro pela identificacao do Neo4j"""
        query = "MATCH (c:Carro) WHERE c.identificacao = $identificacao DETACH DELETE c"
        result = tx.run(query, identificacao=identificacao)
        return result.consume().counters.nodes_deleted > 0

    def buscar_concessionaria_do_carro(self, identificacao: str) -> Optional[str]:
        """Busca a concessionária que possui o carro"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_concessionaria_do_carro, identificacao)

    def _buscar_concessionaria_do_carro(self, tx, identificacao: str) -> Optional[str]:
        """Busca a concessionária que possui o carro"""
        query = """
        MATCH (c:Carro)<-[:OFERECE]-(conc:Concessionaria)
        WHERE c.identificacao = $identificacao
        RETURN conc.identificacao as identificacao
        """
        result = tx.run(query, identificacao=identificacao)
        record = result.single()
        return record["identificacao"] if record else None

    def atualizar_carro(self, identificacao: str, carro_update: Carro) -> bool:
        """Atualiza os dados de um carro no MongoDB"""
        carro_data = carro_update.to_dict()
        carro_data["identificacao"] = identificacao
        result = self.mongo_collection.replace_one({"identificacao": identificacao}, carro_data)
        return result.matched_count > 0