import mysql.connector
from mysql.connector import Error
import datetime

# ==========================================
# Configuração de Conexão
# ==========================================
def conectar_banco():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='companhiaaerea',
            user='root',
            password='root'
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"\n[!] Erro ao conectar ao MySQL: {e}")
        return None

# ==========================================
# Funções de Interação (Procedures e Views)
# ==========================================
def cadastrar_cliente(conn):
    print("\n--- Cadastrar Novo Cliente ---")
    nome = input("Nome: ")
    email = input("E-mail: ")
    telefone = input("Telefone: ")
    documento = input("Documento Fiscal (CPF/CNPJ): ")
    
    try:
        cursor = conn.cursor()
        cursor.callproc('sp_cadastrar_cliente', (nome, email, telefone, documento))
        conn.commit()
        print("\n[+] Cliente cadastrado com sucesso!")
    except Error as e:
        print(f"\n[!] Erro ao cadastrar cliente: {e}")
    finally:
        if cursor: cursor.close() # type: ignore

def cadastrar_passageiro(conn):
    print("\n--- Cadastrar Novo Passageiro ---")
    nome = input("Nome Completo: ")
    documento = input("Documento de Identidade: ")
    data_nascimento = input("Data de Nascimento (YYYY-MM-DD): ")
    
    try:
        cursor = conn.cursor()
        cursor.callproc('sp_cadastrar_passageiro', (nome, documento, data_nascimento))
        conn.commit()
        print("\n[+] Passageiro cadastrado com sucesso!")
    except Error as e:
        print(f"\n[!] Erro ao cadastrar passageiro: {e}")
    finally:
        if cursor: cursor.close() # type: ignore

def criar_reserva(conn):
    print("\n--- Criar Reserva ---")
    id_cliente = input("ID do Cliente: ")
    codigo_reserva = input("Código da Reserva (ex: RES001): ")
    
    try:
        cursor = conn.cursor()
        cursor.callproc('sp_criar_reserva', (id_cliente, codigo_reserva))
        conn.commit()
        print("\n[+] Reserva criada com sucesso! (Status Pendente)")
    except Error as e:
        print(f"\n[!] Erro ao criar reserva: {e}")
    finally:
        if cursor: cursor.close() # type: ignore

def buscar_voos(conn):
    print("\n--- Buscar Voos Disponíveis ---")
    origem = input("Origem (3 letras, ex: GRU): ").upper()
    destino = input("Destino (3 letras, ex: JFK): ").upper()
    
    try:
        cursor = conn.cursor()
        cursor.callproc('sp_buscar_voos', (origem, destino))
        
        encontrou = False
        for result in cursor.stored_results():
            voos = result.fetchall()
            for voo in voos:
                encontrou = True
                print(f"ID: {voo[0]} | Voo: {voo[1]} | Saída: {voo[4]} | Chegada: {voo[5]} | Modelo: {voo[6]}")
        
        if not encontrou:
            print("\n[-] Nenhum voo encontrado para essa rota com data futura.")
            
    except Error as e:
        print(f"\n[!] Erro ao buscar voos: {e}")
    finally:
        if cursor: cursor.close() # type: ignore

def listar_reservas_completas(conn):
    print("\n--- Visão Geral de Reservas ---")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo_reserva, cliente, passageiro, numero_voo, status_pagamento FROM vw_reservas_completas")
        reservas = cursor.fetchall()
        
        if not reservas:
            print("Nenhuma reserva encontrada.")
        else:
            print(f"{'CÓDIGO':<10} | {'CLIENTE':<20} | {'PASSAGEIRO':<20} | {'VOO':<10} | {'STATUS':<15}")
            print("-" * 85)
            for r in reservas:
                print(f"{r[0]:<10} | {r[1][:20]:<20} | {r[2][:20]:<20} | {r[3]:<10} | {r[4]:<15}")
    except Error as e:
        print(f"\n[!] Erro ao listar reservas: {e}")
    finally:
        if cursor: cursor.close() # type: ignore


# ==========================================
# Menu Principal CLI
# ==========================================
def main():
    conn = conectar_banco()
    if not conn:
        return

    while True:
        print("\n" + "="*40)
        print(" SISTEMA COMPANHIA AÉREA BULOVASK ")
        print("="*40)
        print("1. Cadastrar Cliente")
        print("2. Cadastrar Passageiro")
        print("3. Buscar Voos")
        print("4. Criar Reserva")
        print("5. Ver Reservas Completas (View)")
        print("0. Sair")
        print("="*40)
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            cadastrar_cliente(conn)
        elif opcao == '2':
            cadastrar_passageiro(conn)
        elif opcao == '3':
            buscar_voos(conn)
        elif opcao == '4':
            criar_reserva(conn)
        elif opcao == '5':
            listar_reservas_completas(conn)
        elif opcao == '0':
            print("\nEncerrando o sistema. Até logo!")
            break
        else:
            print("\n[!] Opção inválida. Tente novamente.")

    if conn and conn.is_connected():
        conn.close()

if __name__ == '__main__':
    main()