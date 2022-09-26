import socket
import threading
import select
import sys
from tkinter import *
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import messagebox

import PySimpleGUI as sg

sg.theme('SandyBeach')  

# ip host e porta
HOST = '127.0.0.1'
PORT = 9001

def rgb_hack(rgb):
    return "#%02x%02x%02x" % rgb

class Cliente:

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria socket
        self.socket.connect((host, port))       # conecta ao host
        
        # cria layout da caixa que pergunta o nome e sala
        layout = [
        [sg.Text('Digite seu nome:', size =(15, 1),font=(50), pad=(15,15)), sg.InputText(size =(20),font=(50))],
        [sg.Text('Digite a sua sala:', size =(15, 1),font=(50), pad=(15,15)), sg.InputText(size =(20),font=(50))],
        [sg.Submit('Confirmar',size =(15, 1),font=(50),pad=(15,20)), sg.Cancel('Cancelar',size =(15, 1),font=(50),pad=(15,20))]
        ]

        title='Seja Bem-Vindo!'
        window = sg.Window(title, layout,size=(400,220))
        event, values = window.read()
        window.close()
        
        self.nome = values [0] # Guarda o nome do cliente numa variável

        self.sala = values [1] # Guarda o nome da sala numa varíavel
 
        self.mensagem = Label(text="")
        self.mensagem.pack()

        self.front_pronto = False
        self.running = True

        # thread que recebe mensagens no front
        front_thread = threading.Thread(target=self.front)
        front_thread.start()
        
        self.receber() # função que recebe as mensagens

    def front(self): # front-end
        # janela
        self.win = tkinter.Tk()
        self.win.configure(bg=rgb_hack((178, 50, 126)))
        self.win.title("Bate Papo")
        self.win.option_add('*Font', '22')
        self.win.geometry("800x600")

        # label nome da sala
        self.chat_label = tkinter.Label(
        self.win, text='Nome da sala: '+self.sala, bg=rgb_hack((178, 50, 126)),height=2)
        self.chat_label.configure(font=("Arial", 15))
        self.chat_label.pack(padx=20, pady=3)

        # label membros
        self.chat_members = tkinter.Label(
        self.win, text="Membros:", bg=rgb_hack((178, 50, 126)),height=2)
        self.chat_members.configure(font=("Arial", 15))
        self.chat_members.pack(padx=20, pady=0)

        #text box dos membros
        self.chat_text_members = tkinter.scrolledtext.ScrolledText(
            self.win, width=40, height=5)
        self.chat_text_members.pack(padx=20, pady=3)

        # text box do chat das mensagens
        self.chat_text = tkinter.scrolledtext.ScrolledText(
            self.win, width=40, height=10)
        self.chat_text.pack(padx=20, pady=5)

        # label da mensagem
        self.input_label = tkinter.Label(
            self.win, text="Mensagem", bg=rgb_hack((178, 50, 126)))
        self.input_label.pack(padx=20, pady=5)

        # input da mensagem
        self.input_text = tkinter.Entry(self.win, width=40)
        self.input_text.configure(font=("Courier", 12))
        self.input_text.pack(padx=20, pady=5)

        # botao enviar
        self.send_button = tkinter.Button(
            self.win, text="Enviar", command=self.entrada)
        self.send_button.pack(padx=20, pady=5)

        self.front_pronto = True 

        # fechar janela 
        self.win.protocol("WM_DELETE_WINDOW", self.fecha_janela)
        self.win.mainloop()

    def entrada(self):
        mensagem = f"{self.nome}: {self.input_text.get()}"   # msg do input
        
        self.socket.send(mensagem.encode('utf-8'))           # envia msg
       
        self.input_text.delete(first=0, last='end')         # limpa input

    def fecha_janela(self):
        self.running = False    # para o loop
        self.win.destroy()      # fecha janela
        self.socket.close()     # fecha socket
        sys.exit()
    
    def receber(self):
        listaDeMembros=[]
        while self.running:
            all_sockets=[sys.stdin,self.socket] # adiciona o socket a lista
            # pega a lista de todos os sockets que podem ser lidos através do select
            readable,writable,error_s=select.select(all_sockets,[],[])
           
            for each_sock in readable:
                if each_sock==self.socket:
                    try:
                        # recebe mensagem do servidor
                        mensagem = each_sock.recv(1024).decode('utf-8') 
                        if mensagem == 'NOME': # envia nome do cliente
                            self.socket.send(self.nome.encode('utf-8')) 
                        elif mensagem == 'SALA': # envia nome da sala
                            self.socket.send(self.sala.encode('utf-8'))   
                        elif mensagem == 'salaMAX': # se a sala tiver cheia fecha janela
                            print("A sala está lotada. Tente outra.")
                            self.running= False
                            self.win.destroy()
                            self.socket.close()  
                            sys.exit()

                        else:
                            if self.front_pronto:  # chat foi renderizado
                                # adiciona cliente que enviou mensagem ao quadro de membros, 
                                # se ainda não estiver
                                membro=mensagem.split()
                                if membro[0][:-1] not in listaDeMembros and mensagem.find(":")!=-1:
                                    listaDeMembros.append(membro[0][:-1])
                                    self.chat_text_members.config(state='normal')
                                    self.chat_text_members.insert('end', membro[0][:-1] + '\n')
                                    self.chat_text_members.yview('end')
                                    self.chat_text_members.config(state='disabled')
                                # adiciona mensagem ao chat
                                self.chat_text.config(state='normal')
                                self.chat_text.insert('end', mensagem + '\n')
                                self.chat_text.yview('end')
                                self.chat_text.config(state='disabled')
                                
                    except ConnectionAbortedError():
                        break
                    except:
                        print("Error")
                        self.sock.close() 
                        break



def inicia(): 
    client = Cliente(HOST, PORT)

inicia() # inicia cliente
