import mysql.connector
from mysql.connector import Error
import random
import string

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
# Funções de Interação (CRUD / Procedures)
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
        print("\n[+] Reserva criada com sucesso! (Status: Pendente)")
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

def listar_voos_futuros(conn):
    print("\n--- Painel de Voos Futuros (View) ---")
    try:
        cursor = conn.cursor()
        # Consultando a View vw_voos_futuros que filtra automaticamente datas maiores que NOW()
        cursor.execute("SELECT id_voo, numero_voo, origem, destino, partida_prevista, chegada_prevista, aeronave_modelo FROM vw_voos_futuros")
        voos = cursor.fetchall()
        
        if not voos:
            print("[-] Nenhum voo futuro agendado no momento.")
        else:
            # Cabeçalho formatado para alinhamento no terminal
            print(f"{'ID':<4} | {'Nº VOO':<8} | {'ORIGEM':<6} | {'DESTINO':<7} | {'PARTIDA':<19} | {'CHEGADA':<19} | {'AERONAVE':<15}")
            print("-" * 92)
            for v in voos:
                # Tratamento para exibir a data formatada caso o connector retorne objetos datetime
                partida = v[4].strftime('%Y-%m-%d %H:%M:%S') if hasattr(v[4], 'strftime') else v[4]
                chegada = v[5].strftime('%Y-%m-%d %H:%M:%S') if hasattr(v[5], 'strftime') else v[5]
                
                print(f"{v[0]:<4} | {v[1]:<8} | {v[2]:<6} | {v[3]:<7} | {partida:<19} | {chegada:<19} | {v[6]:<15}")
    except Error as e:
        print(f"\n[!] Erro ao listar voos futuros: {e}")
    finally:
        if cursor:  # type: ignore
            cursor.close() # type: ignore

def listar_reservas_completas(conn):
    print("\n--- Visão Geral de Reservas ---")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_reserva, codigo_reserva, cliente, passageiro, numero_voo, status_pagamento FROM vw_reservas_completas")
        reservas = cursor.fetchall()
        
        if not reservas:
            print("Nenhuma reserva ativa com bilhete emitido encontrada.")
        else:
            print(f"{'ID':<4} | {'CÓDIGO':<10} | {'CLIENTE':<20} | {'VOO':<10} | {'STATUS':<15}")
            print("-" * 65)
            for r in reservas:
                print(f"{r[0]:<4} | {r[1]:<10} | {r[2][:20]:<20} | {r[4]:<10} | {r[5]:<15}")
    except Error as e:
        print(f"\n[!] Erro ao listar reservas: {e}")
    finally:
        if cursor: cursor.close() # type: ignore

def confirmar_pagamento(conn):
    print("\n--- Confirmar Pagamento de Reserva ---")
    id_reserva = input("ID da Reserva: ")
    try:
        cursor = conn.cursor()
        cursor.callproc('sp_confirmar_pagamento', (id_reserva,))
        conn.commit()
        print(f"\n[+] Pagamento da reserva ID {id_reserva} confirmado com sucesso!")
    except Error as e:
        print(f"\n[!] Erro ao confirmar pagamento: {e}")
    finally:
        if cursor: cursor.close() # type: ignore

def cancelar_reserva(conn):
    print("\n--- Cancelar Reserva ---")
    id_reserva = input("ID da Reserva: ")
    try:
        cursor = conn.cursor()
        cursor.callproc('sp_cancelar_reserva', (id_reserva,))
        conn.commit()
        print(f"\n[-] Reserva ID {id_reserva} alterada para 'Cancelado'.")
    except Error as e:
        print(f"\n[!] Erro ao cancelar reserva: {e}")
    finally:
        if cursor: cursor.close() # type: ignore

def cadastrar_voo(conn):
    print("\n--- Cadastrar Novo Voo ---")
    numero = input("Número do Voo (ex: G31920): ")
    origem = input("Origem (3 letras, ex: GRU): ").upper()
    destino = input("Destino (3 letras, ex: JFK): ").upper()
    print("Use o formato YYYY-MM-DD HH:MM:SS para as datas.")
    partida = input("Partida Prevista: ")
    chegada = input("Chegada Prevista: ")
    modelo = input("Modelo da Aeronave (ex: Boeing 737): ")

    try:
        cursor = conn.cursor()
        # Chama a procedure que acabamos de criar no banco
        cursor.callproc('sp_cadastrar_voo', (numero, origem, destino, partida, chegada, modelo))
        conn.commit()
        print(f"\n[+] Voo {numero} cadastrado com sucesso!")
    except Error as e:
        # Aqui o trigger trg_validar_datas_voo fará efeito se a data for inválida
        print(f"\n[!] Erro ao cadastrar voo: {e}")
    finally:
        if cursor: cursor.close() # type: ignore

def emitir_bilhete(conn):
    print("\n--- Emitir Bilhete ---")
    id_reserva = input("ID da Reserva: ")
    id_voo = input("ID do Voo: ")
    id_passageiro = input("ID do Passageiro: ")
    
    # Gera um número de bilhete aleatório (ex: TK-A1B2C3D4)
    sufixo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    numero_bilhete = f"TK-{sufixo}"
    print(f"[*] Número do Bilhete gerado automaticamente: {numero_bilhete}")
    
    assento = input("Assento (ex: 12A): ").upper()
    
    print("Classes disponíveis: 1 - Economica | 2 - Executiva | 3 - Primeira Classe")
    op_classe = input("Escolha a Classe (1/2/3): ")
    if op_classe == '2': 
        classe = 'Executiva'
    elif op_classe == '3': 
        classe = 'Primeira Classe'
    else: 
        classe = 'Economica'
        
    preco = input("Preço Pago (ex: 1500.50): ")

    try:
        cursor = conn.cursor()
        # sp_emitir_bilhete exige: id_reserva, id_voo, id_passageiro, numero_bilhete, assento, classe, preco
        cursor.callproc('sp_emitir_bilhete', (
            int(id_reserva), 
            int(id_voo), 
            int(id_passageiro), 
            numero_bilhete, 
            assento, 
            classe, 
            float(preco)
        ))
        conn.commit()
        print(f"\n[+] Sucesso! Bilhete emitido para o assento {assento} na classe {classe}.")
    except ValueError:
         print("\n[!] Erro: IDs e Preço devem ser valores numéricos válidos.")
    except Error as e:
        # A MÁGICA ACONTECE AQUI: 
        # Se o preço for <= 0 ou o assento já estiver ocupado, o MySQL aborta a transação,
        # envia o erro 45000 configurado nos seus Triggers/Procedures, e o Python imprime aqui:
        print(f"\n[!] Falha na emissão (Regra de Negócio): {e}")
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
        print("3. Cadastrar Voo (Novo)")
        print("4. Buscar Voos")
        print("5. Listar Voos Futuros")
        print("6. Criar Reserva (Pendente)")
        print("7. Confirmar Pagamento de Reserva")
        print("8. Emitir Bilhete / Marcar Assento (Novo)")
        print("9. Ver Reservas Detalhadas")
        print("10. Cancelar Reserva")
        print("0. Sair")
        print("="*40)
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1': cadastrar_cliente(conn)
        elif opcao == '2': cadastrar_passageiro(conn)
        elif opcao == '3': cadastrar_voo(conn)
        elif opcao == '4': buscar_voos(conn)
        elif opcao == '5': listar_voos_futuros(conn)
        elif opcao == '6': criar_reserva(conn)
        elif opcao == '7': confirmar_pagamento(conn)
        elif opcao == '8': emitir_bilhete(conn)
        elif opcao == '9': listar_reservas_completas(conn)
        elif opcao == '10': cancelar_reserva(conn)
        elif opcao == '0':
            print("\nEncerrando o sistema. Até logo!")
            break
        else:
            print("\n[!] Opção inválida. Tente novamente.")

    if conn and conn.is_connected():
        conn.close()

if __name__ == '__main__':
    main()