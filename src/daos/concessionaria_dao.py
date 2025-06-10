from neo4j import GraphDatabase
from typing import List, Optional
from models.concessionaria import Concessionaria
from models.carro import Carro
from data.carros_padrao import MODELOS_CARROS, PREFIXOS_CRLV
import random
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

class ConcessionariaDAO:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def criar_concessionaria(self, concessionaria: Concessionaria) -> int:
        """Cria uma nova concessionária no Neo4j, cria e vincula 10 carros, e retorna o ID da concessionária"""
        with self.driver.session() as session:
            concessionaria_id = session.execute_write(self._criar_concessionaria)
            # Cria e vincula 10 carros aleatórios (passando parâmetros, mas só IDs usados no Neo4j)
            carros = []
            for _ in range(10):
                # Parâmetros fictícios para o futuro uso no MongoDB
                carro_param = Carro(modelo="", ano=0, fabricante="", crlv="")
                carros.append(carro_param)
            session.execute_write(self._criar_e_vincular_carros, concessionaria_id, carros)
            return concessionaria_id

    def _criar_concessionaria(self, tx) -> int:
        """Cria uma concessionária no Neo4j e retorna seu ID"""
        query = "CREATE (c:Concessionaria) RETURN id(c) as id"
        result = tx.run(query)
        return result.single()["id"]

    # Isso é necessário pra evitar que o usuário tenha que criar os carros manualmente ao criar uma concessionária
    def _criar_e_vincular_carros(self, tx, concessionaria_id: int, carros):
        """Cria 10 carros (ou a quantidade passada) e vincula à concessionária"""
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
        """Busca uma concessionária pelo ID no Neo4j"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_concessionaria, concessionaria_id)

    def _buscar_concessionaria(self, tx, concessionaria_id: int) -> Optional[Concessionaria]:
        """Busca uma concessionária pelo ID no Neo4j"""
        query = "MATCH (c:Concessionaria) WHERE id(c) = $id RETURN id(c) as id"
        result = tx.run(query, id=concessionaria_id)
        record = result.single()
        if record:
            return Concessionaria(id=record["id"])
        return None

    def buscar_todas_concessionarias(self) -> List[Concessionaria]:
        """Retorna todas as concessionárias do Neo4j"""
        with self.driver.session() as session:
            return session.execute_read(self._buscar_todas_concessionarias)

    def _buscar_todas_concessionarias(self, tx) -> List[Concessionaria]:
        """Retorna todas as concessionárias do Neo4j"""
        query = "MATCH (c:Concessionaria) RETURN id(c) as id"
        result = tx.run(query)
        return [Concessionaria(id=record["id"]) for record in result]

    def remover_concessionaria(self, concessionaria_id: int) -> bool:
        """Remove uma concessionária pelo ID do Neo4j"""
        with self.driver.session() as session:
            return session.execute_write(self._remover_concessionaria, concessionaria_id)

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

    def atualizar_concessionaria(self, concessionaria: Concessionaria) -> Optional[Concessionaria]:
        with self.driver.session() as session:
            return session.execute_write(self._atualizar_concessionaria, concessionaria)

    def _atualizar_concessionaria(self, tx, concessionaria: Concessionaria) -> Optional[Concessionaria]:
        result = tx.run(
            """
            MATCH (c:Concessionaria)
            WHERE id(c) = $id
            SET c.nome = $nome
            RETURN id(c) as id, c.nome as nome
            """,
            id=concessionaria.id,
            nome=concessionaria.nome
        )
        record = result.single()
        if record:
            return Concessionaria(id=record["id"], nome=record["nome"])
        return None

    def atualizar_concessionaria(self, concessionaria_id: int, concessionaria_update: Concessionaria):
        with self.driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (c:Concessionaria)
                    WHERE id(c) = $concessionaria_id
                    SET c.nome = $nome
                    RETURN c
                    """,
                    concessionaria_id=concessionaria_id,
                    **concessionaria_update.to_dict()
                ).single()
            )
            
            if result:
                print(f"Concessionária {concessionaria_id} atualizada com sucesso.")
                return True
            else:
                print(f"Concessionária com id {concessionaria_id} não encontrada para atualização.")
                return False

    def remover_concessionaria(self, concessionaria_id: int):
        with self.driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (c:Concessionaria)
                    WHERE id(c) = $concessionaria_id
                    DELETE c
                    RETURN count(c) as deleted
                    """,
                    concessionaria_id=concessionaria_id
                ).single()
            )
            
            if result["deleted"] > 0:
                print(f"Concessionária {concessionaria_id} excluída com sucesso.")
                return True
            else:
                print(f"Concessionária com id {concessionaria_id} não encontrada para exclusão.")
                return False

    def atualizar_concessionaria(self, concessionaria_id: int, concessionaria_update):
        # Este método precisa ser implementado conforme a lógica de atualização no MongoDB
        # Aqui só um placeholder para não quebrar o CLI
        return False 