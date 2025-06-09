import sys
import time
from config.database import Database
import config.config as config
from daos.carro_dao import CarroDAO, Carro

def slow_print(text, delay=0.02):
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
    print("4. Sair")

    choice = input("Digite sua escolha: ")

    if choice == '1':
        submenu_carros()
    elif choice == '2':
        submenu_clientes()
    elif choice == '3':
        submenu_concessionarias()
    elif choice == '4':
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

        carro = Carro(modelo, ano, fabricante, crlv)
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
        carros = dao.buscar_todos_os_carros()
        
        if not carros:
            slow_print("Nenhum carro cadastrado.")
            return
            
        for carro in carros:
            print(f"\nModelo: {carro.modelo}")
            print(f"\nAno: {carro.ano}")
            print(f"\nFabricante: {carro.fabricante}")
            print(f"\nCRLV: {carro.crlv}")
            print("-" * 30)
            
        dao.close()
    except Exception as e:
        slow_print(f"Erro ao listar carros: {str(e)}")

def atualizar_carro():
    slow_print("\n--- Atualização de Carro ---")
    
    try:
        carro_id = int(input("Digite o ID do carro a ser atualizado: "))
        
        dao = CarroDAO()
        carro_atual = dao.ler_carro_por_id(carro_id)
        
        if not carro_atual:
            slow_print("Carro não encontrado.")
            return
            
        print("\nDados atuais do carro:")
        print(f"\nModelo: {carro_atual.modelo}")
        print(f"\nAno: {carro_atual.ano}")
        print(f"\nFabricante: {carro_atual.fabricante}")
        print(f"\nCRLV: {carro_atual.crlv}")
        
        print("\nDigite os novos dados (deixe em branco para manter o valor atual):")
        modelo = input(f"Novo modelo [{carro_atual.modelo}]: ") or carro_atual.modelo
        ano = input(f"Novo ano [{carro_atual.ano}]: ")
        ano = int(ano) if ano else carro_atual.ano
        fabricante = input(f"Novo fabricante [{carro_atual.fabricante}]: ") or carro_atual.fabricante
        crlv = input(f"Novo CRLV [{carro_atual.crlv}]: ") or carro_atual.crlv
        
        carro_update = Carro(modelo, ano, fabricante, crlv)
        success = dao.atualizar_carro(carro_id, carro_update)
        
        if success:
            slow_print("Carro atualizado com sucesso!")
            
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
        carro = dao.ler_carro_por_id(carro_id)
        
        if not carro:
            slow_print("Carro não encontrado.")
            return
            
        print("\nDados do carro a ser removido:")
        print(f"Modelo: {carro.modelo}")
        print(f"Ano: {carro.ano}")
        print(f"Fabricante: {carro.fabricante}")
        print(f"CRLV: {carro.crlv}")
        
        confirmacao = input("\nTem certeza que deseja remover este carro? (s/N): ").lower()
        
        if confirmacao == 's':
            success = dao.apagar_carro(carro_id)
            if success:
                slow_print("Carro removido com sucesso!")
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
    slow_print("-> Aqui será inserido um novo cliente no banco de dados.\n")

def listar_clientes():
    slow_print("\n--- Lista de Clientes ---")
    slow_print("-> Aqui serão listados os clientes armazenados no banco de dados.\n")

def atualizar_cliente():
    slow_print("\n--- Atualização de Cliente ---")
    slow_print("-> Aqui será buscado e atualizado um cliente existente no banco de dados.\n")

def remover_cliente():
    slow_print("\n--- Remoção de Cliente ---")
    slow_print("-> Aqui será removido um cliente do banco de dados.\n")

# ------------------------ CRUD CONCESSIONÁRIAS ------------------------

def submenu_concessionarias():
    while True:
        print("\n--- Menu de Concessionárias ---")
        print("1. Cadastrar nova concessionária")
        print("2. Listar concessionárias")
        print("3. Atualizar concessionária")
        print("4. Remover concessionária")
        print("5. Voltar ao menu principal")

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
            break
        else:
            slow_print("Opção inválida. Tente novamente.\n")

def cadastrar_concessionaria():
    slow_print("\n--- Cadastro de Nova Concessionária ---")
    slow_print("-> Aqui será inserida uma nova concessionária no banco de dados.\n")

def listar_concessionarias():
    slow_print("\n--- Lista de Concessionárias ---")
    slow_print("-> Aqui serão listadas as concessionárias armazenadas no banco de dados.\n")

def atualizar_concessionaria():
    slow_print("\n--- Atualização de Concessionária ---")
    slow_print("-> Aqui será buscada e atualizada uma concessionária existente no banco de dados.\n")

def remover_concessionaria():
    slow_print("\n--- Remoção de Concessionária ---")
    slow_print("-> Aqui será removida uma concessionária do banco de dados.\n")

# ------------------------------------------------

def run():
    print_banner()
    slow_print("Bem-vindo ao sistema de controle de concessionária!\n", delay=0.03)

    db = Database(config.NEO4J_URI, config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    db.drop_all()
    
    while True:
        main_menu()

if __name__ == "__main__":
    run()
