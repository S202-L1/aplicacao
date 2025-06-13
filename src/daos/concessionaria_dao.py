from neo4j import GraphDatabase
from typing import List, Optional
from models.concessionaria import Concessionaria
from models.carro import Carro
from data.carros_padrao import MODELOS_CARROS, PREFIXOS_CRLV
import random
import uuid
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

    def criar_concessionaria(self, concessionaria: Concessionaria) -> str:
        """Cria uma nova concessionária no Neo4j e MongoDB, cria e vincula 10 carros, e retorna a identificacao da concessionária"""
        identificacao = str(uuid.uuid4())
        with self.driver.session() as session:
            session.execute_write(self._criar_concessionaria, identificacao)
            # Salvar dados da concessionária no MongoDB
            concessionaria_data = concessionaria.to_dict()
            concessionaria_data["identificacao"] = identificacao
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
            carros_identificacoes = session.execute_write(self._criar_e_vincular_carros, identificacao, carros)
            # Salvar carros no MongoDB
            for carro, carro_identificacao in zip(carros, carros_identificacoes):
                carro_data = carro.to_dict()
                carro_data["identificacao"] = carro_identificacao
                self.carro_collection.insert_one(carro_data)
            return identificacao

    def _criar_concessionaria(self, tx, identificacao: str):
        """Cria uma concessionária no Neo4j com a identificacao fornecida"""
        query = "CREATE (c:Concessionaria {identificacao: $identificacao})"
        tx.run(query, identificacao=identificacao)

    def _criar_e_vincular_carros(self, tx, concessionaria_identificacao: str, carros: List[Carro]) -> List[str]:
        """Cria 10 carros e vincula à concessionária"""
        carros_identificacoes = []
        for _ in carros:
            carro_identificacao = str(uuid.uuid4())
            query = "CREATE (c:Carro {identificacao: $identificacao})"
            tx.run(query, identificacao=carro_identificacao)
            carros_identificacoes.append(carro_identificacao)
            # Vincula o carro à concessionária
            query = """
            MATCH (c:Concessionaria), (car:Carro)
            WHERE c.identificacao = $concessionaria_identificacao AND car.identificacao = $carro_identificacao
            CREATE (c)-[:POSSUI]->(car)
            """
            tx.run(query, concessionaria_identificacao=concessionaria_identificacao, carro_identificacao=carro_identificacao)
        return carros_identificacoes

    def buscar_concessionaria(self, identificacao: str) -> Optional[Concessionaria]:
        """Busca uma concessionária pela identificacao no Neo4j e MongoDB"""
        with self.driver.session() as session:
            neo4j_result = session.execute_read(self._buscar_concessionaria, identificacao)
            if neo4j_result:
                # Buscar dados completos no MongoDB
                mongo_data = self.mongo_collection.find_one({"identificacao": identificacao})
                if mongo_data:
                    return Concessionaria.from_dict(mongo_data)
            return None

    def _buscar_concessionaria(self, tx, identificacao: str) -> Optional[Concessionaria]:
        """Busca uma concessionária pela identificacao no Neo4j"""
        query = "MATCH (c:Concessionaria) WHERE c.identificacao = $identificacao RETURN c.identificacao as identificacao"
        result = tx.run(query, identificacao=identificacao)
        record = result.single()
        if record:
            return Concessionaria(identificacao=record["identificacao"])
        return None

    def buscar_todas_concessionarias(self) -> List[Concessionaria]:
        """Retorna todas as concessionárias do Neo4j e MongoDB"""
        with self.driver.session() as session:
            neo4j_concessionarias = session.execute_read(self._buscar_todas_concessionarias)
            concessionarias = []
            for conc in neo4j_concessionarias:
                mongo_data = self.mongo_collection.find_one({"identificacao": conc.identificacao})
                if mongo_data:
                    concessionarias.append(Concessionaria.from_dict(mongo_data))
            return concessionarias

    def _buscar_todas_concessionarias(self, tx) -> List[Concessionaria]:
        """Retorna todas as concessionárias do Neo4j"""
        query = "MATCH (c:Concessionaria) RETURN c.identificacao as identificacao"
        result = tx.run(query)
        return [Concessionaria(identificacao=record["identificacao"]) for record in result]

    def remover_concessionaria(self, identificacao: str) -> bool:
        """Remove uma concessionária pela identificacao do Neo4j e MongoDB"""
        with self.driver.session() as session:
            # Buscar carros da concessionária para remover do MongoDB
            carros_identificacoes = self.buscar_carros_da_concessionaria(identificacao)
            success = session.execute_write(self._remover_concessionaria, identificacao)
            if success:
                self.mongo_collection.delete_one({"identificacao": identificacao})
                # Remover carros associados do MongoDB
                for carro_identificacao in carros_identificacoes:
                    self.carro_collection.delete_one({"identificacao": carro_identificacao})
            return success

    def _remover_concessionaria(self, tx, identificacao: str) -> bool:
        """Remove uma concessionária pela identificacao do Neo4j"""
        query = "MATCH (c:Concessionaria) WHERE c.identificacao = $identificacao DETACH DELETE c"
        result = tx.run(query, identificacao=identificacao)
        return result.consume().counters.nodes_deleted > 0

    def buscar_carros_da_concessionaria(self, identificacao: str) -> List[str]:
        """Busca as identificacoes dos carros que a concessionária possui"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_carros_da_concessionaria, identificacao)

    def _buscar_carros_da_concessionaria(self, tx, identificacao: str) -> List[str]:
        """Busca as identificacoes dos carros que a concessionária possui"""
        query = """
        MATCH (c:Concessionaria)-[:POSSUI]->(car:Carro)
        WHERE c.identificacao = $identificacao
        RETURN car.identificacao as identificacao
        """
        result = tx.run(query, identificacao=identificacao)
        return [record["identificacao"] for record in result]

    def vincular_carro_a_concessionaria(self, concessionaria_identificacao: str, carro_identificacao: str) -> bool:
        """Vincula um carro a uma concessionária"""
        with self.driver.session() as session:
            return session.execute_write(self._vincular_carro_a_concessionaria, concessionaria_identificacao, carro_identificacao)

    def _vincular_carro_a_concessionaria(self, tx, concessionaria_identificacao: str, carro_identificacao: str) -> bool:
        """Vincula um carro a uma concessionária"""
        query = """
        MATCH (c:Concessionaria), (car:Carro)
        WHERE c.identificacao = $concessionaria_identificacao AND car.identificacao = $carro_identificacao
        CREATE (c)-[:POSSUI]->(car)
        """
        result = tx.run(query, concessionaria_identificacao=concessionaria_identificacao, carro_identificacao=carro_identificacao)
        return result.consume().counters.relationships_created > 0

    def desvincular_carro_da_concessionaria(self, concessionaria_identificacao: str, carro_identificacao: str) -> bool:
        """Remove a relação entre uma concessionária e um carro"""
        with self.driver.session() as session:
            return session.execute_write(self._desvincular_carro_da_concessionaria, concessionaria_identificacao, carro_identificacao)

    def _desvincular_carro_da_concessionaria(self, tx, concessionaria_identificacao: str, carro_identificacao: str) -> bool:
        """Remove a relação entre uma concessionária e um carro"""
        query = """
        MATCH (c:Concessionaria)-[r:POSSUI]->(car:Carro)
        WHERE c.identificacao = $concessionaria_identificacao AND car.identificacao = $carro_identificacao
        DELETE r
        """
        result = tx.run(query, concessionaria_identificacao=concessionaria_identificacao, carro_identificacao=carro_identificacao)
        return result.consume().counters.relationships_deleted > 0

    def atualizar_concessionaria(self, identificacao: str, concessionaria_update: Concessionaria) -> bool:
        """Atualiza os dados de uma concessionária no MongoDB"""
        concessionaria_data = concessionaria_update.to_dict()
        concessionaria_data["identificacao"] = identificacao
        result = self.mongo_collection.replace_one({"identificacao": identificacao}, concessionaria_data)
        return result.matched_count > 0