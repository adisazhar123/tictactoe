import tkinter
from tkinter import StringVar, Label, Entry, Button, DISABLED
import threading
from tkinter import messagebox

import Pyro4
import shortuuid
import re
from Pyro4.errors import CommunicationError


class GameGui(threading.Thread):
    def __init__(self, master):
        threading.Thread.__init__(self)
        self.master = master

        self.player_a_name = StringVar()
        self.player_b_name = StringVar()

        self.main_server = self.connect_to_server('main_server')
        self.game_room_server = None

        self.b_click = True
        self.flag = 0

        # init types
        self.TYPE_SPECTATOR = 'spectator'
        self.TYPE_PLAYER = 'player'

        self.TYPE_PLAYER_X = 'player:x'
        self.TYPE_PLAYER_O = 'player:o'

        self.identifier = shortuuid.uuid()
        self.role = None

        self.button_mapping = {}

        label = Label(self.master, text="Tic Tac Toe", font='Times 20 bold', bg='white', fg='black')
        label.grid(row=1, column=0, columnspan=8)

        self.buttons = StringVar()
        self.init_list_of_game_rooms()

        # self.init_game_buttons()

    def init_game_positions(self):
        self.positions = [None] * 9

    def init_list_of_game_rooms(self):
        self.game_rooms_available_label = Label(self.master, text="Game rooms available", font='Times 20', fg='black')
        self.game_rooms_available_label.grid(row=2, column=0)

        self.button_create_game_room = Button(self.master, text="Create game room", font='Times 20', bg='gray', fg='white', command=lambda: self.create_game_room_server())
        self.button_create_game_room.grid(row=4, column=0)

        self.list_box = tkinter.Listbox(self.master, width=20, font='Times 24')
        self.list_box.grid(row=3, column=0)
        self.list_box.bind('<Double-1>', self.list_box_double_click_handler)

        rooms_response = self.main_server.available_rooms_func()
        print(rooms_response)
        self.render_list_of_game_rooms(rooms_response['data'])

    def init_player_labels(self):
        label = Label(self.master, text="Player 1:", font='Times 20 bold', bg='white', fg='black', height=1, width=8)
        label.grid(row=1, column=0)

        label = Label(self.master, text="Player 2:", font='Times 20 bold', bg='white', fg='black', height=1, width=8)
        label.grid(row=2, column=0)

        self.player1_name_entry = Entry(self.master, textvariable=self.player_a_name, bd=5)
        self.player1_name_entry.grid(row=1, column=1, columnspan=8)
        self.player2_name_entry = Entry(self.master, textvariable=self.player_b_name, bd=5)
        self.player2_name_entry.grid(row=2, column=1, columnspan=8)

    def init_game_screen(self):
        self.list_box.destroy()
        self.button_create_game_room.destroy()
        self.game_rooms_available_label.destroy()

        # self.init_player_labels()
        self.init_game_buttons()
        self.init_game_positions()

    def init_game_buttons(self):
        self.button1 = Button(self.master, text='', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                              command=lambda: self.btnClick(self.button1))
        self.button1.grid(row=3, column=0)

        self.button_mapping[self.button1] = 1

        self.button2 = Button(self.master, text='', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                              command=lambda: self.btnClick(self.button2))
        self.button2.grid(row=3, column=1)

        self.button_mapping[self.button2] = 2

        self.button3 = Button(self.master, text='', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                              command=lambda: self.btnClick(self.button3))
        self.button3.grid(row=3, column=2)

        self.button_mapping[self.button3] = 3

        self.button4 = Button(self.master, text='', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                              command=lambda: self.btnClick(self.button4))
        self.button4.grid(row=4, column=0)

        self.button_mapping[self.button4] = 4

        self.button5 = Button(self.master, text='', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                              command=lambda: self.btnClick(self.button5))
        self.button5.grid(row=4, column=1)

        self.button_mapping[self.button5] = 5

        self.button6 = Button(self.master, text='', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                              command=lambda: self.btnClick(self.button6))
        self.button6.grid(row=4, column=2)

        self.button_mapping[self.button6] = 6

        self.button7 = Button(self.master, text='', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                              command=lambda: self.btnClick(self.button7))
        self.button7.grid(row=5, column=0)

        self.button_mapping[self.button7] = 7

        self.button8 = Button(self.master, text='', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                              command=lambda: self.btnClick(self.button8))
        self.button8.grid(row=5, column=1)

        self.button_mapping[self.button8] = 8

        self.button9 = Button(self.master, text='', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                              command=lambda: self.btnClick(self.button9))
        self.button9.grid(row=5, column=2)

        self.button_mapping[self.button9] = 9

    def create_game_room_server(self):
        response = self.main_server.create_room_func()
        rooms_response = self.main_server.available_rooms_func()
        self.render_list_of_game_rooms(rooms_response['data'])

        if response['status'] == 'ok':
            tkinter.messagebox.showinfo("Tic-Tac-Toe", response['message'])

    def disableButton(self):
        self.button1.configure(state=DISABLED)
        self.button2.configure(state=DISABLED)
        self.button3.configure(state=DISABLED)
        self.button4.configure(state=DISABLED)
        self.button5.configure(state=DISABLED)
        self.button6.configure(state=DISABLED)
        self.button7.configure(state=DISABLED)
        self.button8.configure(state=DISABLED)
        self.button9.configure(state=DISABLED)

    def list_box_double_click_handler(self, event):
        selected = self.list_box.get(self.list_box.curselection())
        code = selected.split(' ')[1]
        game_room_server_name = "game_room_server_{}".format(code)

        self.game_room_server = self.connect_to_server(game_room_server_name)
        response = self.game_room_server.connect({'identifier': self.identifier}, self.TYPE_PLAYER)
        print(response)
        if response['status'] == 'ok':
            self.role = response['data']['participant_type']
            self.positions = response['data']['positions']

            self.init_game_screen()
            tkinter.messagebox.showinfo("Tic-Tac-Toe", response['message'])

    def btnClick(self, buttons):
        location = self.button_mapping[buttons] - 1
        player_type = self.role

        response = self.game_room_server.make_a_move(location, player_type)
        print(response)


    def checkForWin(self):
        if (self.button1['text'] == 'X' and self.button2['text'] == 'X' and self.button3['text'] == 'X' or
                self.button4['text'] == 'X' and self.button5['text'] == 'X' and self.button6['text'] == 'X' or
                self.button7['text'] == 'X' and self.button8['text'] == 'X' and self.button9['text'] == 'X' or
                self.button1['text'] == 'X' and self.button5['text'] == 'X' and self.button9['text'] == 'X' or
                self.button3['text'] == 'X' and self.button5['text'] == 'X' and self.button7['text'] == 'X' or
                self.button1['text'] == 'X' and self.button2['text'] == 'X' and self.button3['text'] == 'X' or
                self.button1['text'] == 'X' and self.button4['text'] == 'X' and self.button7['text'] == 'X' or
                self.button2['text'] == 'X' and self.button5['text'] == 'X' and self.button8['text'] == 'X' or
                self.button7['text'] == 'X' and self.button6['text'] == 'X' and self.button9['text'] == 'X'):
            self.disableButton()
            messagebox.showinfo("Tic-Tac-Toe", self.player1_name_entry.get())

        elif self.flag == 8:
            tkinter.messagebox.showinfo("Tic-Tac-Toe", "It is a Tie")

        elif (self.button1['text'] == 'O' and self.button2['text'] == 'O' and self.button3['text'] == 'O' or
              self.button4['text'] == 'O' and self.button5['text'] == 'O' and self.button6['text'] == 'O' or
              self.button7['text'] == 'O' and self.button8['text'] == 'O' and self.button9['text'] == 'O' or
              self.button1['text'] == 'O' and self.button5['text'] == 'O' and self.button9['text'] == 'O' or
              self.button3['text'] == 'O' and self.button5['text'] == 'O' and self.button7['text'] == 'O' or
              self.button1['text'] == 'O' and self.button2['text'] == 'O' and self.button3['text'] == 'O' or
              self.button1['text'] == 'O' and self.button4['text'] == 'O' and self.button7['text'] == 'O' or
              self.button2['text'] == 'O' and self.button5['text'] == 'O' and self.button8['text'] == 'O' or
              self.button7['text'] == 'O' and self.button6['text'] == 'O' and self.button9['text'] == 'O'):
            self.disableButton()
            tkinter.messagebox.showinfo("Tic-Tac-Toe", self.player2_name_entry.get())

    def render_list_of_game_rooms(self, rooms):
        self.list_box.delete(0, tkinter.END)
        for room in rooms:
            self.list_box.insert(int(room['created_at']), "Room {}".format(room['id']))

    @Pyro4.expose
    def update_positions(self, request):
        # TODO:
        # for idx, position in enumerate(request):
        #     btn_val = ''
        #     if position == self.TYPE_PLAYER_O:
        #         btn_val = 'O'
        #     elif position == self.TYPE_PLAYER_X:
        #         btn_val = 'X'
        #     print(btn_val)
        # self.button1.config(text="ahaha")
        # return "ok"
        # print(len(self.button_mapping))
            # if btn_val != '':
            #     for button, number in self.button_mapping.items():
            #         print(button)

    @Pyro4.expose
    def update_list_of_game_rooms(self, request):
        print(request)



    def connect_to_server(self, name):
        try:
            uri = "PYRONAME:{}@localhost:1337".format(name)
            return Pyro4.Proxy(uri)
        except CommunicationError as e:
            print(e)


def start_with_ns(gui_server):
    __host = "localhost"
    __port = 1337
    with Pyro4.Daemon(host=__host) as daemon:
        ns = Pyro4.locateNS(__host, __port)
        uri_server = daemon.register(gui_server)
        print("URI gui  server : ", uri_server)
        uri_name = "gui_server_{}".format(gui_server.identifier)
        ns.register(uri_name, uri_server)
        print(uri_name)
        daemon.requestLoop()
    print('\nexited..')

if __name__ == "__main__":

    master = tkinter.Tk()

    app = GameGui(master)
    print(app.identifier)

    t = threading.Thread(target=start_with_ns, args=(app,))
    t.daemon = True
    t.start()

    app.start()


    master.mainloop()
