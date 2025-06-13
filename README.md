# Concessionária

![Logo da Concessionária](documentacao/logo.png)

Projeto que utiliza Mongo e Neo4j para armazenar dados de uma concessionária

## 1. Pré-requisitos

- Docker
- Docker Compose
- Python 3

## 2. Subindo os serviços

```bash
docker-compose up -d
```

Isso inicia:

- 🟢 MongoDB na porta **27017**
- 🔵 Neo4j na interface web: [http://localhost:7474](http://localhost:7474)
  - **Usuário**: `neo4j`
  - **Senha**: `data_data_base`

## 3.1 Acessando os bancos

### MongoDB

Você pode se conectar via terminal com:

```bash
docker exec -it mongo mongosh
```
---

### 3.2 Neo4j

- Acesse: [http://localhost:7474](http://localhost:7474)
- Use:
  - **Usuário**: `neo4j`
  - **Senha**: `data_data_base`

## 4. Parar os serviços

```bash
docker-compose down
```

### Persistência

Os dados são salvos em volumes Docker nomeados:

- Mongo: `mongo_data`
- Neo4j: `neo4j_data`, `neo4j_logs`, `neo4j_import`
