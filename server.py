# -*- coding: utf-8 -*-
import socket
import threading
import select

# ip host e porta
HOST = '127.0.0.1'
PORT = 9003

# conexão socket
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # criar socket
servidor.bind((HOST, PORT))  # bind

# servidor espera por conexões
servidor.listen(10)

clientes = []
nomes = []
salas = []
paresCliGru = []
paresGruTam = []
all_sockets=[]
paresNamesGru = []


def receive():
    all_sockets.append(servidor)
    while True:
        readable_sock,writable_sock,error_sock=select.select(all_sockets,[],[],0)
        
        for all_socks in readable_sock:
            print('Clientes:')
            print(nomes)
            print('Salas:')
            print(salas)
            print('Pares:')
            print(paresCliGru)

            if all_socks==servidor:
                sockdd, adress = servidor.accept() # aceita conexão e recebe endereços
                print(f'Conectado em {str(adress)}')

                sockdd.send("NICK".encode('utf-8'))
                nome = sockdd.recv(1024).decode('utf-8') # recebe o nome do integrante da sala
                print(f'Apelido: {nome}')
                nomes.append(nome)
                clientes.append(sockdd)

                sockdd.send("GROUP".encode('utf-8'))
                sala = sockdd.recv(1024).decode('utf-8') # recebe o nome da sala
                sala = 'Nome da sala' + sala

                for par in paresGruTam:
                        if par[0] == sala and par[1] > 1:
                            print(par[1])
                            sockdd.send("salaMAX".encode('utf-8'))
                            salaMax = sockdd.recv(1024).decode('utf-8')
                            print(salaMax)
                            continue
                        if par[0] == sala and par[1] < 2:
                            validatesala = False

                print(f'Sala: {sala}')
                if sala not in salas:
                    salas.append(sala) # adiciona a sala a lista, se não tiver ja

                if (sockdd, sala) not in paresCliGru:
                    paresCliGru.append((sockdd, sala)) # adiciona par sockdde/sala a lista de pares
                
                check = True   
                for par in paresGruTam:
                    if par[0] == sala:
                       check = False
                       i = par[1] + 1
                       paresGruTam.remove(par)
                       paresGruTam.append((sala, i))

                if check:
                    paresGruTam.append((sala, 1))

                print(paresGruTam)

                global salaAtual  
                salaAtual = sala

                print(f'{nome} foi adicionado a lista')
                enviaMensagens(f'{nome} entrou no chat!'.encode('utf-8'))  # enviar mensagem de entrada para todos os integrantes da sala

                thread = threading.Thread(target=chat, args=(sockdd,)) # criar thread para cuidar das mensagens
                thread.start()

def chat(cliente): # cuida das mensagens do chat
    while True:
        try:
            msg = cliente.recv(1024) 
            print(msg)              
            
            for par in paresCliGru:
                if par[0] == cliente: # encontra o grupo do cliente que esta enviando a msg
                    global salaAtual 
                    salaAtual = par[1]
                    break

            enviaMensagens(msg)
        except:
            i = clientes.index(client)   
            clientes.remove(client) # remove o cliente da lista se ele sair
            cliente.close()         # fecha conexão
            nome = nomes[i]     
            nomes.remove(nome)      # remove o nome da lista

            for par in paresCliGru:
                if par[0] == cliente:
                    paresCliGru.remove(par) # remove o par do cliente
            
            for sala in salas:
                if sala not in [par[1] for par in paresCliGru]:
                    salas.remove(sala) 

            break

def enviaMensagens(msg): # envia mensagens para os clientes
    print(f'Enviando mensagens, sala {salaAtual}')
    if salaAtual in salas:
        for par in paresCliGru:
            if par[1] == salaAtual: # verifica se o cliente esta no grupo
                par[0].send(msg)


print('servidor online...') # inicia servidor
receive()
