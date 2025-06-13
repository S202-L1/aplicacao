from neo4j import GraphDatabase
from pymongo import MongoClient

class Database:
    def __init__(self, uri, user, password, mongo_uri):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.mongo_client = MongoClient(mongo_uri)
        self.mongo_db = self.mongo_client["concessionaria"]

    def close(self):
        self.driver.close()
        self.mongo_client.close()

    def execute_query(self, query, parameters=None):
        data = []
        with self.driver.session() as session:
            results = session.run(query, parameters)
            for record in results:
                data.append(record)
            return data
        
    def drop_all(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        self.mongo_db["carros"].drop()
        self.mongo_db["clientes"].drop()
        self.mongo_db["concessionarias"].drop()