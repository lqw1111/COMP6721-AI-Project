import copy
import datetime
import time
from datetime import date
from sys import maxsize
from tkinter import Tk, Button, PhotoImage, Frame, X, BOTTOM, Y, Checkbutton, StringVar, CENTER, \
    DISABLED
from tkinter.font import Font
from tkinter.ttk import Label
from tkinter import messagebox
import numpy as np

element_map = {'EMPTY_TYPE':0 , 'RED_SOLID':1, 'WHITE_HOLLOW':2, 'RED_HOLLOW':3, 'WHITE_SOLID': 4}
col_map = {'A':1,'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}
col_0_7 = {'A':0,'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7}

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

selection_map = {'RED_SOLID_WHITE_HOLLOW_H': 1 ,
                 'WHITE_HOLLOW_RED_SOLID_V': 2 ,
                 'WHITE_HOLLOW_RED_SOLID_H': 3 ,
                 'RED_SOLID_WHITE_HOLLOW_V': 4 ,
                 'RED_HOLLOW_WHITE_SOLID_H': 5 ,
                 'WHITE_SOLID_RED_HOLLOW_V': 6 ,
                 'WHITE_SOLID_RED_HOLLOW_H': 7 ,
                 'RED_HOLLOW_WHITE_SOLID_V': 8}

class Node(object):
    def __init__(self, board, card_remain, depth, last_move_card, node_type, selection_card_type, moveable_set,removable_set,recycling = False ,remove_card_position = None, remove_card_type = None ):
        self.board = board                                                                              # board
        self.card_remain = card_remain                                                                  # int
        self.depth = depth                                                                              # int
        self.last_move_card = last_move_card                                                            # (1,'A')
        self.move_card = last_move_card                                                                 # use for record the move step eg. (1,'A')
        self.node_type = node_type                                                                      # 'MAX' or 'MIN'
        self.i_value = -maxsize if self.node_type == 'MAX' else maxsize                                 # int
        self.selection_card_type = selection_card_type                                                  # 'RED_SOLID_WHITE_HOLLOW_H'
        self.moveable_set = moveable_set                                                                # {(1,0),(1,1)} -> {(1,'A'),(1,'B')}
        self.removable_set = removable_set                                                              # {(1,0),(1,1)} -> {(1,'A'),(1,'B')}
        self.recycling = recycling                                                                      # boolean
        self.remove_card_position = remove_card_position                                                # (1,'A')
        self.remove_card_type = remove_card_type                                                        # 'RED_SOLID_WHITE_HOLLOW_H'
        self.children = []
        self.CreateChildren()

    def CreateChildren(self):
        if self.depth > 0:
            if self.card_remain > 0:
                # add card step
                for move_position in self.moveable_set:
                    for j in range(1,9):
                        if self.check_move(move_position, selection_btn[j], self.board):
                            board = self.move(move_position, selection_btn[j], self.board)

                            # moveable_set = self.modify_moveable_set(move_position, self.moveable_set, board, selection_btn[j])
                            # removable_set = set()
                            # removable_set = self.modify_removable_set(move_position, self.removable_set, board, selection_btn[j])
                            #
                            moveable_set = self.scan_for_moveable(board)
                            removable_set = self.scan_for_removable(board)

                            self.children.append(Node(board,
                                                      self.card_remain - 1,
                                                      self.depth - 1,
                                                      copy.copy(self.move_card),
                                                      'MIN' if self.node_type == 'MAX' else 'MAX',
                                                      selection_btn[j],
                                                      moveable_set,
                                                      removable_set))

            elif self.card_remain == 0:
                # recycling step
                for remove_position in self.removable_set:
                    if self.check_removable(self.board, remove_position):

                        point1 = tuple((remove_position[0],self.board.col_header[remove_position[1]]))
                        point2 = self.board.get_data_entry(point1).get_neighbour_position()
                        remove_card_type = self.board.get_data_entry(point1).get_card_type()

                        afterMove_board = self.remove(self.board, remove_position)

                        # removable_set = self.rec_modify_removable_set(afterMove_board, remove_position, remove_card_type, self.removable_set, point2)
                        # moveable_set = self.rec_modify_moveable_set(afterMove_board, remove_position, remove_card_type, self.moveable_set, point2)

                        moveable_set = self.scan_for_moveable(afterMove_board)
                        removable_set = self.scan_for_removable(afterMove_board)

                        for move_position in moveable_set:
                            for k in range(1,9):
                                if move_position == remove_position and selection_map[remove_card_type] == k:
                                    continue
                                elif self.check_move(move_position, selection_btn[k], afterMove_board):
                                    afterM_board = self.move(move_position, selection_btn[k], afterMove_board)

                                    # moveable_set = self.modify_moveable_set(move_position, moveable_set, afterM_board, selection_btn[k])
                                    # removable_set = self.modify_removable_set(move_position,removable_set, afterM_board, selection_btn[k])

                                    moveable_set = self.scan_for_moveable(afterM_board)
                                    removable_set = self.scan_for_removable(afterM_board)

                                    self.children.append(Node(afterM_board,
                                                              self.card_remain - 1 + 1,
                                                              self.depth - 1,
                                                              copy.copy(self.move_card),
                                                              'MIN' if self.node_type == 'MAX' else 'MAX',
                                                              selection_btn[k],
                                                              moveable_set,
                                                              removable_set,
                                                              True,
                                                              self.change_to_point(remove_position),
                                                              remove_card_type))

    def scan_for_removable(self, board):
        removable_set = set()

        for row in board.row_header:
            for col in range(board.cols):
                entry1 = board.get_data_entry(tuple((row, board.col_header[col])))
                if entry1.get_type() != 0 and self.check_removeable(row, col, board):
                    # removable_set.add(tuple((row, col)))
                    neighbour = entry1.get_neighbour_position()
                    neighbourXY = tuple((neighbour[0], col_0_7[neighbour[1]]))
                    if (neighbourXY not in removable_set) and (tuple((row, col)) not in removable_set):
                        if entry1.get_card_type()[-1] == 'H':
                            removable_set.add(tuple((row, col))) if col < neighbourXY[1] else removable_set.add(neighbourXY)
                        else:
                            removable_set.add(tuple((row, col))) if row < neighbourXY[0] else removable_set.add(neighbourXY)
        return removable_set

    def check_removeable(self, row, col, board):
        point1 = tuple((row, board.col_header[col]))
        entry1 = board.get_data_entry(point1)
        point2 = entry1.get_neighbour_position()
        point2_row = point2[0]
        point2_col = col_0_7[point2[1]]
        card_type = entry1.get_card_type()

        if card_type[-1] == 'H':
            if col >= 7:
                return False
            if (board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0
                    and board.get_data_entry(
                        tuple((point2_row + 1, board.col_header[point2_col]))).get_type() == 0):
                return True
            else:
                return False

        elif card_type[-1] == 'V':
            if row > point2_row and row >= 12:
                return False
            if point2_row > row and point2_row >= 12:
                return False
            if (board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0
                    or board.get_data_entry(tuple((point2_row + 1, board.col_header[point2_col]))).get_type() == 0):
                return True
            else:
                return False


    def scan_for_moveable(self,board):
        moveable_set = set()

        for row in board.row_header:
            for col in range(board.cols):
                if board.get_data_entry(tuple((row, board.col_header[col]))).get_type() == 0 and self.check_moveable(row, col,board):
                    moveable_set.add(tuple((row, col)))

        return moveable_set

    def check_moveable(self, row, col, board):
        if row == 12 and col == 7:
            return False
        if row == 1 and col == 7:
            if board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0:
                return True
            else:
                return False
        if row == 12:
            if (board.get_data_entry(tuple((row, board.col_header[col + 1]))).get_type() == 0
                    and board.get_data_entry(tuple((row - 1, board.col_header[col]))).get_type() != 0
                    and board.get_data_entry(tuple((row - 1, board.col_header[col + 1]))).get_type() != 0):
                return True
            else:
                return False
        elif col == 7:
            if (board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0
                    and board.get_data_entry(tuple((row - 1, board.col_header[col]))).get_type() != 0):
                return True
            else:
                return False
        elif row == 1 :
            if (board.get_data_entry(tuple((row, board.col_header[col + 1]))).get_type() == 0
                    or board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0):
                return True
            else:
                return False
        # check for H
        elif (board.get_data_entry(tuple((row, board.col_header[col + 1]))).get_type() == 0
              and board.get_data_entry(tuple((row - 1, board.col_header[col]))).get_type() != 0
              and board.get_data_entry(tuple((row - 1, board.col_header[col + 1]))).get_type() != 0):
            return True
        # check for V
        elif (board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0
              and board.get_data_entry(tuple((row - 1, board.col_header[col]))).get_type() != 0):
            return True
        else:
            return False

    # def rec_modify_removable_set(self, board, remove_position, remove_card_type, removable_set, point2):
    #     # if remove_card_type is H
    #     #       if row == 1
    #     #           get the point1 and point2
    #     #           remove the point1 and point2
    #     #       else
    #     #           point1_down
    #     #           point2_down
    #     #           point1_down_neighbour
    #     #           point2_down_neighbour
    #     #           check whether for the four point can remove
    #     #           if can remove add into removable_set
    #     #           remove the point1 and point2
    #     # if remove_card_type is V
    #     #       if row == 1
    #     #           get the point1 and point2
    #     #           remove the point1 and point2
    #     #       else:
    #     #           point1_down
    #     #           point1_down_neighbour
    #     #           check whether the two point can add into the removable_set
    #     #           remove the point1 and point2
    #     #   return the copy of the removable_set
    #     row = remove_position[0]
    #     col = remove_position[1]
    #     removable_set = copy.copy(removable_set)
    #     point2_row = point2[0]
    #     point2_col = col_0_7[point2[1]]
    #
    #     if remove_card_type[-1] == 'H':
    #         removable_set.discard(tuple((row, col)))
    #         removable_set.discard(tuple((point2_row, point2_col)))
    #         if row != 1:
    #             point1_down = tuple((row - 1, board.col_header[col]))
    #             entry1_down = board.get_data_entry(point1_down)
    #             entry1_down_type = entry1_down.get_card_type()
    #
    #             if entry1_down_type[-1] == 'H':
    #                 entry1_down_neighbour = entry1_down.get_neighbour_position()
    #                 entry1_down_neighbourROW = entry1_down_neighbour[0]
    #                 entry1_down_neighbourCOL = col_0_7[entry1_down_neighbour[1]]
    #
    #                 if board.get_data_entry(tuple((entry1_down_neighbourROW + 1, board.col_header[entry1_down_neighbourCOL]))).get_type() == 0:
    #                     removable_set.add(tuple((row - 1, col)))
    #                     removable_set.add(tuple((entry1_down_neighbourROW, entry1_down_neighbourCOL)))
    #
    #             elif entry1_down_type[-1] == 'V':
    #                 entry1_down_neighbour = entry1_down.get_neighbour_position()
    #                 entry1_down_neighbourROW = entry1_down_neighbour[0]
    #                 entry1_down_neighbourCOL = col_0_7[entry1_down_neighbour[1]]
    #
    #                 removable_set.add(tuple((row - 1, col)))
    #                 removable_set.add(tuple((entry1_down_neighbourROW, entry1_down_neighbourCOL)))
    #
    #             point2_down = tuple((point2_row - 1, board.col_header[point2_col]))
    #             entry2_down = board.get_data_entry(point2_down)
    #             entry2_down_type = entry2_down.get_card_type()
    #
    #             if entry2_down_type[-1] == 'H':
    #                 entry2_down_neighbour = entry1_down.get_neighbour_position()
    #                 entry2_down_neighbourROW = entry2_down_neighbour[0]
    #                 entry2_down_neighbourCOL = col_0_7[entry2_down_neighbour[1]]
    #
    #                 if board.get_data_entry(tuple((entry2_down_neighbourROW + 1, board.col_header[entry2_down_neighbourCOL]))).get_type() == 0:
    #                     removable_set.add(tuple((row - 1, col)))
    #                     removable_set.add(tuple((entry2_down_neighbourROW, entry2_down_neighbourCOL)))
    #
    #             elif entry2_down_type[-1] == 'V':
    #                 entry2_down_neighbour = entry2_down.get_neighbour_position()
    #                 entry2_down_neighbourROW = entry2_down_neighbour[0]
    #                 entry2_down_neighbourCOL = col_0_7[entry2_down_neighbour[1]]
    #
    #                 removable_set.add(tuple((row - 1, col)))
    #                 removable_set.add(tuple((entry2_down_neighbourROW, entry2_down_neighbourCOL)))
    #
    #     elif remove_card_type[-1] == 'V':
    #         removable_set.discard(tuple((row, col)))
    #         removable_set.discard(tuple((point2_row, point2_col)))
    #
    #         if row != 1 and point2_row != 1:
    #             judge_point = tuple((row - 1, board.col_header[col]))
    #
    #             if row > point2_row:
    #                 judge_point = tuple((point2_row - 1 , board.col_header[point2_col]))
    #
    #             judge_entry = board.get_data_entry(judge_point)
    #             judge_entry_type = judge_entry.get_card_type()
    #
    #             if judge_entry_type[-1] == 'H':
    #                 judge_entry_neighbour = judge_entry.get_neighbour_position()
    #                 judge_entry_neighbourROW = judge_entry_neighbour[0]
    #                 judge_entry_neighbourCOL = col_0_7[judge_entry_neighbour[1]]
    #
    #                 if board.get_data_entry(tuple((judge_entry_neighbourROW + 1, board.col_header[judge_entry_neighbourCOL]))).get_type() == 0:
    #                     removable_set.add(judge_point)
    #                     removable_set.add(tuple((judge_entry_neighbourROW,judge_entry_neighbourCOL)))
    #
    #             elif judge_entry_type[-1] == 'V':
    #                 judge_entry_neighbourXY = judge_entry.get_neighbour_position()
    #                 judge_entry_neighbourROW = judge_entry_neighbourXY[0]
    #                 judge_entry_neighbourCOL = col_0_7[judge_entry_neighbourXY[1]]
    #
    #                 removable_set.add(judge_point)
    #                 removable_set.add(tuple((judge_entry_neighbourROW, judge_entry_neighbourCOL)))
    #
    #     return removable_set

    # def rec_modify_moveable_set(self, board, remove_position, remove_card_type, moveable_set, point2):
    #     # if remove_card_type is H
    #     #       add point1 and point2 into moveable_set
    #     # if remove_card_type is V
    #     #       add the upper point into moveable_set
    #     row = remove_position[0]
    #     col = remove_position[1]
    #     moveable_set = copy.copy(moveable_set)
    #     point2_row = point2[0]
    #     point2_col = col_0_7[point2[1]]
    #
    #     if remove_card_type[-1] == 'H':
    #         moveable_set.add(tuple((row, col)))
    #         moveable_set.add(tuple((point2_row, point2_col)))
    #         moveable_set.discard(tuple((row + 1, col)))
    #         moveable_set.discard(tuple((point2_row + 1, point2_col)))
    #
    #     elif remove_card_type[-1] == 'V':
    #         if row > point2_row:
    #             moveable_set.add(tuple((point2_row, point2_col)))
    #             moveable_set.discard(tuple((row + 1, col)))
    #         else:
    #             moveable_set.add(tuple((row, col)))
    #             moveable_set.discard(tuple((point2_row + 1, point2_col)))
    #
    #     return moveable_set

    def remove(self, board, remove_position):
        # modify the board
        # set the element to empty
        # record the remove position into remove_card_position
        # record the remove card type
        # return the deep copy of the board
        board_C = copy.deepcopy(board)
        row = remove_position[0]
        col = remove_position[1]
        point1 = tuple((row, board_C.col_header[col]))
        entry1 = board_C.get_data_entry(point1)
        entry2 = entry1.get_neighbour()
        entry1.set_empty()
        entry2.set_empty()
        return board_C


    def check_removable(self, board, remove_position):
        # judge the last move card whether can remove
        # get the card
        # if the card is H
        #       for the two upper point ,whether the point is not null
        # if the card is V
        #       for the two point ,whether either one point's upper point is not null
        row = remove_position[0]
        col = remove_position[1]
        point1 = tuple((row, board.col_header[col]))
        entry1 = board.get_data_entry(point1)
        card_type = entry1.get_card_type()
        point2 = entry1.get_neighbour_position()

        if point2 != None:
            row_neighbour = point2[0]
            col_neighbour = col_0_7[point2[1]]

            if ((point1 == self.last_move_card[0] or point1 == self.last_move_card[1])
                    and (point2 == self.last_move_card[0] or point2 == self.last_move_card[1])):
                return False
            if card_type[-1] == 'H':
                if (board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0
                        and board.get_data_entry(tuple((row_neighbour + 1, board.col_header[col_neighbour]))).get_type() == 0):
                    return True
                else:
                    return False
            elif card_type[-1] == 'V':
                if (row > row_neighbour) \
                        and board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0:
                    return True
                elif (row < row_neighbour) \
                        and board.get_data_entry(tuple((row_neighbour + 1, board.col_header[col_neighbour]))).get_type() == 0:
                    return True
                else:
                    return False
        else:
            return False


    def modify_moveable_set(self, move_step, moveable_set, board, selection):
        # if selection is H
        #       get two point1 and point2
        #       remove the two point from the moveable_set
        #       add the upper two point into the moveable_set
        # if selection is V
        #       get two point1 and point2
        #       remove the point from the moveable_set
        #       add the one upper point into the moveable_set
        # return the copy of the moveable_set
        row = move_step[0]
        col = move_step[1]
        moveable_set_c = copy.copy(moveable_set)
        if selection[-1] == 'H':
            point2 = tuple((row, col + 1))
            moveable_set_c.discard(move_step)
            moveable_set_c.discard(point2)
            if row != 12:
                moveable_set_c.add(tuple((row + 1, col)))
                moveable_set_c.add(tuple((row + 1, col + 1)))
        if selection[-1] == 'V':
            point2 = tuple((row + 1, col))
            moveable_set_c.discard(move_step)
            moveable_set_c.discard(point2)
            if row != 11:
                moveable_set_c.add(tuple((row + 2, col)))

        return moveable_set_c

    def modify_removable_set(self, move_step, removable_set, board, selection):
        # if selection is H
        #       get two move point1 and point2
        #       if row == 1
        #              removable_set add point1 and point2 ???????
        #       else:
        #              point1 get the bottom point -> 1
        #              point2 get the bottom point -> 2
        #              1's neighbour               -> 3
        #              2's neighbour               -> 4
        #              remove the 1,2,3,4 point from the removeable_set
        #              consider whether point1 and point2 can be remove ??????
        # if selection is V
        #       get two point1 and point2
        #       if row == 1
        #               removable_set add point1 and point2
        #       else:
        #               point bottom point -> 1
        #               1's neightbour     -> 2
        #               remove 1,2 from the removable set
        row = move_step[0]
        col = move_step[1]
        removable_set_c = copy.copy(removable_set)

        if selection[-1] == 'H':
            if row == 1:
                removable_set_c.add(tuple((row, col)))
                removable_set_c.add(tuple((row, col + 1)))
            else:
                point1_down = board.get_data_entry(tuple((row - 1, board.col_header[col])))
                point2_down = board.get_data_entry(tuple((row - 1, board.col_header[col + 1])))
                point1_down_neighbour = point1_down.get_neighbour_position()
                point2_down_neighbour = point2_down.get_neighbour_position()
                point1_down_neighbourXY = tuple((point1_down_neighbour[0], col_0_7[point1_down_neighbour[1]]))
                point2_down_neighbourXY = tuple((point2_down_neighbour[0], col_0_7[point2_down_neighbour[1]]))
                removable_set_c.discard(tuple((row - 1, col)))
                removable_set_c.discard(tuple((row - 1, col + 1)))
                removable_set_c.discard(point1_down_neighbourXY)
                removable_set_c.discard(point2_down_neighbourXY)
                removable_set_c.add(tuple((row, col)))
                removable_set_c.add(tuple((row, col + 1)))
        elif selection[-1] == 'V':
            if row == 1:
                removable_set_c.add(tuple((row , col)))
                removable_set_c.add(tuple((row + 1 , col)))
            else:
                point_down = board.get_data_entry(tuple((row - 1, board.col_header[col])))
                point_down_neighbour = point_down.get_neighbour_position()
                point_down_neighbourXY = tuple((point_down_neighbour[0], col_0_7[point_down_neighbour[1]]))
                removable_set_c.discard(tuple((row - 1, col)))
                removable_set_c.discard(point_down_neighbourXY)
                removable_set_c.add(tuple((row, col)))
                removable_set_c.add(tuple((row + 1, col)))

        return removable_set_c

    def move(self, move_point, selection, board):
        # modify the board
        # config two element
        # set move_card = move_step
        # return the deep copy of the board
        # print('-'*10, selection_btn)
        row = move_point[0]
        col = move_point[1]
        board_C = copy.deepcopy(board)

        if selection[-1] == 'H':
            point1 = tuple((row, board_C.col_header[col]))
            point2 = tuple((row, board_C.col_header[col + 1]))
            entry1 = board_C.get_data_entry(point1)
            entry2 = board_C.get_data_entry(point2)
            str = selection.split('_')
            entry1.set_type(element_map[str[0] + '_' + str[1]])
            entry2.set_type(element_map[str[2] + '_' + str[3]])
            self.config_element(entry1, entry2, point1, point2, selection)

        elif selection[-1] == 'V':
            point1 = tuple((row, board_C.col_header[col]))
            point2 = tuple((row + 1, board_C.col_header[col]))
            entry1 = board_C.get_data_entry(point1)
            entry2 = board_C.get_data_entry(point2)
            str = selection.split('_')
            entry1.set_type(element_map[str[0] + '_' + str[1]])
            entry2.set_type(element_map[str[2] + '_' + str[3]])
            self.config_element(entry1, entry2, point1, point2, selection)

        self.move_card = tuple((point1, point2))

        return board_C

    def config_element(self, element1, element2, point1, point2, cur_selection):
        # print('point1 point2:', point1, point2)
        element1.set_neighbour(element2)
        element2.set_neighbour(element1)
        element1.set_neighbour_position(point2)
        element2.set_neighbour_position(point1)
        element1.set_card_type(cur_selection)
        element2.set_card_type(cur_selection)

    def check_move(self, move_point, selection, board):
        row = move_point[0]
        col = move_point[1]

        if selection[-1] == 'H':
            if col == 7:
                return False
            if row == 1:
                if (board.get_data_entry(tuple((row, board.col_header[col]))).get_type() == 0
                        and board.get_data_entry(tuple((row , board.col_header[col + 1]))).get_type() == 0 ):
                    return True
                else:
                    return False
            else:
                if (board.get_data_entry(tuple((row, board.col_header[col]))).get_type() == 0
                        and board.get_data_entry(tuple((row, board.col_header[col + 1]))).get_type() == 0
                        and board.get_data_entry(tuple((row - 1, board.col_header[col]))).get_type() != 0
                        and board.get_data_entry(tuple((row - 1, board.col_header[col + 1]))).get_type() != 0 ) :
                    return True
                else:
                    return False
        elif selection[-1] == 'V':
            if row == 12:
                return False
            if row == 1:
                if (board.get_data_entry(tuple((row, board.col_header[col]))).get_type() == 0
                        and board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0):
                    return True
                else:
                    return False
            else:
                if (board.get_data_entry(tuple((row, board.col_header[col]))).get_type() == 0
                        and board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0
                        and board.get_data_entry(tuple((row - 1, board.col_header[col]))).get_type() != 0):
                    return True
                else:
                    return False

    def change_to_point(self, remove_position):
        return tuple((remove_position[0], self.board.col_header[remove_position[1]]))


    def heuristic(self, board):
        # return self.test_num + 1
        score = 0
        red_count = 0
        white_count = 0

        for r in range(board.rows):
            for c in range(board.cols):
                scan_point = self.board.get_data_entry(tuple((r + 1 , self.board.col_header[c]))).get_type()
                if scan_point == 1 or scan_point == 3:
                    red_count += 1
                    score += self.calculate(white_count)
                    white_count = 0
                if scan_point == 2 or scan_point == 4:
                    white_count += 1
                    score += self.calculate(red_count)
                    red_count = 0
        if red_count != 0:
            score = score + self.calculate(red_count)
            red_count = 0
        elif white_count != 0:
            score = score + self.calculate(white_count)
            white_count = 0

        return score

    def calculate(self, count):
        if count == 1:
            return 1
        elif count == 2:
            return 10
        elif count == 3:
            return 100
        elif count == 4:
            return 1000
        elif count == 0:
            return 0
        else:
            return 0

def naive_heuristic(board):
    white_hollow = 0
    white_solid = 0
    red_solid = 0
    red_hollow = 0

    for row in board.row_header:
        for col in range(board.cols):
            if board.get_data_entry(tuple((row, board.col_header[col]))).get_type() == 1:
                red_solid = coordinate(row, col) + red_solid
            elif board.get_data_entry(tuple((row, board.col_header[col]))).get_type() == 2:
                white_hollow = coordinate(row, col) + white_hollow
            elif board.get_data_entry(tuple((row, board.col_header[col]))).get_type() == 3:
                red_hollow = coordinate(row, col) + red_hollow
            elif board.get_data_entry(tuple((row, board.col_header[col]))).get_type() == 4:
                white_solid = coordinate(row, col) + white_solid

    return white_hollow + 3 * white_solid - 2 * red_solid - 1.5 * red_hollow

def coordinate(row, col):
    return (row - 1) * 10 + (col + 1)

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
        self.card_remain = 4
        self.cur_player = 0
        self.step = 0
        # self.mode = 'M'
        self.mode = 'AI'
        self.last_move_card = None
        self.player1 = None
        self.player2 = None
        self.end = 60

        self.trace_file = False
        self.ab_on_off = False

        self.ai_first = False

        self.depth = 2
        self.init_value = 0
        self.alpha_beta_count = 0


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

        choose_color = lambda : self.select_color()
        choose_dots = lambda : self.select_dots()
        alpha_beta_on_off = lambda : self.AB_on_off()
        Ai_first = lambda :self.AI_First()
        Mode_choice = lambda : self.mode_chioce()
        trace_file = lambda : self.trace_file_opt()

        ab_ONOFF = Button(self.app, command = alpha_beta_on_off, text = 'AlphaBeta ON/OFF')
        ab_ONOFF.place(x=20, y=400, height=40, width=130)

        trace_ONOFF = Button(self.app, command = trace_file, text = 'Trace File')
        trace_ONOFF.place(x=20, y=550, height=40, width=130)

        mode_choice = Button(self.app, command = Mode_choice, text = 'Mode Choice')
        mode_choice.place(x = 20, y = 450, height = 40, width = 130)

        color_btn = Button(self.app, command = choose_color, text = 'COLOR')
        color_btn.place(x = 20, y = 350, height = 40, width = 60)

        dots_btn = Button(self.app, command = choose_dots, text = 'DOTS')
        dots_btn.place(x = 80, y = 350, height = 40, width = 60)

        Ai_First = Button(self.app, command = Ai_first, text = 'AI as FIRST PLAYER')
        Ai_First.place(x=20, y=500, height=40, width=130)

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

    def mode_chioce(self):
        if self.mode == 'M':
            self.mode = 'AI'
            print('AI MODE')
        elif self.mode == 'AI':
            self.mode = 'M'
            print('HUMAN MODE')

    def trace_file_opt(self):
        if self.trace_file:
            self.trace_file = False
            print('Trace File OFF')
        else:
            self.trace_file = True
            print('Trace File ON')

    def board_btn_clicked(self, row, col):
        if (self.card_remain > 0):
            print('-------------------------------')
            print('button clicked: {}, {}'.format(row, self.board.col_header[col - 1]))
            if self.cur_selection == 'UNDEFINED':
                # do nothing if current state is undefined
                print('UNDEFINED')
                pass
            else:
                direction = self.cur_selection[-1]

                if (direction == 'H' and 1 <= row <= self.board.rows and 1 <= col <= self.board.cols - 1):
                    point1 = tuple((row, self.board.col_header[col - 1]))
                    point2 = tuple((row, self.board.col_header[col]))
                elif (direction == 'V' and 1 <= row <= self.board.rows - 1 and 1 <= col <= self.board.rows):
                    point1 = tuple((row, self.board.col_header[col - 1]))
                    point2 = tuple((row + 1, self.board.col_header[col - 1]))
                else:
                    print('out of the board')
                    return

                key1, key2 = get_component_icon(self.cur_selection)

                if (self.is_valid_step( point1, point2)):
                    # update UI
                    entry1_btn = self.data_btn[point1[0], point1[1]]
                    entry1_btn.config(image=self.icons[key1])
                    entry2_btn = self.data_btn[point2[0], point2[1]]
                    entry2_btn.config(image=self.icons[key2])

                    # upate the data status
                    entry1 = self.board.get_data_entry(point1)
                    entry2 = self.board.get_data_entry(point2)
                    str = self.cur_selection.split('_')
                    entry1.set_type(element_map[str[0] + '_' + str[1]])
                    entry2.set_type(element_map[str[2] + '_' + str[3]])

                    self.config_element(entry1, entry2, point1, point2, self.cur_selection)

                    # check winner
                    self.announce_winner(self.check_winner(point1, point2))

                    # config the parameter
                    self.card_remain = self.card_remain - 1
                    self.step = self.step + 1
                    self.player = self.step % 2
                    self.last_move_card = tuple((point1, point2))

                    if self.step > self.end:
                        messagebox.showinfo('GAME END', 'GAME END')

                    if self.player == 0:
                        self.var.set("   Player1 Turn")
                    elif self.player == 1:
                        self.var.set("   Player2 Turn")

                    if (self.mode == 'AI'):
                        if(self.player == 1):
                            self.AI_Step()
                        elif (self.ai_first and self.player == 0):
                            self.AI_First()
                    print('SUCCESS!!')
                else:
                    print("The Step is not Valid!!!")

        else:
            print('-------------------------------')
            # todo: remove card step
            # remove card
            # update the GUI
            # remind_card + 1
            # cur_player = cur_player
            point1 = tuple((row, self.board.col_header[col - 1]))
            print('remove card position:',row, col, point1)
            selecte_element1 = self.board.get_data_entry(point1)
            selecte_element2 = selecte_element1.get_neighbour()
            point2 = selecte_element1.get_neighbour_position()

            if self.is_valid_remove_step(point1, point2):

                # update the UI
                element_btn1 = self.data_btn[point1[0], point1[1]]
                element_btn1.config(image=self.icons['img/empty.png'])
                element_btn2 = self.data_btn[point2[0], point2[1]]
                element_btn2.config(image=self.icons['img/empty.png'])
                self.cur_selection = selecte_element1.get_card_type()
                self.card_remain = self.card_remain + 1

                selecte_element1.set_empty()
                selecte_element2.set_empty()
            else:
                print('You Can not Choice the block!!!')

    def OutPut_File(self, f, root_node, best_value, level2_list, alpha_beta_count):
        level3_count = 0

        if self.ab_on_off:
            level3_count = alpha_beta_count
        else:
            for child in root_node.children:
                level3_count += len(child.children)
        f.writelines(str(level3_count))
        f.writelines('\n')
        f.writelines(str(best_value))
        f.writelines('\n')
        f.writelines('\n')
        for num in level2_list:
            f.writelines(str(num))
            f.writelines('\n')
        f.writelines('\n')

    def AI_First(self):
        self.ai_first = True
        removable_set = self.get_removable_set(self.board)
        moveable_set = self.get_moveable_set(self.board)

        start = time.time()
        root_node = Node(self.board,
                         self.card_remain,
                         self.depth,
                         self.last_move_card,
                         'MAX',
                         self.cur_selection,
                         moveable_set,
                         removable_set)
        end = time.time()
        print('------USING-------------',end - start)
        best_value = -maxsize
        best_node = root_node

        if self.ab_on_off:
            self.alpha_beta(self.depth, root_node, maxsize, -maxsize)
        else:
            self.MinMax(root_node, self.depth)

        level2_list = []
        for child in root_node.children:
            level2_list.append(child.i_value)
            if child.i_value > best_value:
                best_value = child.i_value
                best_node = child

        if self.trace_file:
            f = open('./output.txt', 'a')
            self.OutPut_File(f, root_node, best_value, level2_list, self.alpha_beta_count)
            self.alpha_beta_count = 0

        self.cur_selection = best_node.selection_card_type

        if not best_node.recycling:
            point1 = best_node.last_move_card[0]
            row = point1[0]
            col = col_map[point1[1]]
            self.execute_ai_step(row, col)
        else:
            remove_position = best_node.remove_card_position
            row = remove_position[0]
            col = col_map[remove_position[1]]
            self.execute_ai_step(row, col)

            move_point = best_node.last_move_card[0]
            self.cur_selection = best_node.selection_card_type
            row = move_point[0]
            col = col_map[move_point[1]]
            self.execute_ai_step(row, col)

    def get_removable_set(self, board):
        removable_set = set()

        for row in board.row_header:
            for col in range(board.cols):
                entry1 = board.get_data_entry(tuple((row, board.col_header[col])))
                if entry1.get_type() != 0 and self.check_removeable(row, col, self.board):
                    neighbour = entry1.get_neighbour_position()
                    neighbourXY = tuple((neighbour[0], col_0_7[neighbour[1]]))
                    if (neighbourXY not in removable_set) and (tuple((row, col)) not in removable_set):
                        if entry1.get_card_type()[-1] == 'H':
                            removable_set.add(tuple((row, col))) if col < neighbourXY[1] else removable_set.add(neighbourXY)
                        else:
                            removable_set.add(tuple((row, col))) if row < neighbourXY[0] else removable_set.add(neighbourXY)
        return removable_set

    def execute_ai_step(self, row , col):
        if (self.card_remain > 0):
            print('-------------------------------')
            print('button clicked: {}, {}'.format(row, self.board.col_header[col - 1]))
            if self.cur_selection == 'UNDEFINED':
                # do nothing if current state is undefined
                print('UNDEFINED')
                pass
            else:
                direction = self.cur_selection[-1]

                if (direction == 'H' and 1 <= row <= self.board.rows and 1 <= col <= self.board.cols - 1):
                    point1 = tuple((row, self.board.col_header[col - 1]))
                    point2 = tuple((row, self.board.col_header[col]))
                elif (direction == 'V' and 1 <= row <= self.board.rows - 1 and 1 <= col <= self.board.rows):
                    point1 = tuple((row, self.board.col_header[col - 1]))
                    point2 = tuple((row + 1, self.board.col_header[col - 1]))
                else:
                    print('out of the board')
                    return

                key1, key2 = get_component_icon(self.cur_selection)

                if (self.is_valid_step( point1, point2)):
                    # update UI
                    entry1_btn = self.data_btn[point1[0], point1[1]]
                    entry1_btn.config(image=self.icons[key1])
                    entry2_btn = self.data_btn[point2[0], point2[1]]
                    entry2_btn.config(image=self.icons[key2])

                    # upate the data status
                    entry1 = self.board.get_data_entry(point1)
                    entry2 = self.board.get_data_entry(point2)
                    str = self.cur_selection.split('_')
                    entry1.set_type(element_map[str[0] + '_' + str[1]])
                    entry2.set_type(element_map[str[2] + '_' + str[3]])

                    self.config_element(entry1, entry2, point1, point2, self.cur_selection)

                    # check winner
                    self.announce_winner(self.check_winner(point1, point2))

                    # config the parameter
                    self.card_remain = self.card_remain - 1
                    self.step = self.step + 1
                    self.player = self.step % 2
                    self.last_move_card = tuple((point1, point2))

                    if self.step > self.end:
                        messagebox.showinfo('GAME END','GAME END')

                    if self.player == 0:
                        self.var.set("   Player1 Turn")
                    elif self.player == 1:
                        self.var.set("   Player2 Turn")
                    print('SUCCESS!!')
                else:
                    print("The Step is not Valid!!!")

        else:
            print('-------------------------------')
            point1 = tuple((row, self.board.col_header[col - 1]))
            print('remove card position:',row, col, point1)
            selecte_element1 = self.board.get_data_entry(point1)
            selecte_element2 = selecte_element1.get_neighbour()
            point2 = selecte_element1.get_neighbour_position()

            if self.is_valid_remove_step(point1, point2):
                element_btn1 = self.data_btn[point1[0], point1[1]]
                element_btn1.config(image=self.icons['img/empty.png'])
                element_btn2 = self.data_btn[point2[0], point2[1]]
                element_btn2.config(image=self.icons['img/empty.png'])
                self.cur_selection = selecte_element1.get_card_type()
                self.card_remain = self.card_remain + 1

                selecte_element1.set_empty()
                selecte_element2.set_empty()
            else:
                print('You Can not Choice the block!!!')

    def check_removeable(self, row, col, board):
        point1 = tuple((row, board.col_header[col]))
        entry1 = board.get_data_entry(point1)
        point2 = entry1.get_neighbour_position()
        point2_row = point2[0]
        point2_col = col_0_7[point2[1]]
        card_type = entry1.get_card_type()

        if card_type[-1] == 'H':
            if (board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0
                and board.get_data_entry(tuple((point2_row + 1, board.col_header[point2_col]))).get_type() == 0):
                    return True
            else:
                return False

        elif card_type[-1] == 'V':
            if row > point2_row and row >= 12:
                return False
            if point2_row > row and point2_row >= 12:
                return False
            if (board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0
                    or board.get_data_entry(tuple((point2_row + 1, board.col_header[point2_col]))).get_type() == 0):
                return True
            else:
                return False

    def AB_on_off(self):
        if self.ab_on_off :
            self.ab_on_off = False
            print("Alpha_Beta OFF")
        else:
            self.ab_on_off = True
            print("Alpha_Beta ON")

    def AI_Step(self):
        removable_set = self.get_removable_set(self.board)
        moveable_set = self.get_moveable_set(self.board)

        start = datetime.datetime.now()
        root_node = Node(self.board,
                         self.card_remain,
                         self.depth,
                         self.last_move_card,
                         'MAX',
                         self.cur_selection,
                         moveable_set,
                         removable_set)

        end = datetime.datetime.now()
        print('------------USING-----------', end - start)
        best_value = -maxsize
        best_node = root_node

        if self.ab_on_off:
            self.alpha_beta(self.depth, root_node, -maxsize, maxsize)
        else:
            self.MinMax(root_node, self.depth)

        level2_list = []

        for child in root_node.children:
            level2_list.append(child.i_value)
            if child.i_value > best_value:
                best_value = child.i_value
                best_node = child

        if self.trace_file:
            f = open('./output.txt', 'a')
            self.OutPut_File(f, root_node, best_value, level2_list, self.alpha_beta_count)
            self.alpha_beta_count = 0

        self.cur_selection = best_node.selection_card_type
        if not best_node.recycling:
            point1 = best_node.last_move_card[0]
            row = point1[0]
            col = col_map[point1[1]]
            self.board_btn_clicked(row, col)
        else:
            remove_position = best_node.remove_card_position
            row = remove_position[0]
            col = col_map[remove_position[1]]
            self.board_btn_clicked(row, col)

            move_point = best_node.last_move_card[0]
            self.cur_selection = best_node.selection_card_type
            row = move_point[0]
            col = col_map[move_point[1]]
            self.board_btn_clicked(row, col)


    def get_moveable_set(self, board):
        # moveable store (1,0) -> (1, 'A') can be reflect to point
        moveable_set = set()

        for row in board.row_header:
            for col in range(board.cols):
                if board.get_data_entry(tuple((row, board.col_header[col]))).get_type() == 0 and self.check_moveable(row, col, self.board):
                    moveable_set.add(tuple((row, col)))

        return moveable_set

    def check_moveable(self, row, col, board):
        # check first line
        if row == 12 and col == 7:
            return False
        if row == 1 and col == 7:
            if board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0:
                return True
            else:
                return False
        if row == 12:
            if (board.get_data_entry(tuple((row, board.col_header[col + 1]))).get_type() == 0
                    and board.get_data_entry(tuple((row - 1, board.col_header[col]))).get_type() != 0
                    and board.get_data_entry(tuple((row - 1, board.col_header[col + 1]))).get_type() != 0):
                return True
            else:
                return False
        elif col == 7:
            if (board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0
                    and board.get_data_entry(tuple((row - 1, board.col_header[col]))).get_type() != 0):
                return True
            else:
                return False
        elif row == 1 :
            if (board.get_data_entry(tuple((row, board.col_header[col + 1]))).get_type() == 0
                    or board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0):
                return True
            else:
                return False
        # check for H
        elif (board.get_data_entry(tuple((row, board.col_header[col + 1]))).get_type() == 0
              and board.get_data_entry(tuple((row - 1, board.col_header[col]))).get_type() != 0
              and board.get_data_entry(tuple((row - 1, board.col_header[col + 1]))).get_type() != 0):
            return True
        # check for V
        elif (board.get_data_entry(tuple((row + 1, board.col_header[col]))).get_type() == 0
              and board.get_data_entry(tuple((row - 1, board.col_header[col]))).get_type() != 0):
            return True
        else:
            return False

    # def test_function(self):
    #     f = open('test.txt', 'r')
    #     for line in f.readlines():
    #         cmd = line.strip()
    #         command = cmd.split(' ')
    #         if len(command) == 4:
    #             self.cur_selection = selection_btn[int(command[1])]
    #             self.board_btn_clicked(int(command[3]), col_map[command[2]])
    #         if len(command) == 7:
    #             row = int(command[1])
    #             col = col_map[command[0]]
    #             self.board_btn_clicked(row, col)
    #             self.cur_selection = selection_btn[int(command[4])]
    #             col = col_map[command[-2]]
    #             row = int(command[-1])
    #             self.board_btn_clicked(row, col)
    #
    #     f.close()

    def board_to_matrix(self, board):
        board_matrix = np.zeros((12,8))

        for row in range(board.rows):
            for col in range(self.board.cols):
                board_matrix[row][col] = board.get_data_entry(tuple((row + 1, self.board.col_header[col]))).get_type()

        print(board_matrix)

        return board_matrix


    def test_function(self):
        removable_set = set()

        for row in self.board.row_header:
            for col in range(self.board.cols):
                if self.board.get_data_entry(tuple((row, self.board.col_header[col]))).get_type() != 0 \
                        and self.check_removeable(row, col, self.board):
                    neighbour = self.board.get_data_entry(tuple((row, self.board.col_header[col]))).get_neighbour_position()
                    neighbourXY = tuple((neighbour[0], col_0_7[neighbour[1]]))
                    if (neighbourXY not in removable_set) and (tuple((row, col)) not in removable_set):
                        removable_set.add(tuple((row, col)))
        return removable_set

    def MinMax(self, node, depth):
        if depth == 0:
            node.i_value = naive_heuristic(node.board)
            return node.i_value

        if node.node_type == 'MAX':
            best_value = -maxsize;
            for i in range(len(node.children)):
                child = node.children[i]
                selected_node_value = self.MinMax(child, depth - 1)
                if selected_node_value > best_value:
                    best_value = selected_node_value

            node.i_value = best_value

        elif node.node_type == 'MIN':
            best_value = maxsize
            for i in range(len(node.children)):
                child = node.children[i]
                selected_node_value = self.MinMax(child, depth - 1)
                if selected_node_value < best_value:
                    best_value = selected_node_value
            node.i_value = best_value

        return node.i_value

    def alpha_beta(self, depth, node, alpha, beta):
        if depth == 0:
            self.alpha_beta_count = self.alpha_beta_count + 1
            node.i_value = naive_heuristic(node.board)
            return node.i_value

        else:
            if node.node_type == 'MAX':
                for child in node.children:
                    alpha = max(alpha, self.alpha_beta(depth - 1, child, alpha, beta))
                    if alpha >= beta:
                        node.i_value = alpha
                        return alpha
                node.i_value = alpha
                return alpha
            else:
                for child in node.children:
                    beta = min(beta, self.alpha_beta(depth - 1, child, alpha, beta))
                    if beta <= alpha:
                        node.i_value = beta
                        return beta
                node.i_value = beta
                return beta



    def select_color(self):
        print('color')
        self.player1 = 'color'
        self.player2 = 'dots'

    def select_dots(self):
        print('dots')
        self.player1 = 'dots'
        self.player2 = 'color'


    def announce_winner(self, winner):
        if winner[0] and winner[1]:
            if self.player == 0:
                messagebox.showinfo("WINNER",'Player ONE Win')
            else :
                messagebox.showinfo("WINNER",'Player TWO Win')
        if winner[0] and not winner[1]:
            if self.player1 == 'color':
                messagebox.showinfo("WINNER","Player ONE Win")
            else:
                messagebox.showinfo("WINNER", "Player TWO Win")
        elif not winner[0] and winner[1] :
            if self.player1 == 'dots':
                messagebox.showinfo("WINNER", "Player ONE Win")
            else:
                messagebox.showinfo("WINNER", "Player TWO Win")




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


    def is_valid_step(self, point1, point2):
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
