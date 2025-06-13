from neo4j import GraphDatabase
from typing import List, Optional
from models.cliente import Cliente
import uuid
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, MONGO_URI
from config.database import Database

class ClienteDAO:
    def __init__(self):
        self.database = Database(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, MONGO_URI)
        self.driver = self.database.driver
        self.mongo_collection = self.database.mongo_db["clientes"]

    def close(self):
        self.database.close()

    def criar_cliente(self, cliente: Cliente) -> str:
        """Cria um novo cliente no Neo4j e MongoDB, retorna sua identificacao"""
        identificacao = str(uuid.uuid4())
        with self.driver.session() as session:
            session.execute_write(self._criar_cliente, identificacao)
            # Salvar dados completos no MongoDB
            cliente_data = cliente.to_dict()
            cliente_data["identificacao"] = identificacao
            self.mongo_collection.insert_one(cliente_data)
            return identificacao

    def _criar_cliente(self, tx, identificacao: str):
        """Cria um cliente no Neo4j com a identificacao fornecida"""
        query = "CREATE (c:Cliente {identificacao: $identificacao})"
        tx.run(query, identificacao=identificacao)

    def buscar_cliente(self, identificacao: str) -> Optional[Cliente]:
        """Busca um cliente pela identificacao no Neo4j e MongoDB"""
        with self.driver.session() as session:
            neo4j_result = session.execute_read(self._buscar_cliente, identificacao)
            if neo4j_result:
                # Buscar dados completos no MongoDB
                mongo_data = self.mongo_collection.find_one({"identificacao": identificacao})
                if mongo_data:
                    return Cliente.from_dict(mongo_data)
            return None

    def _buscar_cliente(self, tx, identificacao: str) -> Optional[Cliente]:
        """Busca um cliente pela identificacao no Neo4j"""
        query = "MATCH (c:Cliente) WHERE c.identificacao = $identificacao RETURN c.identificacao as identificacao"
        result = tx.run(query, identificacao=identificacao)
        record = result.single()
        if record:
            return Cliente(identificacao=record["identificacao"])
        return None

    def buscar_todos_clientes(self) -> List[Cliente]:
        """Retorna todos os clientes do Neo4j e MongoDB"""
        with self.driver.session() as session:
            neo4j_clientes = session.execute_read(self._buscar_todos_clientes)
            clientes = []
            for cli in neo4j_clientes:
                mongo_data = self.mongo_collection.find_one({"identificacao": cli.identificacao})
                if mongo_data:
                    clientes.append(Cliente.from_dict(mongo_data))
            return clientes

    def _buscar_todos_clientes(self, tx) -> List[Cliente]:
        """Retorna todos os clientes do Neo4j"""
        query = "MATCH (c:Cliente) RETURN c.identificacao as identificacao"
        result = tx.run(query)
        return [Cliente(identificacao=record["identificacao"]) for record in result]

    def remover_cliente(self, identificacao: str) -> bool:
        """Remove um cliente pela identificacao do Neo4j e MongoDB"""
        with self.driver.session() as session:
            success = session.execute_write(self._remover_cliente, identificacao)
            if success:
                self.mongo_collection.delete_one({"identificacao": identificacao})
            return success

    def _remover_cliente(self, tx, identificacao: str) -> bool:
        """Remove um cliente pela identificacao do Neo4j"""
        query = "MATCH (c:Cliente) WHERE c.identificacao = $identificacao DETACH DELETE c"
        result = tx.run(query, identificacao=identificacao)
        return result.consume().counters.nodes_deleted > 0

    def buscar_carros_do_cliente(self, identificacao: str) -> List[str]:
        """Busca as identificacoes dos carros que o cliente possui"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_carros_do_cliente, identificacao)

    def _buscar_carros_do_cliente(self, tx, identificacao: str) -> List[str]:
        """Busca as identificacoes dos carros que o cliente possui"""
        query = """
        MATCH (c:Cliente)-[:POSSUI]->(car:Carro)
        WHERE c.identificacao = $identificacao
        RETURN car.identificacao as identificacao
        """
        result = tx.run(query, identificacao=identificacao)
        return [record["identificacao"] for record in result]

    def vincular_carro_ao_cliente(self, cliente_identificacao: str, carro_identificacao: str) -> bool:
        """Vincula um carro a um cliente"""
        with self.driver.session() as session:
            return session.execute_write(self._vincular_carro_ao_cliente, cliente_identificacao, carro_identificacao)

    def _vincular_carro_ao_cliente(self, tx, cliente_identificacao: str, carro_identificacao: str) -> bool:
        """Vincula um carro a um cliente"""
        query = """
        MATCH (c:Cliente), (car:Carro)
        WHERE c.identificacao = $cliente_identificacao AND car.identificacao = $carro_identificacao
        CREATE (c)-[:POSSUI]->(car)
        """
        result = tx.run(query, cliente_identificacao=cliente_identificacao, carro_identificacao=carro_identificacao)
        return result.consume().counters.relationships_created > 0

    def desvincular_carro_do_cliente(self, cliente_identificacao: str, carro_identificacao: str) -> bool:
        """Remove a relação entre um cliente e um carro"""
        with self.driver.session() as session:
            return session.execute_write(self._desvincular_carro_do_cliente, cliente_identificacao, carro_identificacao)

    def _desvincular_carro_do_cliente(self, tx, cliente_identificacao: str, carro_identificacao: str) -> bool:
        """Remove a relação entre um cliente e um carro"""
        query = """
        MATCH (c:Cliente)-[r:POSSUI]->(car:Carro)
        WHERE c.identificacao = $cliente_identificacao AND car.identificacao = $carro_identificacao
        DELETE r
        """
        result = tx.run(query, cliente_identificacao=cliente_identificacao, carro_identificacao=carro_identificacao)
        return result.consume().counters.relationships_deleted > 0

    def atualizar_cliente(self, identificacao: str, cliente_update: Cliente) -> bool:
        """Atualiza os dados de um cliente no MongoDB"""
        cliente_data = cliente_update.to_dict()
        cliente_data["identificacao"] = identificacao
        result = self.mongo_collection.replace_one({"identificacao": identificacao}, cliente_data)
        return result.matched_count > 0