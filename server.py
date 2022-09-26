# -*- coding: utf-8 -*-
import socket
import select

# ip host e porta
HOST = '127.0.0.1'
PORT = 9001

# conexão socket
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # criar socket
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # fornece os meios para controlar o comportamento do socket
servidor.bind((HOST, PORT))  # bind

MAXCLI = 2 # máximo de clientes por sala

# servidor espera por conexões
servidor.listen(MAXCLI)

nomes = []          # lista dos nomes dos clientes
salas = []          # lista dos nomes das salas
paresCliSala = []   # lista de pares (socket do cliente, nome da sala)
paresSalaTam = []   # lista de pares (nome da sala, numero de pessoas na sala)
all_sockets=[]      # lista de todos os sockets
paresSalaNomes = [] # lista de pares (nome da sala, nome do cliente)

def receber():
    all_sockets.append(servidor) # adiciona primeiro socket
    print(f'servidor online na porta {PORT}...') 
    while True:
        # pega a lista de todos os sockets que podem ser lidos através do select
        readable_sock,writable_sock,error_sock=select.select(all_sockets,[],[],0)
        
        for sock in readable_sock:
            if sock==servidor: # se for uma nova conexão
                confirmacao=0       # variável pra validar se ainda tem vaga na sala
               
                # lista os dados que tem no servidor
                print('Clientes:')
                print(nomes)
                print('Salas:')
                print(salas)
                for sala in salas:
                    print(f'Integrantes da sala {sala}:')
                    print(f'\t Nomes:')
                    for par in paresSalaNomes:
                        if par[0]==sala: 
                            print(f'\t\t{par[1]}')

                sockdd, adress = servidor.accept()  # aceita conexão
                all_sockets.append(sockdd)          # adicionan novo socket     
                print(f'Conectado em {str(adress)}')

                sockdd.send("NOME".encode('utf-8'))
                nome = sockdd.recv(1024).decode('utf-8') # recebe o nome do integrante da sala
                print(f'Nome do cliente: {nome}')

                sockdd.send("SALA".encode('utf-8'))
                sala = sockdd.recv(1024).decode('utf-8') # recebe o nome da sala

                for par in paresSalaTam:
                        # verifica se o máximo de clientes numa sala foi atingido
                        # se sim, retorna a esperar por nome do cliente e da sala
                        if par[0] == sala and par[1] > MAXCLI-1:          
                            sockdd.send("salaMAX".encode('utf-8'))
                            confirmacao=1
                            break
                if confirmacao==1:
                    continue

                nomes.append(nome) # adiciona nome a lista
                paresSalaNomes.append((sala,nome)) # adiciona par sala/nome a lista

                print(f'Nome da sala: {sala}')
                if sala not in salas:
                    salas.append(sala) # adiciona a sala a lista, se não tiver já

                if (sockdd, sala) not in paresCliSala:
                    paresCliSala.append((sockdd, sala)) # adiciona par sockdde/sala a lista de pares
                
                check = True   
                for par in paresSalaTam: # incrementa a quantidade de clientes no par sala/quantidade de clientes
                    if par[0] == sala:
                       check = False
                       i = par[1] + 1
                       paresSalaTam.remove(par)
                       paresSalaTam.append((sala, i))
                if check:
                    paresSalaTam.append((sala, 1)) # sala nova -> adiciona novo par sala/1

                global salaAtual  
                salaAtual = sala # variável da sala do cliente que acabou de ser criado

                print(f'{nome} foi adicionado a lista')
                # enviar mensagem de entrada para todos os integrantes da sala
                enviaMensagens(sock,f'{nome} entrou no chat!'.encode('utf-8'))  
            else: # lida com as mensagens, não uma nova conexão
                chat(sock)

    servidor.close()

def chat(cliente): # cuida das mensagens do chat
    try:
        msg = cliente.recv(1024) # recebe mensagem no socket
        print(msg)              
        if msg: # tem alguma mensagem no socket
            for par in paresCliSala:
                if par[0] == cliente: # encontra o grupo do cliente que esta enviando a msg
                    global salaAtual 
                    salaAtual = par[1]
                    break

            enviaMensagens(cliente, msg) 
        else:   # socket quebrado
            if cliente in all_sockets:
                all_sockets.remove(cliente)
    except: # socket está desconectado
        cliente.send("salaMAX".encode('utf-8'))
            
def enviaMensagens(sock, msg): # envia mensagem para todos clientes da sala atual
    print(f'Enviando mensagens, sala {salaAtual}')
    for socketA in all_sockets: 
        if socketA != servidor: # envia somente pro peer
            try:
                if (socketA, salaAtual) in paresCliSala:
                    socketA.send(msg)
            except:
                print('Conexão quebrada!!')
                socketA.close()
                if socketA in all_sockets:
                    all_sockets.remove(socketA)


<<<<<<< HEAD
receber()# inicia servidor
=======
receber()# inicia servidor
>>>>>>> 326113f542d19d3ec03024b1bf17100bb07ea421
