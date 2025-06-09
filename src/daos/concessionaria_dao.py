from neo4j import GraphDatabase
from typing import List, Optional
import random
from models.concessionaria import Concessionaria
from models.carro import Carro
from data.carros_padrao import MODELOS_CARROS, PREFIXOS_CRLV
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

class ConcessionariaDAO:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def criar_concessionaria(self, concessionaria: Concessionaria) -> Concessionaria:
        with self.driver.session() as session:
            # Criar a concessionária
            result = session.execute_write(self._criar_concessionaria, concessionaria)
            
            # Criar e vincular 10 carros aleatórios
            self._criar_e_vincular_carros(session, result.id)
            
            return result

    def _criar_e_vincular_carros(self, session, concessionaria_id: int):
        # Selecionar 10 carros aleatórios (pode haver repetição de modelo)
        carros_selecionados = random.choices(MODELOS_CARROS, k=10)
        
        for carro_data in carros_selecionados:
            # Gerar CRLV único baseado no fabricante
            prefixo = PREFIXOS_CRLV[carro_data["fabricante"]]
            numero = random.randint(100000, 999999)
            crlv = f"{prefixo}{numero}"
            
            # Criar objeto Carro
            carro = Carro(
                modelo=carro_data["modelo"],
                ano=carro_data["ano"],
                fabricante=carro_data["fabricante"],
                crlv=crlv
            )
            
            # Criar carro e vincular à concessionária
            session.execute_write(self._criar_e_vincular_carro, carro, concessionaria_id)

    def _criar_e_vincular_carro(self, tx, carro: Carro, concessionaria_id: int):
        # Criar nó do carro
        result = tx.run(
            """
            CREATE (c:Carro {
                modelo: $modelo,
                ano: $ano,
                fabricante: $fabricante,
                crlv: $crlv
            })
            RETURN id(c) as id
            """,
            modelo=carro.modelo,
            ano=carro.ano,
            fabricante=carro.fabricante,
            crlv=carro.crlv
        )
        carro_id = result.single()["id"]
        
        # Criar relacionamento entre concessionária e carro
        tx.run(
            """
            MATCH (c:Concessionaria), (car:Carro)
            WHERE id(c) = $concessionaria_id AND id(car) = $carro_id
            CREATE (c)-[:TEM_EM_ESTOQUE]->(car)
            """,
            concessionaria_id=concessionaria_id,
            carro_id=carro_id
        )
        
        return carro_id

    def _criar_concessionaria(self, tx, concessionaria: Concessionaria) -> Concessionaria:
        result = tx.run(
            """
            CREATE (c:Concessionaria {
                nome: $nome
            })
            RETURN id(c) as id, c.nome as nome
            """,
            nome=concessionaria.nome
        )
        record = result.single()
        return Concessionaria(id=record["id"], nome=record["nome"])

    def buscar_concessionaria(self, id: int) -> Optional[Concessionaria]:
        with self.driver.session() as session:
            return session.execute_read(self._buscar_concessionaria, id)

    def _buscar_concessionaria(self, tx, id: int) -> Optional[Concessionaria]:
        result = tx.run(
            """
            MATCH (c:Concessionaria)
            WHERE id(c) = $id
            RETURN id(c) as id, c.nome as nome
            """,
            id=id
        )
        record = result.single()
        if record:
            return Concessionaria(id=record["id"], nome=record["nome"])
        return None

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

    def remover_concessionaria(self, id: int) -> bool:
        with self.driver.session() as session:
            return session.execute_write(self._remover_concessionaria, id)

    def _remover_concessionaria(self, tx, id: int) -> bool:
        result = tx.run(
            """
            MATCH (c:Concessionaria)
            WHERE id(c) = $id
            DETACH DELETE c
            RETURN count(c) as deleted
            """,
            id=id
        )
        return result.single()["deleted"] > 0

    def buscar_todas_concessionarias(self) -> List[Concessionaria]:
        with self.driver.session() as session:
            return session.execute_read(self._buscar_todas_concessionarias)

    def _buscar_todas_concessionarias(self, tx) -> List[Concessionaria]:
        result = tx.run(
            """
            MATCH (c:Concessionaria)
            RETURN id(c) as id, c.nome as nome
            """
        )
        return [Concessionaria(id=record["id"], nome=record["nome"]) for record in result]

    def buscar_carros_concessionaria(self, concessionaria_id: int) -> List[Carro]:
        with self.driver.session() as session:
            return session.execute_read(self._buscar_carros_concessionaria, concessionaria_id)

    def _buscar_carros_concessionaria(self, tx, concessionaria_id: int) -> List[Carro]:
        result = tx.run(
            """
            MATCH (c:Concessionaria)-[:TEM_EM_ESTOQUE]->(car:Carro)
            WHERE id(c) = $id
            RETURN id(car) as id, car.modelo as modelo, car.ano as ano,
                   car.fabricante as fabricante, car.crlv as crlv
            """,
            id=concessionaria_id
        )
        return [
            Carro(
                id=record["id"],
                modelo=record["modelo"],
                ano=record["ano"],
                fabricante=record["fabricante"],
                crlv=record["crlv"]
            )
            for record in result
        ]

    def ler_concessionaria_por_id(self, concessionaria_id: int):
        with self.driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run(
                    """
                    MATCH (c:Concessionaria)
                    WHERE id(c) = $concessionaria_id
                    RETURN c
                    """,
                    concessionaria_id=concessionaria_id
                ).single()
            )
            
            if result:
                concessionaria_data = result["c"]
                print(f"Concessionária encontrada.")
                return Concessionaria.from_dict(dict(concessionaria_data))
            else:
                print(f"Concessionária com id {concessionaria_id} não encontrada.")
                return None

    def buscar_todas_concessionarias(self):
        with self.driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run(
                    """
                    MATCH (c:Concessionaria)
                    RETURN c
                    """
                ).data()
            )
            
            concessionarias = [Concessionaria.from_dict(dict(record["c"])) for record in result]
            print(f"Encontrada(s) {len(concessionarias)} concessionária(s).")
            return concessionarias

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

    def apagar_concessionaria(self, concessionaria_id: int):
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