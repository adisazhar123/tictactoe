import tkinter
from tkinter import *
import threading
from tkinter import messagebox


class GameGui(threading.Thread):
    def __init__(self, master):
        threading.Thread.__init__(self)
        self.master = master

        self.player_a_name = StringVar()
        self.player_b_name = StringVar()

        self.player1_name_entry = Entry(self.master, textvariable=self.player_a_name, bd=5)
        self.player1_name_entry.grid(row=1, column=1, columnspan=8)
        self.player2_name_entry = Entry(self.master, textvariable=self.player_b_name, bd=5)
        self.player2_name_entry.grid(row=2, column=1, columnspan=8)

        self.b_click = True
        self.flag = 0

        self.buttons = StringVar()

        label = Label(self.master, text="Player 1:", font='Times 20 bold', bg='white', fg='black', height=1, width=8)
        label.grid(row=1, column=0)

        label = Label(self.master, text="Player 2:", font='Times 20 bold', bg='white', fg='black', height=1, width=8)
        label.grid(row=2, column=0)

        self.button1 = Button(self.master, text=" ", font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                         command=lambda: self.btnClick(self.button1))
        self.button1.grid(row=3, column=0)

        self.button2 = Button(self.master, text=' ', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                         command=lambda: self.btnClick(self.button2))
        self.button2.grid(row=3, column=1)

        self.button3 = Button(self.master, text=' ', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                         command=lambda: self.btnClick(self.button3))
        self.button3.grid(row=3, column=2)

        self.button4 = Button(self.master, text=' ', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                         command=lambda: self.btnClick(self.button4))
        self.button4.grid(row=4, column=0)

        self.button5 = Button(self.master, text=' ', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                         command=lambda: self.btnClick(self.button5))
        self.button5.grid(row=4, column=1)

        self.button6 = Button(self.master, text=' ', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                         command=lambda: self.btnClick(self.button6))
        self.button6.grid(row=4, column=2)

        self.button7 = Button(self.master, text=' ', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                         command=lambda: self.btnClick(self.button7))
        self.button7.grid(row=5, column=0)

        self.button8 = Button(self.master, text=' ', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                         command=lambda: self.btnClick(self.button8))
        self.button8.grid(row=5, column=1)

        self.button9 = Button(self.master, text=' ', font='Times 20 bold', bg='gray', fg='white', height=4, width=8,
                         command=lambda: self.btnClick(self.button9))
        self.button9.grid(row=5, column=2)

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

    def btnClick(self, buttons):
        if buttons["text"] == " " and self.b_click == True:
            buttons["text"] = "X"
            self.b_click = False
            pa = self.player1_name_entry.get() + " Wins!"
            self.checkForWin()
            self.flag += 1

        elif buttons["text"] == " " and self.b_click == False:
            buttons["text"] = "O"
            self.b_click = True
            self.checkForWin()
            self.flag += 1
        else:
            tkinter.messagebox.showinfo("Tic-Tac-Toe", "Button already Clicked!")

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


master = tkinter.Tk()
app = GameGui(master).start()

master.mainloop()
