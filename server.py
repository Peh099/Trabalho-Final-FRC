# -*- coding: utf-8 -*-
import socket
import select

# ip host e porta
HOST = '127.0.0.1'
PORT = 9001

# conexão socket
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # criar socket
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PORT))  # bind

# servidor espera por conexões
servidor.listen(10)

clientes = []
nomes = []
salas = []
paresCliGru = []
paresGruTam = []
all_sockets=[]
paresNomesSala = []

def receive():
    all_sockets.append(servidor)
    print(f'servidor online na porta {PORT}...') 
    while True:
        readable_sock,writable_sock,error_sock=select.select(all_sockets,[],[],0)
        
        for sock in readable_sock:
            confirmacao=0
            print('Clientes:')
            print(nomes)
            print('Salas:')
            print(salas)
            for sala in salas:
                print(f'Integrantes da sala {sala}:')
                print(f'\t Nomes:')
                for par in paresNomesSala:
                    if par[0]==sala: 
                        print(f'\t\t{par[1]}')

            if sock==servidor: # nova conexão
                sockdd, adress = servidor.accept() # aceita conexão e recebe endereços
                all_sockets.append(sockdd)
                print(f'Conectado em {str(adress)}')

                sockdd.send("NICK".encode('utf-8'))
                nome = sockdd.recv(1024).decode('utf-8') # recebe o nome do integrante da sala
                print(f'Apelido: {nome}')

                sockdd.send("GROUP".encode('utf-8'))
                sala = sockdd.recv(1024).decode('utf-8') # recebe o nome da sala
                sala = sala

                for par in paresGruTam:
                        if par[0] == sala and par[1] > 1:
                            sockdd.send("salaMAX".encode('utf-8'))
                            confirmacao=1
                            break
                if confirmacao==1:
                    continue
                nomes.append(nome)
                clientes.append(sockdd)
                paresNomesSala.append((sala,nome))

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

                global salaAtual  
                salaAtual = sala

                print(f'{nome} foi adicionado a lista')
                enviaMensagens(sock,f'{nome} entrou no chat!'.encode('utf-8'))  # enviar mensagem de entrada para todos os integrantes da sala
            else: # lida com as mensagens, não nova conexão
                chat(sock)

    servidor.close()

def chat(cliente): # cuida das mensagens do chat
    #while True:
        try:
            msg = cliente.recv(1024) 
            print(msg)              
            if msg:
                for par in paresCliGru:
                    if par[0] == cliente: # encontra o grupo do cliente que esta enviando a msg
                        global salaAtual 
                        salaAtual = par[1]
                        break

                enviaMensagens(cliente, msg)
            else:
                if cliente in all_sockets:
                    all_sockets.remove(cliente)
        except:
            cliente.send("salaMAX".encode('utf-8'))
            
def enviaMensagens(sock, msg): # envia mensagens para os clientes
    print(f'Enviando mensagens, sala {salaAtual}')
    for socketA in all_sockets:
        if socketA != servidor:
            try:
                if (socketA, salaAtual) in paresCliGru:
                    socketA.send(msg)
            except:
                print('Conexão quebrada!!')
                socketA.close()
                if socketA in all_sockets:
                    all_sockets.remove(socketA)


receive()# inicia servidor
