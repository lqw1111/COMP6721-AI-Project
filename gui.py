
from tkinter import Tk, Button, PhotoImage, Frame, X, BOTTOM, Y, Checkbutton, TOP, LEFT, OUTSIDE, StringVar, CENTER, \
    DISABLED
from tkinter.font import Font
from tkinter.ttk import Label
from tkinter import messagebox

element_map = {'EMPTY_TYPE':0 , 'RED_SOLID':1, 'WHITE_HOLLOW':2, 'RED_HOLLOW':3, 'WHITE_SOLID': 4}
col_map = {'A':1,'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}

class CardElement(object):

    # final variables describe the type of the cards
    EMPTY_TYPE   = 0
    RED_SOLID    = 1
    WHITE_HOLLOW = 2
    RED_HOLLOW   = 3
    WHITE_SOLID  = 4

    def __init__(self, elementType):
        self.type = elementType
        self.neighbour = None
        self.neighbour_position = None
        self.card_type = None

    def set_empty(self):
        self.type = 0
        self.neighbour = None
        self.neighbour_position = None
        self.card_type = None

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

    def set_neighbour_position(self, neighbour_position):
        self.neighbour_position = neighbour_position

    def get_neighbour_position(self):
        return self.neighbour_position

    def set_neighbour(self, neighbour):
        self.neighbour = neighbour

    def get_neighbour(self):
        return self.neighbour

    def set_card_type(self, card_type):
        self.card_type = card_type

    def get_card_type(self):
        return self.card_type


class Board:

    def __init__(self):
        self.col_header = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.row_header = [x for x in range(1, 13)]
        self.cols = len(self.col_header)
        self.rows = len(self.row_header)
        self.pos = (-1, -1)
        self.content = {}

    def create_data_entry(self, row, col):
        row = row + 1
        col = self.col_header[col - 1]
        # print('create cell: {}, {}'.format(row, col))
        data_cell = CardElement(CardElement.EMPTY_TYPE)
        self.content[row, col] = data_cell

    def get_data_entry(self, point):
        return self.content[point[0], point[1]]

    
# selection_btn = [
#     'UNDEFINED',
#     'RED_SOLID_WHITE_HOLLOW_H',
#     'RED_SOLID_WHITE_HOLLOW_V',
#     'WHITE_HOLLOW_RED_SOLID_H',
#     'WHITE_HOLLOW_RED_SOLID_V',
#     'RED_HOLLOW_WHITE_SOLID_H',
#     'RED_HOLLOW_WHITE_SOLID_V',
#     'WHITE_SOLID_RED_HOLLOW_H',
#     'WHITE_SOLID_RED_HOLLOW_V',
# ]
selection_btn = [
    'UNDEFINED',
    'RED_SOLID_WHITE_HOLLOW_H',
    'WHITE_HOLLOW_RED_SOLID_V',
    'WHITE_HOLLOW_RED_SOLID_H',
    'RED_SOLID_WHITE_HOLLOW_V',
    'RED_HOLLOW_WHITE_SOLID_H',
    'WHITE_SOLID_RED_HOLLOW_V',
    'WHITE_SOLID_RED_HOLLOW_H',
    'RED_HOLLOW_WHITE_SOLID_V',
]

def get_component_icon(selection):
    prefix = 'img/part'
    suffix  = '.png'
    if selection == 'RED_SOLID_WHITE_HOLLOW_H' or selection == 'RED_SOLID_WHITE_HOLLOW_V':
        id1 = 1
        id2 = 2
    elif selection == 'WHITE_HOLLOW_RED_SOLID_H' or selection == 'WHITE_HOLLOW_RED_SOLID_V':
        id1 = 2
        id2 = 1
    elif selection == 'RED_HOLLOW_WHITE_SOLID_H' or selection == 'RED_HOLLOW_WHITE_SOLID_V':
        id1 = 3
        id2 = 4
    elif selection == 'WHITE_SOLID_RED_HOLLOW_H' or selection == 'WHITE_SOLID_RED_HOLLOW_V':
        id1 = 4
        id2 = 3
    key1 = prefix + str(id1) + suffix
    key2 = prefix + str(id2) + suffix
    return key1, key2

class GUI:

    def __init__(self):
        # set GUI
        self.app = Tk()
        self.app.title('Double Card')
        self.app.geometry('800x800')
        self.app.resizable(width=False, height=False)
        self.font = Font(family="Helvetica", size=16)

        self.board = Board()

        self.icons = self.prepare_icon()

        self.boardFrame = Frame(self.app)
        self.boardFrame.pack()
        self.selectionFrame = Frame(self.app)
        self.selectionFrame.pack(side=BOTTOM)

        self.data_btn = {}
        self.slt_btn = []
        self.cur_selection = 'UNDEFINED'

        # game controller
        self.card_remain = 24
        self.cur_player = 1
        self.step = 0
        self.mode = 'M'
        self.last_move_card = None


        # build the board with header
        btn = Button(self.boardFrame, image=self.icons['img/empty.png'])
        btn.grid(row=0,column=0)

        self.var = StringVar()
        self.var.set("    Player1 Turn")
        label = Label(self.app, textvariable = self.var, compound = CENTER)
        label.place(x=20, y=100, height=100, width=120)

        test_func = lambda : self.test_function()
        test_button = Button(self.app, command = test_func, text = 'TEST')
        test_button.place(x=20, y=200, height=100, width=120)

        for r in range(0, self.board.rows + 1):
            for c in range(0, self.board.cols + 1):
                if r == self.board.rows and c == 0:
                    continue
                elif r == self.board.rows or c == 0:
                    # create header cells GUI
                    file_name = ''
                    if r == self.board.rows:
                        file_name = 'img/letter' + str(c) + '.png'
                    else:
                        file_name = 'img/num' + str(self.board.rows - r) + '.png'
                    btn = Button(self.boardFrame, image=self.icons[file_name])
                    btn.grid(row=r,column=c)
                else:
                    # create data cells GUI and connect the GUI to the data
                    handler = lambda row=self.board.rows - r, col=c: self.board_btn_clicked(row, col)
                    btn = Button(self.boardFrame, image=self.icons['img/empty.png'], command=handler)
                    btn.grid(row=r,column=c)
                    self.board.create_data_entry(r, c)
                    self.data_btn[self.board.rows - r, self.board.col_header[c - 1]] = btn

        # build the selection panel
        for idx in range(1, 9):
            idx_ = idx - 1
            file_name = 'img/face' + str(idx) + '.png'
            handler = lambda selection = idx: self.select_btn_clicked(selection)
            btn = Checkbutton(self.selectionFrame, image=self.icons[file_name],
                              indicatoron=0, command=handler, padx=8, pady=8)
            btn.grid(row=0, column=idx_)
            self.slt_btn.append(btn)

    def board_btn_clicked(self, row, col):
        if (self.card_remain > 0):
            # todo:add card step
            print('-------------------------------')
            print('button clicked: {}, {}'.format(row, self.board.col_header[col - 1]))
            if self.cur_selection == 'UNDEFINED':
                # do nothing if current state is undefined
                pass
            else:
                direction = self.cur_selection[-1]

                if (direction == 'H' and 1 <= row <= self.board.rows and 1 <= col <= self.board.cols - 1):
                    point1 = tuple((row, self.board.col_header[col - 1]))
                    point2 = tuple((row, self.board.col_header[col]))
                # elif (direction == 'V' and 2 <= row <= self.board.rows and 1 <= col <= self.board.rows):
                elif (direction == 'V' and 1 <= row <= self.board.rows - 1 and 1 <= col <= self.board.rows):
                    point1 = tuple((row, self.board.col_header[col - 1]))
                    # point2 = tuple((row - 1, self.board.col_header[col - 1]))
                    point2 = tuple((row + 1, self.board.col_header[col - 1]))
                else:
                    print('out of the board')
                    return

                key1, key2 = get_component_icon(self.cur_selection)

                # todo:check entry status
                if (self.is_valid_step(row, col, point1, point2)):
                    # update UI
                    # print(self.board.content[1,'A'].type)
                    entry1_btn = self.data_btn[point1[0], point1[1]]
                    entry1_btn.config(image=self.icons[key1])
                    entry2_btn = self.data_btn[point2[0], point2[1]]
                    entry2_btn.config(image=self.icons[key2])

                    # todo: upate the data status
                    # 1. update board content
                    # 2. bind two element, using cur_selection, we know the shape of cube
                    #    when we choice the place the postion, we can bind two element
                    #    In the element, we need a attribution to record the neighbourhood
                    entry1 = self.board.get_data_entry(point1)
                    entry2 = self.board.get_data_entry(point2)
                    str = self.cur_selection.split('_')
                    entry1.set_type(element_map[str[0] + '_' + str[1]])
                    entry2.set_type(element_map[str[2] + '_' + str[3]])

                    self.config_element(entry1, entry2, point1, point2, self.cur_selection)

                    # check winner
                    # print("Check WINNER: ", self.check_winner(point1, point2))
                    self.announce_winner(self.check_winner(point1, point2))

                    # config the parameter
                    self.card_remain = self.card_remain - 1
                    self.step = self.step + 1
                    self.player = self.step % 2
                    self.last_move_card = tuple((point1, point2))

                    if self.player == 0:
                        self.var.set("   Player1 Turn")
                    elif self.player == 1:
                        self.var.set("   Player2 Turn")

                    if (self.mode == 'AI'):
                        # todo: add AI algorithm
                        # calculate the step
                        # update the GUI
                        # check winner
                        # step + 1
                        # self.play = self.step % 2
                        pass

                    print('SUCCESS!!')
                else:
                    print("The Step is not Valid!!!")

        else:
            print("remove card step")
            print('remove card position:', row , col)
            # todo: remove card step
            # remove card
            # update the GUI
            # remind_card + 1
            # cur_player = cur_player
            point1 = tuple((row, self.board.col_header[col - 1]))
            print(point1)
            selecte_element1 = self.board.get_data_entry(point1)
            selecte_element2 = selecte_element1.get_neighbour()
            point2 = selecte_element1.get_neighbour_position()

            # test
            print('point1 ',point1, ' point2 ', point2)
            print('element1 ',selecte_element1,'element2 ',selecte_element2)

            if self.is_valid_remove_step(point1, point2):

                # update the UI
                element_btn1 = self.data_btn[point1[0], point1[1]]
                element_btn1.config(image=self.icons['img/empty.png'])
                element_btn2 = self.data_btn[point2[0], point2[1]]
                element_btn2.config(image=self.icons['img/empty.png'])

                # self.disable_eight_btn()

                # config the data
                self.cur_selection = selecte_element1.get_card_type()
                self.card_remain = self.card_remain + 1

                selecte_element1.set_empty()
                selecte_element2.set_empty()
            else:
                print('You Can not Choice the block!!!')

    def test_function(self):
        # self.cur_selection = 'RED_SOLID_WHITE_HOLLOW_H'
        # self.board_btn_clicked(1,1)
        i = 1
        f = open('test.txt', 'r')
        for line in f.readlines():
            cmd = line.strip()
            command = cmd.split(' ')
            # print(selection_btn[int(command[1])])

            self.cur_selection = selection_btn[int(command[1])]
            self.board_btn_clicked(int(command[3]), col_map[command[2]])

        f.close()


    def announce_winner(self, winner):
        if winner[0] and winner[1]:
            if self.cur_player == 0:
                messagebox.showinfo("WINNER",'Player ONE Win')
            else :
                messagebox.showinfo("WINNER",'Player TWO Win')
        if winner[0] and not winner[1]:
            messagebox.showinfo("WINNER","Color Win!!")
        elif not winner[0] and winner[1] :
            messagebox.showinfo("WINNER","Dots Win!!")



    def is_valid_remove_step(self, point1, point2):
        # two point is not none
        # the card is not just move by the last player
        # if is H, there is no element on the two point
        # if is V, there is no element on the upper element
        print('last move card',self.last_move_card)
        entry1 = self.board.get_data_entry(point1)

        if self.board.get_data_entry(point1).get_type() == 0 or self.board.get_data_entry(point2).get_type() == 0 :
            return False
        if self.last_move_card == tuple((point1, point2)) or self.last_move_card == tuple((point2, point1)):
            return False
        if entry1.get_card_type()[-1] == 'H' and (self.board.get_data_entry(tuple((point1[0] + 1 , point1[1]))).get_type() != 0 or self.board.get_data_entry(tuple((point2[0] + 1 , point2[1]))).get_type() != 0):
            return False
        elif entry1.get_card_type()[-1] == 'V':
            if point1[0] > point2[0]:
                judge_point = tuple((point1[0] + 1 , point1[1]))
            else:
                judge_point = tuple((point2[0] + 1 , point2[1]))

            if self.board.get_data_entry(judge_point).get_type() != 0:
                return False

        return True

    def disable_eight_btn(self):
        for i in range(len(self.slt_btn)):
            btn = self.slt_btn[i]
            btn.config(state=DISABLED)
            btn.update()

    def config_element(self, element1, element2, point1, point2, cur_selection):
        print('point1 point2:', point1, point2)
        element1.set_neighbour(element2)
        element2.set_neighbour(element1)
        element1.set_neighbour_position(point2)
        element2.set_neighbour_position(point1)
        element1.set_card_type(cur_selection)
        element2.set_card_type(cur_selection)


    def check_winner(self, point1, point2):
        Color_Win = False
        Dots_Win = False

        # scan the point1 horizontal
        for i in range(self.board.cols - 3):
            scan_point1 = self.board.get_data_entry(tuple((point1[0], self.board.col_header[i]))).get_type()
            scan_point2 = self.board.get_data_entry(tuple((point1[0], self.board.col_header[i + 1]))).get_type()
            scan_point3 = self.board.get_data_entry(tuple((point1[0], self.board.col_header[i + 2]))).get_type()
            scan_point4 = self.board.get_data_entry(tuple((point1[0], self.board.col_header[i + 3]))).get_type()
            if ((scan_point1 == 1 or scan_point1 == 3) and (scan_point2 == 1 or scan_point2 == 3) and (scan_point3 == 1 or scan_point3 == 3) and (scan_point4 == 1 or scan_point4 == 3)) or ((scan_point1 == 2 or scan_point1 == 4) and (scan_point2 == 2 or scan_point2 == 4) and (scan_point3 == 2 or scan_point3 == 4) and (scan_point4 == 2 or scan_point4 == 4)):
                Color_Win = True
            if ((scan_point1 == 1 or scan_point1 == 4) and (scan_point2 == 1 or scan_point2 == 4) and (scan_point3 == 1 or scan_point3 == 4) and (scan_point4 == 1 or scan_point4 == 4)) or ((scan_point1 == 2 or scan_point1 == 3) and (scan_point2 == 2 or scan_point2 == 3) and (scan_point3 == 2 or scan_point3 == 3) and (scan_point4 == 2 or scan_point4 == 3)):
                Dots_Win = True

        # scan the point1 vertical
        for i in range(1, self.board.rows - 2):
            # print(i)
            scan_point1 = self.board.get_data_entry(tuple((i, point1[1]))).get_type()
            scan_point2 = self.board.get_data_entry(tuple((i + 1, point1[1]))).get_type()
            scan_point3 = self.board.get_data_entry(tuple((i + 2, point1[1]))).get_type()
            scan_point4 = self.board.get_data_entry(tuple((i + 3, point1[1]))).get_type()
            if ((scan_point1 == 1 or scan_point1 == 3) and (scan_point2 == 1 or scan_point2 == 3) and (scan_point3 == 1 or scan_point3 == 3) and (scan_point4 == 1 or scan_point4 == 3)) or ((scan_point1 == 2 or scan_point1 == 4) and (scan_point2 == 2 or scan_point2 == 4) and (scan_point3 == 2 or scan_point3 == 4) and (scan_point4 == 2 or scan_point4 == 4)):
                Color_Win = True
            if ((scan_point1 == 1 or scan_point1 == 4) and (scan_point2 == 1 or scan_point2 == 4) and (scan_point3 == 1 or scan_point3 == 4) and (scan_point4 == 1 or scan_point4 == 4)) or ((scan_point1 == 2 or scan_point1 == 3) and (scan_point2 == 2 or scan_point2 == 3) and (scan_point3 == 2 or scan_point3 == 3) and (scan_point4 == 2 or scan_point4 == 3)):
                Dots_Win = True

        # scan the point2 horizontal
        for i in range(self.board.cols - 3):
            scan_point1 = self.board.get_data_entry(tuple((point2[0], self.board.col_header[i]))).get_type()
            scan_point2 = self.board.get_data_entry(tuple((point2[0], self.board.col_header[i + 1]))).get_type()
            scan_point3 = self.board.get_data_entry(tuple((point2[0], self.board.col_header[i + 2]))).get_type()
            scan_point4 = self.board.get_data_entry(tuple((point2[0], self.board.col_header[i + 3]))).get_type()
            if ((scan_point1 == 1 or scan_point1 == 3) and (scan_point2 == 1 or scan_point2 == 3) and (
                    scan_point3 == 1 or scan_point3 == 3) and (scan_point4 == 1 or scan_point4 == 3)) or (
                    (scan_point1 == 2 or scan_point1 == 4) and (scan_point2 == 2 or scan_point2 == 4) and (
                    scan_point3 == 2 or scan_point3 == 4) and (scan_point4 == 2 or scan_point4 == 4)):
                Color_Win = True
            if ((scan_point1 == 1 or scan_point1 == 4) and (scan_point2 == 1 or scan_point2 == 4) and (
                    scan_point3 == 1 or scan_point3 == 4) and (scan_point4 == 1 or scan_point4 == 4)) or (
                    (scan_point1 == 2 or scan_point1 == 3) and (scan_point2 == 2 or scan_point2 == 3) and (
                    scan_point3 == 2 or scan_point3 == 3) and (scan_point4 == 2 or scan_point4 == 3)):
                Dots_Win = True

        # scan the point1 vertical
        for i in range(1, self.board.rows - 2):
            # print(i)
            scan_point1 = self.board.get_data_entry(tuple((i, point2[1]))).get_type()
            scan_point2 = self.board.get_data_entry(tuple((i + 1, point2[1]))).get_type()
            scan_point3 = self.board.get_data_entry(tuple((i + 2, point2[1]))).get_type()
            scan_point4 = self.board.get_data_entry(tuple((i + 3, point2[1]))).get_type()
            if ((scan_point1 == 1 or scan_point1 == 3) and (scan_point2 == 1 or scan_point2 == 3) and (
                    scan_point3 == 1 or scan_point3 == 3) and (scan_point4 == 1 or scan_point4 == 3)) or (
                    (scan_point1 == 2 or scan_point1 == 4) and (scan_point2 == 2 or scan_point2 == 4) and (
                    scan_point3 == 2 or scan_point3 == 4) and (scan_point4 == 2 or scan_point4 == 4)):
                Color_Win = True
            if ((scan_point1 == 1 or scan_point1 == 4) and (scan_point2 == 1 or scan_point2 == 4) and (
                    scan_point3 == 1 or scan_point3 == 4) and (scan_point4 == 1 or scan_point4 == 4)) or (
                    (scan_point1 == 2 or scan_point1 == 3) and (scan_point2 == 2 or scan_point2 == 3) and (
                    scan_point3 == 2 or scan_point3 == 3) and (scan_point4 == 2 or scan_point4 == 3)):
                Dots_Win = True


        # Check positively sloped diaganols
        for r in range(1, self.board.rows - 2):
            for c in range(self.board.cols - 3):
                # print(tuple(((r,self.board.col_header[c]))))
                scan_point1 = self.board.get_data_entry(tuple((r, self.board.col_header[c]))).get_type()
                scan_point2 = self.board.get_data_entry(tuple((r + 1, self.board.col_header[c + 1]))).get_type()
                scan_point3 = self.board.get_data_entry(tuple((r + 2, self.board.col_header[c + 2]))).get_type()
                scan_point4 = self.board.get_data_entry(tuple((r + 3, self.board.col_header[c + 3]))).get_type()
                # print(tuple((scan_point1,scan_point2,scan_point3,scan_point4)))
                if ((scan_point1 == 1 or scan_point1 == 3) and (scan_point2 == 1 or scan_point2 == 3) and (
                        scan_point3 == 1 or scan_point3 == 3) and (scan_point4 == 1 or scan_point4 == 3)) or (
                        (scan_point1 == 2 or scan_point1 == 4) and (scan_point2 == 2 or scan_point2 == 4) and (
                        scan_point3 == 2 or scan_point3 == 4) and (scan_point4 == 2 or scan_point4 == 4)):
                    Color_Win = True
                if ((scan_point1 == 1 or scan_point1 == 4) and (scan_point2 == 1 or scan_point2 == 4) and (
                        scan_point3 == 1 or scan_point3 == 4) and (scan_point4 == 1 or scan_point4 == 4)) or (
                        (scan_point1 == 2 or scan_point1 == 3) and (scan_point2 == 2 or scan_point2 == 3) and (
                        scan_point3 == 2 or scan_point3 == 3) and (scan_point4 == 2 or scan_point4 == 3)):
                    Dots_Win = True


        # Check negatively sloped diaganols
        for r in range(4,self.board.rows + 1):
            for c in range(self.board.cols - 3):
                # print(tuple((r, self.board.col_header[c])))
                scan_point1 = self.board.get_data_entry(tuple((r, self.board.col_header[c]))).get_type()
                scan_point2 = self.board.get_data_entry(tuple((r - 1, self.board.col_header[c + 1]))).get_type()
                scan_point3 = self.board.get_data_entry(tuple((r - 2, self.board.col_header[c + 2]))).get_type()
                scan_point4 = self.board.get_data_entry(tuple((r - 3, self.board.col_header[c + 3]))).get_type()
                if ((scan_point1 == 1 or scan_point1 == 3) and (scan_point2 == 1 or scan_point2 == 3) and (
                        scan_point3 == 1 or scan_point3 == 3) and (scan_point4 == 1 or scan_point4 == 3)) or (
                        (scan_point1 == 2 or scan_point1 == 4) and (scan_point2 == 2 or scan_point2 == 4) and (
                        scan_point3 == 2 or scan_point3 == 4) and (scan_point4 == 2 or scan_point4 == 4)):
                    Color_Win = True
                if ((scan_point1 == 1 or scan_point1 == 4) and (scan_point2 == 1 or scan_point2 == 4) and (
                        scan_point3 == 1 or scan_point3 == 4) and (scan_point4 == 1 or scan_point4 == 4)) or (
                        (scan_point1 == 2 or scan_point1 == 3) and (scan_point2 == 2 or scan_point2 == 3) and (
                        scan_point3 == 2 or scan_point3 == 3) and (scan_point4 == 2 or scan_point4 == 3)):
                    Dots_Win = True

        return tuple((Color_Win,Dots_Win))


    def is_valid_step(self, row, col, point1, point2):
        print("check is valid step")
        entry1 = self.board.get_data_entry(point1)
        entry2 = self.board.get_data_entry(point2)
        if (entry1.get_type() != 0 or entry2.get_type() != 0): return False

        if (self.cur_selection[-1] == 'H'):
            if (point1[0] == 1 and point2[0] == 1):
                return True
            elif(self.board.get_data_entry(tuple((point1[0] - 1, point1[1]))).get_type() != 0 and self.board.get_data_entry(tuple((point2[0] - 1, point2[1]))).get_type() != 0):
                return True
            else:
                return False

        elif (self.cur_selection[-1] == 'V'):
            if (point1[0] == 1):
                return True
            elif (point1[0] - 1 > 0 and self.board.get_data_entry(tuple((point1[0] - 1,point1[1]))).get_type() != 0):
                return True
            else:
                return False

        else:
            return False


    def select_btn_clicked(self, selection):
        # unselect the current button
        if self.cur_selection == selection_btn[selection]:
            self.cur_selection = selection_btn[selection]
            print('unselect: {}'.format(self.cur_selection))
        # put focus on the current selection button
        else:
            for b in self.slt_btn:
                b.deselect()
            self.slt_btn[selection - 1].select()
            self.cur_selection = selection_btn[selection]
            print('select: {}'.format(self.cur_selection))
            

    def prepare_icon(self):
        icons = {}

        # read empty cell icon
        file_name = 'img/empty.png'
        icons[file_name] = PhotoImage(file=file_name)

        # read 4 parts icon
        for idx in range(1, 5):
            file_name = 'img/part' + str(idx) + '.png'
            icons[file_name] = PhotoImage(file=file_name)
        
        # read 8 faces icon
        for idx in range(1, 9):
            file_name = 'img/face' + str(idx) + '.png'
            icons[file_name] = PhotoImage(file=file_name)
        
        # read header icon
        for idx in range(1, self.board.rows + 1):
            file_name = 'img/num' + str(idx) + '.png'
            icons[file_name] = PhotoImage(file=file_name)
        for idx in range(1, self.board.cols + 1):
            file_name = 'img/letter' + str(idx) + '.png'
            icons[file_name] = PhotoImage(file=file_name)
        
        return icons

    def mainloop(self):
        self.app.mainloop()


if __name__ == '__main__':
    GUI().mainloop()
