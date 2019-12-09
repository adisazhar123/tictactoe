import tkinter
from tkinter import StringVar, Label, Entry, Button, DISABLED
import threading
from tkinter import messagebox

import Pyro4
import shortuuid
from Pyro4.errors import CommunicationError, ConnectionClosedError
import os, sys
import time


# class GameGui(threading.Thread):
@Pyro4.expose
class GameGui():
    def __init__(self, master):
        # threading.Thread.__init__(self)
        self.master = master
        self.interval = 1
        self.winner = ''
        self.player_a_name = StringVar()
        self.player_b_name = StringVar()
        self.player_name = StringVar()
        self.type = StringVar()

        self.dark_color = '#000000'
        self.communication_server = self.connect_to_server('communication_server')
        self.game_room_server = None

        self.game_room_server_code = None

        self.flag = 0

        # init types
        self.TYPE_SPECTATOR = 'spectator'
        self.TYPE_PLAYER = 'player'

        self.TYPE_PLAYER_X = 'player:x'
        self.TYPE_PLAYER_O = 'player:o'

        self.turn = None

        self.button_mapping = {}

        self.identifier = shortuuid.uuid()
        self.role = None

        self.button_mapping = {}
        self.turn_label = None

        label = Label(self.master, text="Tic Tac Toe", font='Times 15 bold', fg='#ffffff', bg=self.dark_color)
        label.grid(row=1, column=0, columnspan=8)

        self.buttons = StringVar()
        self.init_list_of_game_rooms()

        # self.init_game_buttons()

    def init_game_positions(self):
        self.positions = [None] * 9

    def init_list_of_game_rooms(self):
        self.dark_background_master()
        self.game_rooms_available_label = Label(self.master, text="Game rooms available", font='Times 15', fg='#ffffff', bg=self.dark_color)
        self.game_rooms_available_label.grid(row=2, column=0)

        self.button_create_game_room = Button(self.master, text="Create game room", font='Times 15 bold', bg='#66B2FF', fg='#ffffff', command=lambda: self.create_game_room_server())
        self.button_create_game_room.grid(row=4, column=0)

        self.list_box = tkinter.Listbox(self.master, font='Times 20', bg='#121212', fg='#FFFFFF')
        self.list_box.grid(row=3, column=0)
        self.list_box.bind('<Double-1>', self.list_box_double_click_handler)

        try:
            rooms_response = self.communication_server.available_rooms_command()
            print(rooms_response)
        except (ConnectionClosedError, CommunicationError) as e:
            print(str(e))
            self.gracefully_exits()
        self.render_list_of_game_rooms(rooms_response['data'])

    def init_player_labels(self):
        label = Label(self.master, text="Player 1:", font='Times 20 bold', bg='white', fg='black', height=1, width=8)
        label.grid(row=1, column=0)

        label = Label(self.master, text="Player 2:", font='Times 20 bold', bg='white', fg='black', height=1, width=8)
        label.grid(row=2, column=0)

        self.player1_name_entry = Entry(self.master, textvariable="wuaa", bd=5)
        self.player1_name_entry.grid(row=1, column=1, columnspan=8)
        self.player2_name_entry = Entry(self.master, textvariable="kaka", bd=5)
        self.player2_name_entry.grid(row=2, column=1, columnspan=8)

    def init_game_screen(self):
        self.room_name.destroy()
        self.label_name.destroy()
        self.name_input.destroy()
        self.button_join_room.destroy()

        self.init_game_buttons()
        self.init_game_positions()

    def init_game_player_labels(self):
        if self.role in [self.TYPE_PLAYER_O, self.TYPE_PLAYER_X]:
            self.name_label_game = Label(self.master, text=self.player_name, font='Times 15', fg='#ffffff', bg=self.dark_color)
            self.name_label_game.grid(row=6, column=1)
            role_game = self.role.replace('player:', '')
            size = '50'
        else:
            role_game = 'SPECTATOR'
            size = '15'
        self.role_label_game = Label(self.master, text=role_game, font='Times {}'.format(size), fg='#ffffff', bg=self.dark_color)
        self.role_label_game.grid(row=7, column=1)

    def init_name_form_screen(self, game_room_server_name):
        self.init_form_layout(game_room_server_name)

    def init_form_player_screen(self, game_room_server_name):
        self.list_box.destroy()
        self.button_create_game_room.destroy()
        self.game_rooms_available_label.destroy()

        # self.connect_to_game_room(game_room_server_name)

    def init_form_layout(self, game_room_server_name):
        self.init_form_player_screen(game_room_server_name)

        self.room_name = Label(self.master, pady=20, text="You are entering room {}".format(game_room_server_name.replace('game_room_server_', '')), font='Times 15', fg='#ffffff', bg=self.dark_color)
        self.room_name.grid(row=2, column=0)

        self.label_name = Label(self.master, text="Enter Your Name", font='Times 12', fg='#ffffff', bg=self.dark_color)
        self.label_name.grid(row=3, column=0)

        self.name_input = Entry(self.master, textvariable="name")
        self.name_input.grid(row=4, column=0, columnspan=8)

        # TODO:
        self.button_join_room = Button(self.master, text="Join Room", font='Times 15 bold', bg='#66B2FF', fg='#ffffff', command=lambda: self.join_room_server(self.name_input.get(), game_room_server_name))
        self.button_join_room.grid(row=5, column=0, pady=20)

        # self.connect_to_game_room(game_room_server_name)

    def join_room_server(self, username, game_room_server_name):
        self.player_name = username
        self.init_game_screen()
        self.connect_to_game_room(game_room_server_name, username)
        self.init_game_player_labels()
        tkinter.messagebox.showinfo("Tic-Tac-Toe", "Welcome {}".format(username))

    def reset_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def back_to_main_menu(self):
        self.reset_widgets()

        self.room_name.destroy()
        self.label_name.destroy()
        self.name_input.destroy()
        self.button_join_room.destroy()

        if self.role in [self.TYPE_PLAYER_O, self.TYPE_PLAYER_X]:
            self.name_label_game.destroy()

        self.role_label_game.destroy()

        self.init_game_positions()
        self.turn = None

        self.role = None

        self.button_mapping = {}

        label = Label(self.master, text="Tic Tac Toe", font='Times 15 bold', fg='#ffffff', bg=self.dark_color)
        label.grid(row=1, column=0, columnspan=8)

        self.init_list_of_game_rooms()

        rooms_response = self.communication_server.available_rooms_command()
        self.render_list_of_game_rooms(rooms_response['data'])

    def init_game_buttons(self):
        self.button1 = Button(self.master, text='', font='Times 20 bold', bg='#343a40', fg='#FFFFFF', height=4, width=8,
                              command=lambda: self.btnClick(self.button1))
        self.button1.grid(row=3, column=0)

        self.button_mapping[self.button1] = 1

        self.button2 = Button(self.master, text='', font='Times 20 bold', bg='#343a40', fg='#FFFFFF', height=4, width=8,
                              command=lambda: self.btnClick(self.button2))
        self.button2.grid(row=3, column=1)

        self.button_mapping[self.button2] = 2

        self.button3 = Button(self.master, text='', font='Times 20 bold', bg='#343a40', fg='#FFFFFF', height=4, width=8,
                              command=lambda: self.btnClick(self.button3))
        self.button3.grid(row=3, column=2)

        self.button_mapping[self.button3] = 3

        self.button4 = Button(self.master, text='', font='Times 20 bold', bg='#343a40', fg='#FFFFFF', height=4, width=8,
                              command=lambda: self.btnClick(self.button4))
        self.button4.grid(row=4, column=0)

        self.button_mapping[self.button4] = 4

        self.button5 = Button(self.master, text='', font='Times 20 bold', bg='#343a40', fg='#FFFFFF', height=4, width=8,
                              command=lambda: self.btnClick(self.button5))
        self.button5.grid(row=4, column=1)

        self.button_mapping[self.button5] = 5

        self.button6 = Button(self.master, text='', font='Times 20 bold', bg='#343a40', fg='#FFFFFF', height=4, width=8,
                              command=lambda: self.btnClick(self.button6))
        self.button6.grid(row=4, column=2)

        self.button_mapping[self.button6] = 6

        self.button7 = Button(self.master, text='', font='Times 20 bold', bg='#343a40', fg='#FFFFFF', height=4, width=8,
                              command=lambda: self.btnClick(self.button7))
        self.button7.grid(row=5, column=0)

        self.button_mapping[self.button7] = 7

        self.button8 = Button(self.master, text='', font='Times 20 bold', bg='#343a40', fg='#FFFFFF', height=4, width=8,
                              command=lambda: self.btnClick(self.button8))
        self.button8.grid(row=5, column=1)

        self.button_mapping[self.button8] = 8

        self.button9 = Button(self.master, text='', font='Times 20 bold', bg='#343a40', fg='#FFFFFF', height=4, width=8,
                              command=lambda: self.btnClick(self.button9))
        self.button9.grid(row=5, column=2)

        self.button_mapping[self.button9] = 9

        self.turn_label_game = Label(self.master, text='', font='Times 15', fg='#ffffff', bg=self.dark_color)
        self.turn_label_game.grid(row=8, column=1)

        self.turn_label = self.turn_label_game

    def create_game_room_server(self):
        response = self.communication_server.create_room_command(self.identifier)
        rooms_response = self.communication_server.available_rooms_command()
        self.render_list_of_game_rooms(rooms_response['data'])

        if response['status'] == 'ok':
            tkinter.messagebox.showinfo("Tic-Tac-Toe", response['message'])

    def dark_background_master(self):
        self.master.configure(background = self.dark_color)

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
        self.game_room_server_code = code
        game_room_server_name = "game_room_server_{}".format(code)
        self.init_form_layout(game_room_server_name)
        # self.init_form_player_screen(game_room_server_name)

    # TODO:
    def connect_to_game_room(self, game_room_server_name, username):
        self.game_room_server = self.connect_to_server(game_room_server_name)
        response = self.game_room_server.connect({'identifier': self.identifier}, self.TYPE_PLAYER, username)

        print(response)

        if response['status'] == 'ok':
            self.role = response['data']['participant_type']
            self.positions = response['data']['positions']
            self.turn = response['data']['turn']

            self.init_game_screen()

            self.game_room_server.update_positions()

            tkinter.messagebox.showinfo("Tic-Tac-Toe", response['message'])

    def btnClick(self, buttons):
        if buttons["text"] != '':
            tkinter.messagebox.showinfo("Tic-Tac-Toe", "Button already Clicked!")
        elif self.role != self.turn:
            if self.role in [self.TYPE_PLAYER_O, self.TYPE_PLAYER_X]:
                msg = 'Not your turn'
            else:
                msg = 'You are spectator'
            tkinter.messagebox.showinfo("Tic-Tac-Toe", msg)
        else:
            location = self.button_mapping[buttons] - 1
            player_type = self.role

            try:
                response = self.game_room_server.make_a_move(location, player_type)
            except Exception as e:
                print("le error", e)
                self.game_room_server = None
                self.game_room_server = self.connect_to_server("game_room_server_{}".format(self.game_room_server_code))
                response = self.game_room_server.make_a_move(location, player_type)

            self.turn = response['data']['turn']
            if response['data']['winner'] is not None:
                self.winner = response['data']['winner']
                # self.game_room_server.announce_winner(self.winner)
            print(response)

    def render_list_of_game_rooms(self, rooms):
        self.list_box.delete(0, tkinter.END)
        for room in rooms:
            self.list_box.insert(int(room['created_at']), "Room {}".format(room['id']))

    def change_button_label(self, button, val, turn):
        button['text'] = val
        self.turn = turn

    def change_turn_label(self):
        if self.role == self.turn:
            self.turn_label['text'] = 'Your Turn'
        else:
            self.turn_label['text'] = self.turn + ' turn'

    def gracefully_exits(self):
        print("disconnecting..")
        time.sleep(0.5)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit()

    def communicate(self) -> bool:
        try:
            res = self.communication_server.check_connection()
            if res == 'ok':
                pass
        except:
            return False
        return True

    def job_ping_server_ping_ack(self) -> threading.Thread:
        t = threading.Thread(target=self.ping_server)
        t.start()
        return t

    def ping_server(self):
        while True:
            alive = self.communicate()
            if not alive:
                alive = self.communicate()
                if not alive:
                    print("\ncommunication server is down [DETECT BY ping ack]\n")
                    break
            time.sleep(self.interval)
        self.gracefully_exits()

    def __dialog_box_popup(self, msg):
        res = tkinter.messagebox.showinfo("Tic-Tac-Toe", msg)
        if res == 'ok':
            threading.Thread(target=self.back_to_main_menu, daemon=True).start()

    def all_children(self, window):
        _list = window.winfo_children()

        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())

        return _list

    @Pyro4.expose
    def get_the_winner(self, winner):
        print('winner:{}'.format(winner))
        if self.role not in [self.TYPE_PLAYER_O, self.TYPE_PLAYER_X]:
            msg = 'Player {} Win'.format(winner.replace('player:', ''))            
        if winner == 'tie':
            msg = 'Tie'
        elif winner == self.role:
            msg = 'You Win'
        else:
            msg = 'You Lose'

        threading.Thread(target=self.__dialog_box_popup, args=(msg,), daemon=True).start()

    @Pyro4.expose
    def update_positions(self, request, turn):
        threading.Thread(target=self._update_positions, args=(request, turn,), daemon=True).start()

    def _update_positions(self, request, turn):
        print('starting')
        for idx, position in enumerate(request):
            btn_val = ''
            if position == self.TYPE_PLAYER_O:
                btn_val = 'O'
            elif position == self.TYPE_PLAYER_X:
                btn_val = 'X'
            if btn_val != '':
                for button, number in self.button_mapping.items():
                    if number == (idx + 1):
                        threading.Thread(target=self.change_button_label, args=(button, btn_val, turn),
                                         daemon=True).start()
        self.turn = turn
        threading.Thread(target=self.change_turn_label, daemon=True).start()
        print('done updating positions')

    @Pyro4.expose
    def update_list_of_game_rooms(self, request):
        self.render_list_of_game_rooms(request['data'])

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
    try:
        t = threading.Thread(target=start_with_ns, args=(app,))
        t.daemon = True
        t.start()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
    except:
        print('failed to start gui client server')
        sys.exit(0)

    try:
        app.interval = app.communication_server.ping_interval()
        res = app.communication_server.register_command(app.identifier)
        app.communication_server._pyroTimeout = app.interval
        print(res)
        tpa = app.job_ping_server_ping_ack()
    except:
        print('failed to connect with communication server')
        sys.exit(0)

    print(app.identifier)

    # app.start()

    master.mainloop()
