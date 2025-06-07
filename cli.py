import sys
import time

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
        slow_print("-> Funcionalidade de gerenciamento de carros (em desenvolvimento)\n")
    elif choice == '2':
        slow_print("-> Funcionalidade de gerenciamento de clientes (em desenvolvimento)\n")
    elif choice == '3':
        slow_print("-> Funcionalidade de gerenciamento de concessionárias (em desenvolvimento)\n")
    elif choice == '4':
        slow_print("Saindo do sistema. Até logo!")
        sys.exit()
    else:
        slow_print("Opção inválida. Tente novamente.\n")

def run():
    print_banner()
    slow_print("Bem-vindo ao sistema de controle de concessionária!\n", delay=0.03)

    while True:
        main_menu()

if __name__ == "__main__":
    run()
