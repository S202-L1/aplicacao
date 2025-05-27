# Concessionária

🚧🚧🚧

Projeto que utiliza Mongo e Neo4j para armazenar dados de uma concessionária

## 🔧 Pré-requisitos

- Docker
- Docker Compose
- Python 3

## Subindo os serviços

```bash
docker-compose up -d
```

Isso inicia:

- 🟢 MongoDB na porta **27017**
- 🔵 Neo4j na interface web: [http://localhost:7474](http://localhost:7474)
  - **Usuário**: `neo4j`
  - **Senha**: `test123`

## 🛠️ Acessando os bancos

### MongoDB

Você pode se conectar via terminal com:

```bash
docker exec -it mongo mongosh
```
---

### Neo4j

- Acesse: [http://localhost:7474](http://localhost:7474)
- Use:
  - **Usuário**: `neo4j`
  - **Senha**: `test123`

## ⛔ Parar os serviços

```bash
docker-compose down
```

## Persistência

Os dados são salvos em volumes Docker nomeados:

- Mongo: `mongo_data`
- Neo4j: `neo4j_data`, `neo4j_logs`, `neo4j_import`
