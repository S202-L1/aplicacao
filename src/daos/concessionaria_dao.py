from neo4j import GraphDatabase
from typing import List, Optional
from models.concessionaria import Concessionaria
from models.carro import Carro
from data.carros_padrao import MODELOS_CARROS, PREFIXOS_CRLV
import random
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, MONGO_URI
from config.database import Database

class ConcessionariaDAO:
    def __init__(self):
        self.database = Database(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, MONGO_URI)
        self.driver = self.database.driver
        self.mongo_collection = self.database.mongo_db["concessionarias"]
        self.carro_collection = self.database.mongo_db["carros"]

    def close(self):
        self.database.close()

    def criar_concessionaria(self, concessionaria: Concessionaria) -> int:
        """Cria uma nova concessionária no Neo4j e MongoDB, cria e vincula 10 carros, e retorna o ID da concessionária"""
        with self.driver.session() as session:
            concessionaria_id = session.execute_write(self._criar_concessionaria)
            # Salvar dados da concessionária no MongoDB
            concessionaria_data = concessionaria.to_dict()
            concessionaria_data["_id"] = concessionaria_id
            self.mongo_collection.insert_one(concessionaria_data)
            # Criar e vincular 10 carros aleatórios
            carros = []
            for _ in range(10):
                carro_data = random.choice(MODELOS_CARROS)
                crlv = f"{PREFIXOS_CRLV[carro_data['fabricante']]}-{random.randint(1000, 9999)}"
                carro = Carro(
                    modelo=carro_data["modelo"],
                    ano=carro_data["ano"],
                    fabricante=carro_data["fabricante"],
                    crlv=crlv
                )
                carros.append(carro)
            carros_ids = session.execute_write(self._criar_e_vincular_carros, concessionaria_id, carros)
            # Salvar carros no MongoDB
            for carro, carro_id in zip(carros, carros_ids):
                carro_data = carro.to_dict()
                carro_data["_id"] = carro_id
                self.carro_collection.insert_one(carro_data)
            return concessionaria_id

    def _criar_concessionaria(self, tx) -> int:
        """Cria uma concessionária no Neo4j e retorna seu ID"""
        query = "CREATE (c:Concessionaria) RETURN id(c) as id"
        result = tx.run(query)
        return result.single()["id"]

    def _criar_e_vincular_carros(self, tx, concessionaria_id: int, carros: List[Carro]) -> List[int]:
        """Cria 10 carros e vincula à concessionária"""
        carros_ids = []
        for _ in carros:
            query = "CREATE (c:Carro) RETURN id(c) as id"
            result = tx.run(query)
            carro_id = result.single()["id"]
            carros_ids.append(carro_id)
            # Vincula o carro à concessionária
            query = """
            MATCH (c:Concessionaria), (car:Carro)
            WHERE id(c) = $concessionaria_id AND id(car) = $carro_id
            CREATE (c)-[:POSSUI]->(car)
            """
            tx.run(query, concessionaria_id=concessionaria_id, carro_id=carro_id)
        return carros_ids

    def buscar_concessionaria(self, concessionaria_id: int) -> Optional[Concessionaria]:
        """Busca uma concessionária pelo ID no Neo4j e MongoDB"""
        with self.driver.session() as session:
            neo4j_result = session.execute_read(self._buscar_concessionaria, concessionaria_id)
            if neo4j_result:
                # Buscar dados completos no MongoDB
                mongo_data = self.mongo_collection.find_one({"_id": concessionaria_id})
                if mongo_data:
                    return Concessionaria.from_dict(mongo_data)
            return None

    def _buscar_concessionaria(self, tx, concessionaria_id: int) -> Optional[Concessionaria]:
        """Busca uma concessionária pelo ID no Neo4j"""
        query = "MATCH (c:Concessionaria) WHERE id(c) = $id RETURN id(c) as id"
        result = tx.run(query, id=concessionaria_id)
        record = result.single()
        if record:
            return Concessionaria(id=record["id"])
        return None

    def buscar_todas_concessionarias(self) -> List[Concessionaria]:
        """Retorna todas as concessionárias do Neo4j e MongoDB"""
        with self.driver.session() as session:
            neo4j_concessionarias = session.execute_read(self._buscar_todas_concessionarias)
            concessionarias = []
            for conc in neo4j_concessionarias:
                mongo_data = self.mongo_collection.find_one({"_id": conc.id})
                if mongo_data:
                    concessionarias.append(Concessionaria.from_dict(mongo_data))
            return concessionarias

    def _buscar_todas_concessionarias(self, tx) -> List[Concessionaria]:
        """Retorna todas as concessionárias do Neo4j"""
        query = "MATCH (c:Concessionaria) RETURN id(c) as id"
        result = tx.run(query)
        return [Concessionaria(id=record["id"]) for record in result]

    def remover_concessionaria(self, concessionaria_id: int) -> bool:
        """Remove uma concessionária pelo ID do Neo4j e MongoDB"""
        with self.driver.session() as session:
            # Buscar carros da concessionária para remover do MongoDB
            carros_ids = self.buscar_carros_da_concessionaria(concessionaria_id)
            success = session.execute_write(self._remover_concessionaria, concessionaria_id)
            if success:
                self.mongo_collection.delete_one({"_id": concessionaria_id})
                # Remover carros associados do MongoDB
                for carro_id in carros_ids:
                    self.carro_collection.delete_one({"_id": carro_id})
            return success

    def _remover_concessionaria(self, tx, concessionaria_id: int) -> bool:
        """Remove uma concessionária pelo ID do Neo4j"""
        query = "MATCH (c:Concessionaria) WHERE id(c) = $id DETACH DELETE c"
        result = tx.run(query, id=concessionaria_id)
        return result.consume().counters.nodes_deleted > 0

    def buscar_carros_da_concessionaria(self, concessionaria_id: int) -> List[int]:
        """Busca os IDs dos carros que a concessionária possui"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_carros_da_concessionaria, concessionaria_id)

    def _buscar_carros_da_concessionaria(self, tx, concessionaria_id: int) -> List[int]:
        """Busca os IDs dos carros que a concessionária possui"""
        query = """
        MATCH (c:Concessionaria)-[:POSSUI]->(car:Carro)
        WHERE id(c) = $concessionaria_id
        RETURN id(car) as id
        """
        result = tx.run(query, concessionaria_id=concessionaria_id)
        return [record["id"] for record in result]

    def vincular_carro_a_concessionaria(self, concessionaria_id: int, carro_id: int) -> bool:
        """Vincula um carro a uma concessionária"""
        with self.driver.session() as session:
            return session.execute_write(self._vincular_carro_a_concessionaria, concessionaria_id, carro_id)

    def _vincular_carro_a_concessionaria(self, tx, concessionaria_id: int, carro_id: int) -> bool:
        """Vincula um carro a uma concessionária"""
        query = """
        MATCH (c:Concessionaria), (car:Carro)
        WHERE id(c) = $concessionaria_id AND id(car) = $carro_id
        CREATE (c)-[:POSSUI]->(car)
        """
        result = tx.run(query, concessionaria_id=concessionaria_id, carro_id=carro_id)
        return result.consume().counters.relationships_created > 0

    def desvincular_carro_da_concessionaria(self, concessionaria_id: int, carro_id: int) -> bool:
        """Remove a relação entre uma concessionária e um carro"""
        with self.driver.session() as session:
            return session.execute_write(self._desvincular_carro_da_concessionaria, concessionaria_id, carro_id)

    def _desvincular_carro_da_concessionaria(self, tx, concessionaria_id: int, carro_id: int) -> bool:
        """Remove a relação entre uma concessionária e um carro"""
        query = """
        MATCH (c:Concessionaria)-[r:POSSUI]->(car:Carro)
        WHERE id(c) = $concessionaria_id AND id(car) = $carro_id
        DELETE r
        """
        result = tx.run(query, concessionaria_id=concessionaria_id, carro_id=carro_id)
        return result.consume().counters.relationships_deleted > 0

    def atualizar_concessionaria(self, concessionaria_id: int, concessionaria_update: Concessionaria) -> bool:
        """Atualiza os dados de uma concessionária no MongoDB"""
        concessionaria_data = concessionaria_update.to_dict()
        concessionaria_data["_id"] = concessionaria_id
        result = self.mongo_collection.replace_one({"_id": concessionaria_id}, concessionaria_data)
        return result.matched_count > 0