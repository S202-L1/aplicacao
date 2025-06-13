import sys
import time
from config.database import Database
import config.config as config
from daos.carro_dao import CarroDAO, Carro
from daos.cliente_dao import ClienteDAO, Cliente
from daos.concessionaria_dao import ConcessionariaDAO, Concessionaria
from datetime import datetime

def slow_print(text, delay=0.01):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def print_banner():
    banner = r"""
                        ____________________                              
                     //|           |        \                            
                   //  |           |          \                          
      ___________//____|___________|__________()\__________________      
    /__________________|_=_________|_=___________|_________________{}    
    [           ______ |           | .           | ==  ______      { }   
  __[__        /##  ##\|           |             |    /##  ##\    _{# }_ 
 {_____)______|##    ##|___________|_____________|___|##    ##|__(______}
             /  ##__##                              /  ##__##        \    
                                                               
         Sistema de Gestão de Concessionária de Veículos
    MongoDB para dados | Neo4j para relacionamentos inteligentes
"""
    print(banner)

def main_menu():
    print("\nSelecione uma opção:")
    print("1. Gerenciar carros")
    print("2. Gerenciar clientes")
    print("3. Gerenciar concessionárias")
    print("4. Transações")
    print("5. Sair")

    choice = input("Digite sua escolha: ")

    if choice == '1':
        submenu_carros()
    elif choice == '2':
        submenu_clientes()
    elif choice == '3':
        submenu_concessionarias()
    elif choice == '4':
        submenu_transacoes()
    elif choice == '5':
        slow_print("Saindo do sistema. Até logo!")
        sys.exit()
    else:
        slow_print("Opção inválida. Tente novamente.\n")

# ------------------------ CRUD CARROS ------------------------

def submenu_carros():
    while True:
        print("\n--- Menu de Carros ---")
        print("1. Cadastrar novo carro")
        print("2. Listar carros")
        print("3. Atualizar carro")
        print("4. Remover carro")
        print("5. Voltar ao menu principal")

        choice = input("Digite sua escolha: ")

        if choice == '1':
            cadastrar_carro()
        elif choice == '2':
            listar_carros()
        elif choice == '3':
            atualizar_carro()
        elif choice == '4':
            remover_carro()
        elif choice == '5':
            break
        else:
            slow_print("Opção inválida. Tente novamente.\n")

def cadastrar_carro():
    slow_print("\n--- Cadastro de Novo Carro ---")
    
    try:
        modelo = input("Modelo do carro: ")
        ano = int(input("Ano do carro: "))
        fabricante = input("Fabricante do carro: ")
        crlv = input("CRLV do carro: ")

        carro = Carro(modelo=modelo, ano=ano, fabricante=fabricante, crlv=crlv)
        dao = CarroDAO()
        
        carro_id = dao.criar_carro(carro)
        slow_print(f"Carro cadastrado com sucesso! ID: {carro_id}")
        
        dao.close()
    except ValueError:
        slow_print("Erro: O ano deve ser um número inteiro.")
    except Exception as e:
        slow_print(f"Erro ao cadastrar carro: {str(e)}")

def listar_carros():
    slow_print("\n--- Lista de Carros ---")
    
    try:
        dao = CarroDAO()
        carros = dao.buscar_todos_carros()
        
        if not carros:
            slow_print("Nenhum carro cadastrado.")
            return
            
        for carro in carros:
            print(f"\nID: {carro.identificacao}")
            print(f"Modelo: {carro.modelo}")
            print(f"Ano: {carro.ano}")
            print(f"Fabricante: {carro.fabricante}")
            print(f"CRLV: {carro.crlv}")
            # Mostrar concessionária, se houver
            conc_id = dao.buscar_concessionaria_do_carro(carro.identificacao)
            if conc_id:
                conc_dao = ConcessionariaDAO()
                conc = conc_dao.buscar_concessionaria(conc_id)
                print(f"Concessionária: {conc.nome if conc else 'Desconhecida'}")
                conc_dao.close()
            print("-" * 30)
            
        dao.close()
    except Exception as e:
        slow_print(f"Erro ao listar carros: {str(e)}")

def atualizar_carro():
    slow_print("\n--- Atualização de Carro ---")
    
    try:
        carro_id = int(input("Digite o ID do carro a ser atualizado: "))
        
        dao = CarroDAO()
        carro_atual = dao.buscar_carro(carro_id)
        
        if not carro_atual:
            slow_print("Carro não encontrado.")
            return
            
        print("\nDados atuais do carro:")
        print(f"ID: {carro_atual.identificacao}")
        print(f"Modelo: {carro_atual.modelo}")
        print(f"Ano: {carro_atual.ano}")
        print(f"Fabricante: {carro_atual.fabricante}")
        print(f"CRLV: {carro_atual.crlv}")
        
        print("\nDigite os novos dados (deixe em branco para manter o valor atual):")
        modelo = input(f"Novo modelo [{carro_atual.modelo}]: ") or carro_atual.modelo
        ano = input(f"Novo ano [{carro_atual.ano}]: ")
        ano = int(ano) if ano else carro_atual.ano
        fabricante = input(f"Novo fabricante [{carro_atual.fabricante}]: ") or carro_atual.fabricante
        crlv = input(f"Novo CRLV [{carro_atual.crlv}]: ") or carro_atual.crlv
        
        carro_update = Carro(modelo=modelo, ano=ano, fabricante=fabricante, crlv=crlv)
        success = dao.atualizar_carro(carro_id, carro_update)
        
        if success:
            slow_print("Carro atualizado com sucesso!")
        else:
            slow_print("Falha ao atualizar carro.")
            
        dao.close()
    except ValueError:
        slow_print("Erro: O ID e o ano devem ser números inteiros.")
    except Exception as e:
        slow_print(f"Erro ao atualizar carro: {str(e)}")

def remover_carro():
    slow_print("\n--- Remoção de Carro ---")
    
    try:
        carro_id = int(input("Digite o ID do carro a ser removido: "))
        
        dao = CarroDAO()
        carro = dao.buscar_carro(carro_id)
        
        if not carro:
            slow_print("Carro não encontrado.")
            return
            
        print("\nDados do carro a ser removido:")
        print(f"ID: {carro.identificacao}")
        print(f"Modelo: {carro.modelo}")
        print(f"Ano: {carro.ano}")
        print(f"Fabricante: {carro.fabricante}")
        print(f"CRLV: {carro.crlv}")
        
        confirmacao = input("\nTem certeza que deseja remover este carro? (s/N): ").lower()
        
        if confirmacao == 's':
            success = dao.remover_carro(carro_id)
            if success:
                slow_print("Carro removido com sucesso!")
            else:
                slow_print("Falha ao remover carro.")
        else:
            slow_print("Operação cancelada.")
            
        dao.close()
    except ValueError:
        slow_print("Erro: O ID deve ser um número inteiro.")
    except Exception as e:
        slow_print(f"Erro ao remover carro: {str(e)}")

# ------------------------ CRUD CLIENTES ------------------------

def submenu_clientes():
    while True:
        print("\n--- Menu de Clientes ---")
        print("1. Cadastrar novo cliente")
        print("2. Listar clientes")
        print("3. Atualizar cliente")
        print("4. Remover cliente")
        print("5. Voltar ao menu principal")

        choice = input("Digite sua escolha: ")

        if choice == '1':
            cadastrar_cliente()
        elif choice == '2':
            listar_clientes()
        elif choice == '3':
            atualizar_cliente()
        elif choice == '4':
            remover_cliente()
        elif choice == '5':
            break
        else:
            slow_print("Opção inválida. Tente novamente.\n")

def cadastrar_cliente():
    slow_print("\n--- Cadastro de Novo Cliente ---")
    
    try:
        cpf = input("CPF do cliente: ")
        nome = input("Nome do cliente: ")
        nacionalidade = input("Nacionalidade do cliente: ")
        data_nascimento = input("Data de nascimento (YYYY-MM-DD): ")
        data_nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d")

        cliente = Cliente(cpf=cpf, nome=nome, nacionalidade=nacionalidade, data_nascimento=data_nascimento)
        dao = ClienteDAO()
        
        cliente_id = dao.criar_cliente(cliente)
        slow_print(f"Cliente cadastrado com sucesso! ID: {cliente_id}")
        
        dao.close()
    except ValueError as e:
        if "time data" in str(e):
            slow_print("Erro: Formato de data inválido. Use YYYY-MM-DD.")
        else:
            slow_print(f"Erro: {str(e)}")
    except Exception as e:
        slow_print(f"Erro ao cadastrar cliente: {str(e)}")

def listar_clientes():
    slow_print("\n--- Lista de Clientes ---")
    
    try:
        dao = ClienteDAO()
        clientes = dao.buscar_todos_clientes()
        
        if not clientes:
            slow_print("Nenhum cliente cadastrado.")
            return
            
        for cliente in clientes:
            print(f"\nID: {cliente.identificacao}")
            print(f"CPF: {cliente.cpf}")
            print(f"Nome: {cliente.nome}")
            print(f"Nacionalidade: {cliente.nacionalidade}")
            print(f"Data de Nascimento: {cliente.data_nascimento.strftime('%d/%m/%Y')}")
            # Mostrar carros do cliente, se houver
            carros_ids = dao.buscar_carros_do_cliente(cliente.identificacao)
            if carros_ids:
                print("Carros possuídos:")
                carro_dao = CarroDAO()
                for carro_id in carros_ids:
                    carro = carro_dao.buscar_carro(carro_id)
                    if carro:
                        print(f" - Modelo: {carro.modelo}, Fabricante: {carro.fabricante}, Ano: {carro.ano}, CRLV: {carro.crlv}")
                carro_dao.close()
            print("-" * 30)
            
        dao.close()
    except Exception as e:
        slow_print(f"Erro ao listar clientes: {str(e)}")

def atualizar_cliente():
    slow_print("\n--- Atualização de Cliente ---")
    
    try:
        cliente_id = int(input("Digite o ID do cliente a ser atualizado: "))
        
        dao = ClienteDAO()
        cliente_atual = dao.buscar_cliente(cliente_id)
        
        if not cliente_atual:
            slow_print("Cliente não encontrado.")
            return
            
        print("\nDados atuais do cliente:")
        print(f"ID: {cliente_atual.identificacao}")
        print(f"CPF: {cliente_atual.cpf}")
        print(f"Nome: {cliente_atual.nome}")
        print(f"Nacionalidade: {cliente_atual.nacionalidade}")
        print(f"Data de Nascimento: {cliente_atual.data_nascimento.strftime('%d/%m/%Y')}")
        
        print("\nDigite os novos dados (deixe em branco para manter o valor atual):")
        cpf = input(f"Novo CPF [{cliente_atual.cpf}]: ") or cliente_atual.cpf
        nome = input(f"Novo nome [{cliente_atual.nome}]: ") or cliente_atual.nome
        nacionalidade = input(f"Nova nacionalidade [{cliente_atual.nacionalidade}]: ") or cliente_atual.nacionalidade
        data_nascimento = input(f"Nova data de nascimento [{cliente_atual.data_nascimento.strftime('%Y-%m-%d')}]: ")
        data_nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d") if data_nascimento else cliente_atual.data_nascimento
        
        cliente_update = Cliente(cpf=cpf, nome=nome, nacionalidade=nacionalidade, data_nascimento=data_nascimento)
        success = dao.atualizar_cliente(cliente_id, cliente_update)
        
        if success:
            slow_print("Cliente atualizado com sucesso!")
        else:
            slow_print("Falha ao atualizar cliente.")
            
        dao.close()
    except ValueError as e:
        if "time data" in str(e):
            slow_print("Erro: Formato de data inválido. Use YYYY-MM-DD.")
        else:
            slow_print("Erro: O ID deve ser um número inteiro.")
    except Exception as e:
        slow_print(f"Erro ao atualizar cliente: {str(e)}")

def remover_cliente():
    slow_print("\n--- Remoção de Cliente ---")
    
    try:
        cliente_id = int(input("Digite o ID do cliente a ser removido: "))
        
        dao = ClienteDAO()
        cliente = dao.buscar_cliente(cliente_id)
        
        if not cliente:
            slow_print("Cliente não encontrado.")
            return
            
        print("\nDados do cliente a ser removido:")
        print(f"ID: {cliente.identificacao}")
        print(f"CPF: {cliente.cpf}")
        print(f"Nome: {cliente.nome}")
        print(f"Nacionalidade: {cliente.nacionalidade}")
        print(f"Data de Nascimento: {cliente.data_nascimento.strftime('%d/%m/%Y')}")
        
        confirmacao = input("\nTem certeza que deseja remover este cliente? (s/N): ").lower()
        
        if confirmacao == 's':
            success = dao.remover_cliente(cliente_id)
            if success:
                slow_print("Cliente removido com sucesso!")
            else:
                slow_print("Falha ao remover cliente.")
        else:
            slow_print("Operação cancelada.")
            
        dao.close()
    except ValueError:
        slow_print("Erro: O ID deve ser um número inteiro.")
    except Exception as e:
        slow_print(f"Erro ao remover cliente: {str(e)}")

# ------------------------ CRUD CONCESSIONÁRIAS ------------------------

def submenu_concessionarias():
    while True:
        print("\n--- Menu de Concessionárias ---")
        print("1. Cadastrar nova concessionária")
        print("2. Listar concessionárias")
        print("3. Atualizar concessionária")
        print("4. Remover concessionária")
        print("5. Adicionar carro à concessionária")
        print("6. Voltar ao menu principal")

        choice = input("Digite sua escolha: ")

        if choice == '1':
            cadastrar_concessionaria()
        elif choice == '2':
            listar_concessionarias()
        elif choice == '3':
            atualizar_concessionaria()
        elif choice == '4':
            remover_concessionaria()
        elif choice == '5':
            adicionar_carro_concessionaria()
        elif choice == '6':
            break
        else:
            slow_print("Opção inválida. Tente novamente.\n")

def cadastrar_concessionaria():
    slow_print("\n--- Cadastro de Nova Concessionária ---")
    try:
        nome = input("Nome da concessionária: ")
        dao = ConcessionariaDAO()
        # Verifica se já existe uma concessionária com esse nome
        for c in dao.buscar_todas_concessionarias():
            if c.nome == nome:
                slow_print("Já existe uma concessionária com esse nome. O nome deve ser único.")
                dao.close()
                return
        concessionaria = Concessionaria(nome=nome)
        concessionaria_id = dao.criar_concessionaria(concessionaria)
        slow_print(f"Concessionária cadastrada com sucesso! ID: {concessionaria_id}")
        dao.close()
    except Exception as e:
        slow_print(f"Erro ao cadastrar concessionária: {str(e)}")

def listar_concessionarias():
    slow_print("\n--- Lista de Concessionárias ---")
    
    try:
        dao = ConcessionariaDAO()
        concessionarias = dao.buscar_todas_concessionarias()
        
        if not concessionarias:
            slow_print("Nenhuma concessionária cadastrada.")
            return
            
        for concessionaria in concessionarias:
            print(f"\nID: {concessionaria.identificacao}")
            print(f"Nome: {concessionaria.nome}")
            print("Carros em estoque:")
            carros_ids = dao.buscar_carros_da_concessionaria(concessionaria.identificacao)
            if carros_ids:
                for carro_id in carros_ids:
                    carro_data = dao.carro_collection.find_one({"identificacao": carro_id})
                    if carro_data:
                        carro = Carro.from_dict(carro_data)
                        print(f" - Modelo: {carro.modelo}, Fabricante: {carro.fabricante}, Ano: {carro.ano}, CRLV: {carro.crlv}")
            else:
                print("Nenhum carro em estoque")
            print("-" * 30)
            
        dao.close()
    except Exception as e:
        slow_print(f"Erro ao listar concessionárias: {str(e)}")

def atualizar_concessionaria():
    slow_print("\n--- Atualização de Concessionária ---")
    
    try:
        identificacao = input("Digite a identificação da concessionária a ser atualizada: ")
        
        dao = ConcessionariaDAO()
        concessionaria_atual = dao.buscar_concessionaria(identificacao)
        
        if not concessionaria_atual:
            slow_print("Concessionária não encontrada.")
            return
            
        print("\nDados atuais da concessionária:")
        print(f"ID: {concessionaria_atual.identificacao}")
        print(f"Nome: {concessionaria_atual.nome}")
        
        print("\nDigite os novos dados (deixe em branco para manter o valor atual):")
        nome = input(f"Novo nome [{concessionaria_atual.nome}]: ") or concessionaria_atual.nome
        
        concessionaria_update = Concessionaria(nome=nome)
        success = dao.atualizar_concessionaria(identificacao, concessionaria_update)
        
        if success:
            slow_print("Concessionária atualizada com sucesso!")
        else:
            slow_print("Falha ao atualizar concessionária.")
            
        dao.close()
    except Exception as e:
        slow_print(f"Erro ao atualizar concessionária: {str(e)}")

def adicionar_carro_concessionaria():
    slow_print("\n--- Adicionar Carro à Concessionária ---")
    try:
        nome_conc = input("Nome da concessionária: ")
        modelo = input("Modelo do carro: ")
        fabricante = input("Fabricante do carro: ")

        conc_dao = ConcessionariaDAO()
        conc = None
        for c in conc_dao.buscar_todas_concessionarias():
            if c.nome.lower() == nome_conc.lower():
                conc = c
                break
        if not conc:
            slow_print("Concessionária não encontrada.")
            conc_dao.close()
            return

        carro_dao = CarroDAO()
        carro_encontrado = None
        for carro in carro_dao.buscar_todos_carros():
            if carro.modelo.lower() == modelo.lower() and carro.fabricante.lower() == fabricante.lower():
                carro_encontrado = carro
                break
        if not carro_encontrado:
            slow_print("Carro não encontrado.")
            conc_dao.close()
            carro_dao.close()
            return

        # Verifica se o carro já está em alguma concessionária
        conc_atual = carro_dao.buscar_concessionaria_do_carro(carro_encontrado.identificacao)
        if conc_atual:
            slow_print("Este carro já está em uma concessionária.")
            conc_dao.close()
            carro_dao.close()
            return

        # Vincula o carro à concessionária
        success = conc_dao.vincular_carro_a_concessionaria(conc.identificacao, carro_encontrado.identificacao)
        if success:
            slow_print("Carro adicionado à concessionária com sucesso!")
        else:
            slow_print("Falha ao adicionar carro à concessionária.")

        conc_dao.close()
        carro_dao.close()
    except Exception as e:
        slow_print(f"Erro ao adicionar carro à concessionária: {str(e)}")

def remover_concessionaria():
    slow_print("\n--- Remoção de Concessionária ---")
    
    try:
        identificacao = input("Digite a identificação da concessionária a ser removida: ")
        
        dao = ConcessionariaDAO()
        concessionaria = dao.buscar_concessionaria(identificacao)
        
        if not concessionaria:
            slow_print("Concessionária não encontrada.")
            return
            
        print("\nDados da concessionária a ser removida:")
        print(f"ID: {concessionaria.identificacao}")
        print(f"Nome: {concessionaria.nome}")
        
        confirmacao = input("\nTem certeza que deseja remover esta concessionária? (s/N): ").lower()
        
        if confirmacao == 's':
            success = dao.remover_concessionaria(identificacao)
            if success:
                slow_print("Concessionária removida com sucesso!")
            else:
                slow_print("Falha ao remover concessionária.")
        else:
            slow_print("Operação cancelada.")
            
        dao.close()
    except Exception as e:
        slow_print(f"Erro ao remover concessionária: {str(e)}")

# ------------------------ CRUD TRANSACOES ------------------------

def submenu_transacoes():
    while True:
        print("\n--- Menu de Transações ---")
        print("1. Comprar um carro de uma concessionária")
        print("2. Adicionar carro a uma concessionária")
        print("3. Voltar ao menu principal")
        choice = input("Digite sua escolha: ")
        if choice == '1':
            comprar_carro_concessionaria()
        elif choice == '2':
            adicionar_carro_concessionaria_transacao()
        elif choice == '3':
            break
        else:
            slow_print("Opção inválida. Tente novamente.\n")

def adicionar_carro_concessionaria_transacao():
    slow_print("\n--- Adicionar Carro a uma Concessionária ---")
    try:
        nome_conc = input("Nome da concessionária: ")
        modelo = input("Modelo do carro: ")
        fabricante = input("Fabricante do carro: ")

        conc_dao = ConcessionariaDAO()
        conc = None
        for c in conc_dao.buscar_todas_concessionarias():
            if c.nome.lower() == nome_conc.lower():
                conc = c
                break
        if not conc:
            slow_print("Concessionária não encontrada.")
            conc_dao.close()
            return

        carro_dao = CarroDAO()
        carro_encontrado = None
        for carro in carro_dao.buscar_todos_carros():
            if carro.modelo.lower() == modelo.lower() and carro.fabricante.lower() == fabricante.lower():
                carro_encontrado = carro
                break
        if not carro_encontrado:
            slow_print("Carro não encontrado.")
            conc_dao.close()
            carro_dao.close()
            return

        # Verifica se o carro já está em alguma concessionária
        conc_atual = carro_dao.buscar_concessionaria_do_carro(carro_encontrado.identificacao)
        if conc_atual:
            slow_print("Este carro já está em uma concessionária.")
            conc_dao.close()
            carro_dao.close()
            return

        # Vincula o carro à concessionária
        success = conc_dao.vincular_carro_a_concessionaria(conc.identificacao, carro_encontrado.identificacao)
        if success:
            slow_print("Carro adicionado à concessionária com sucesso!")
        else:
            slow_print("Falha ao adicionar carro à concessionária.")

        conc_dao.close()
        carro_dao.close()
    except Exception as e:
        slow_print(f"Erro ao adicionar carro à concessionária: {str(e)}")

def comprar_carro_concessionaria():
    slow_print("\n--- Comprar um Carro de uma Concessionária ---")
    try:
        cpf = input("CPF do comprador: ")
        nome_conc = input("Nome da concessionária: ")
        modelo = input("Modelo do carro: ")
        fabricante = input("Fabricante do carro: ")

        cliente_dao = ClienteDAO()
        cliente = None
        for c in cliente_dao.buscar_todos_clientes():
            if c.cpf == cpf:
                cliente = c
                break
        if not cliente:
            slow_print("Cliente não encontrado.")
            return

        conc_dao = ConcessionariaDAO()
        conc = None
        for c in conc_dao.buscar_todas_concessionarias():
            if c.nome == nome_conc:
                conc = c
                break
        if not conc:
            slow_print("Concessionária não encontrada.")
            return

        carro_dao = CarroDAO()
        carro_encontrado = None
        for carro in carro_dao.buscar_todos_carros():
            if carro.modelo == modelo and carro.fabricante == fabricante:
                # Verifica se o carro está na concessionária
                conc_id = carro_dao.buscar_concessionaria_do_carro(carro.identificacao)
                if conc_id == conc.identificacao:
                    carro_encontrado = carro
                    break
        if not carro_encontrado:
            slow_print("Carro não encontrado na concessionária especificada.")
            return

        # Desvincula o carro da concessionária
        conc_dao.desvincular_carro_da_concessionaria(conc.identificacao, carro_encontrado.identificacao)
        # Vincula o carro ao cliente
        cliente_dao.vincular_carro_ao_cliente(cliente.identificacao, carro_encontrado.identificacao)
        slow_print("Transação realizada com sucesso! O carro agora pertence ao cliente.")
        conc_dao.close()
        cliente_dao.close()
        carro_dao.close()
    except Exception as e:
        slow_print(f"Erro na transação: {str(e)}")

# ------------------------------------------------

def run():
    print_banner()
    slow_print("Bem-vindo ao sistema de controle de concessionária!\n", delay=0.01)

    db = Database(config.NEO4J_URI, config.NEO4J_USERNAME, config.NEO4J_PASSWORD, config.MONGO_URI)
    db.drop_all()
    
    while True:
        main_menu()

if __name__ == "__main__":
    run()
