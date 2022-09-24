import socket
import threading
import select
import sys
# se não tiver o tkinter, instale-o com o comando: sudo apt install python3-tk
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import messagebox

# ip host e porta
HOST = '127.0.0.1'
PORT = 9001


class Client:

    def __init__(self, host, port):
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM) # cria socket
        
        self.socket.connect((host, port))       # conecta ao host

        msg = tkinter.Tk()
        msg.withdraw()

        self.nome = simpledialog.askstring(
            "Nome", "Digite seu nome:")         # pergunta nome

        self.sala = simpledialog.askstring(
            "Sala", "Escolha sua sala:")        # pergunta nome da sala
        
        # self.sala = simpledialog.askstring(
        #     "sala", "Escolha seu grupo:")

        # self.salaMax = messagebox.showerror("ERROR!!", "Esse grupo está cheio")

        self.front_done = False
        self.running = True

        # thread que recebe mensagens
        front_thread = threading.Thread(target=self.front)
        receive_thread = threading.Thread(target=self.receive)
        front_thread.start()
        receive_thread.start()

    def front(self): # front-end
        # janela
        self.win = tkinter.Tk()
        self.win.configure(bg="lightblue")
        self.win.title("Bate Papo")
        self.win.geometry("400x400")

        # input
        self.chat_label = tkinter.Label(
            self.win, text=self.sala, bg='lightblue')
        self.chat_label.configure(font=("Courier", 12))
        self.chat_label.pack(padx=20, pady=5)

        # text box
        self.chat_text = tkinter.scrolledtext.ScrolledText(
            self.win, width=40, height=10)
        self.chat_text.pack(padx=20, pady=5)

        # label 
        self.input_label = tkinter.Label(
            self.win, text="Mensagem", bg='lightblue')
        self.input_label.pack(padx=20, pady=5)

        # texto de entrada
        self.input_text = tkinter.Entry(self.win, width=40)
        self.input_text.configure(font=("Courier", 12))
        self.input_text.pack(padx=20, pady=5)

        # botao enviar
        self.send_button = tkinter.Button(
            self.win, text="Enviar", command=self.entrada)
        self.send_button.pack(padx=20, pady=5)

        self.front_done = True

        # fechar janela 
        self.win.protocol("WM_DELETE_WINDOW", self.fecha_janela)
        self.win.mainloop()

    def entrada(self):
        mensagem = f"{self.nome}: {self.input_text.get()}"   # msg do input
        
        self.socket.send(mensagem.encode('utf-8'))           # envia msg
       
        self.input_text.delete(first=0, last='end')         # limpar input

    def fecha_janela(self):
        self.running = False    # para loop
        self.win.destroy()      # fecha janela
       # send...
        self.socket.close()     # fecha socket
        exit(0)


    def receive(self):
        while self.running:
            all_sockets=[sys.stdin,self.socket]
            readable,writable,error_s=select.select(all_sockets,[],[])
            for each_sock in readable:
                if each_sock==self.socket:
                    try:
                        mensagem = each_sock.recv(1024).decode('utf-8')
                        if mensagem == 'NICK':
                            self.socket.send(self.nome.encode('utf-8'))  # envia nome
                        elif mensagem == 'GROUP':
                            self.socket.send(self.sala.encode('utf-8'))   # envia nome da sala
                        elif mensagem == 'GROUPMAX':
                            self.socket.send("GRUPO CHEIO".encode('utf-8'))
                        else:
                            if self.front_done:
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


def iniciate():
    client = Client(HOST, PORT)

iniciate()
