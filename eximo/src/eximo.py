from colorama import Fore, Back, Style 
from copy import copy

from state import State, start_state
from aux import Direction
from eval import *
import sys

import time

from typing import Callable


class Eximo:
    prv_player = 2

    cuts = 0
    children = 0

    def __init__(self, p1: list, p2: list):
        self.player = {}
        self.player[1] = p1
        self.player[2] = p2

    def game_over(self, state: State) -> bool:
        if state.score[1] <= 0:
            state.print()
            print("Player 2 won!")
            return True
        elif state.score[2] <= 0:
            state.print()
            print("Player 1 won!")
            return True
        elif self.prv_player == state.player:
            state.print()
            print('Player ' + str(state.player) + ' has ran out of moves...')
            print('Player ' + str(state.player % 2 + 1) + ' won!')
            return True
        return False

    def play(self):
        state = start_state
        self.prv_player = state.player % 2 + 1

        while not self.game_over(state):
            state.print()

            self.prv_player = state.player

            if self.player[state.player][0] == 'P':
                state = self.player_move(state)
            
            else:
                start = time.time()
                state = self.minimax_prunning(state, self.player[state.player][1], state.player, self.player[state.player][2])
                end = time.time()
                print("------- MINIMAX STATS START --------")
                print("elapsed time : " + str(end - start) + " seconds")
                print("number of children : " + str(self.cuts))
                print("number of cuts : " + str(self.children))
                print("-------- MINIMAX STATS END ---------")
                self.cuts = 0
                self.children = 0

    def statistics(self, filename):
        file = open(filename, "w")

        # plays = {}
        # plays[1] = [0, 0, 0, 0]
        # plays[2] = [0, 0, 0, 0]

        file.write('Player,Depth,Heuristic')
        file.write('\n1,' + str(self.player[1][1]) + ',' + str(self.player[1][2].__name__))
        file.write('\n2,' + str(self.player[2][1]) + ',' + str(self.player[2][2].__name__))
        file.write('\n')
        file.write('\nPlayer,Elapsed Time,Leaves,Cuts')
        
        state = start_state
        state.prv_player = state.player % 2 + 1
        while True:
            self.prv_player = state.player

            start = time.time()
            state = self.minimax_prunning(state, self.player[state.player][1], state.player, self.player[state.player][2])
            end = time.time()
            
            # plays[state.player % 2 + 1][0] += 1
            # plays[state.player % 2 + 1][1] += end - start
            # plays[state.player % 2 + 1][2] += self.children
            # plays[state.player % 2 + 1][3] += self.cuts

            file.write('\n' + str(state.player % 2 + 1) + ',' + str(end - start) + ',' + str(self.children) + ',' + str(self.cuts))

            self.cuts = 0
            self.children = 0

            if state.score[1] <= 0:
                file.write('\n\nWinner,2')
                break
            elif state.score[2] <= 0:
                file.write('\n\nWinner,1')
                break
            elif self.prv_player == state.player:
                file.write('\n\nWinner,' + str(state.player % 2 + 1) + '\n\n\n')
                break
        
        file.close()


    @staticmethod
    def sel_cell() -> tuple:
        while True:
            
            row_number = input('Row (1-8): ')
            while len(row_number) > 1 or len(row_number) == 0:
                row_number = input('Row (1-8): ') 
            row = ord(row_number) - 49

            col_number = input('Col (A-H): ').lower()
            while len(col_number) > 1 or len(col_number) == 0:
                col_number = input('Col (A-H): ').lower()
            col = ord(col_number) - 97

            if State.valid_position((row, col)):
                return (row, col)

    @staticmethod
    def sel_cp_dir() -> tuple:
        while True:
            dir = input('Direction (W|NW|N|NE|E): ').upper()
            if dir == 'W':
                return Direction.WEST
            elif dir == 'NW':
                return Direction.NORTHWEST
            elif dir == 'N':
                return Direction.NORTH
            elif dir == 'NE':
                return Direction.NORTHEAST
            elif dir == 'E':
                return Direction.EAST

    @staticmethod
    def sel_mv_dir() -> tuple:
        while True:
            dir = input('Direction (NW|N|NE): ').upper()
            if dir == 'NW':
                return Direction.NORTHWEST
            elif dir == 'N':
                return Direction.NORTH
            elif dir == 'NE':
                return Direction.NORTHEAST

    @staticmethod
    def player_move(state) -> State:
        n_state = None
        while n_state == None:
            
            # start mode
            if state.action[0] == 1:
                pos = Eximo.sel_cell()
                if not state.is_ally(pos):
                    continue

                if state.check_capture():
                    vec = Eximo.sel_cp_dir()
                    n_state = state.capture(pos, vec)
                else:
                    vec = Eximo.sel_mv_dir()
                    n_state = state.move(pos, vec) or state.jump(pos, vec)

            # jump mode
            elif state.action[0] == 2:
                pos = state.action[1]
                vec = Eximo.sel_mv_dir()
                n_state = state.jump(pos, vec)

            # capture mode
            elif state.action[0] == 3:
                pos = state.action[1]
                vec = Eximo.sel_cp_dir()
                n_state = state.capture(pos, vec)

            # place mode
            elif state.action[0] == 4:
                pos = Eximo.sel_cell()

                row = 2 if state.player == 2 else 8
                if pos[1] not in range(1, 8) or pos[0] not in range(row - 2, row) or not state.is_empty(pos):
                    continue

                n_state = state.place(pos)

        return n_state

    @staticmethod
    def minimax(state: State, depth: int, max_player: int, root: bool) -> State:
        
        if depth == 0:
            return state

        children = state.get_children()
        if len(children) == 0:
            return state

        if state.player == max_player:
            max_score = -1
            max_index = -1
            max_state = state
            
            for i, child in enumerate(children):
                n_state = Eximo.minimax(child, depth - 1, max_player, False)
                if n_state.score[max_player] > max_score:
                    max_score = n_state.score[max_player]
                    max_state = n_state
                    max_index = i
            if not root:
                return max_state
            else:
                return children[max_index]
        
        else:
            min_score = sys.maxsize
            min_state = state
            min_index = -1

            for i, child in enumerate(children):
                n_state = Eximo.minimax(child, depth - 1, max_player, False)
                if n_state.score[max_player] < min_score:
                    min_score = n_state.score[max_player]
                    min_state = n_state
                    min_index = i
            if not root:
                return min_state
            else:
                return children[min_index]

    # @staticmethod
    def minimax_prunning(self, state, depth, max_player, eval):
        if depth <= 0:
            return state

        better = lambda a, b: a > b if state.player == max_player else a < b
        best_score = -1 if state.player == max_player else sys.maxsize
        best_child = state

        for child in state.get_children():
            score = self.minimax_score(child, depth - 1, max_player, best_score, eval)
            if better(score, best_score):
                best_score = score
                best_child = child

        return best_child

    # @staticmethod
    def minimax_score(self, state, depth, max_player, parent_best, eval):
        if depth <= 0:
            # return state.score[max_player]
            self.children += 1
            return eval(state)
            # return available_moves(state)


        better = lambda a, b: a > b if state.player == max_player else a <= b
        best_score = -1 if state.player == max_player else sys.maxsize
        
        for child in state.get_children():
            score = self.minimax_score(child, depth - 1, max_player, best_score, eval)
            if better(score, parent_best): # abort early because this branch will not be picked
                self.cuts += 1
                return score
            if better(score, best_score):
                best_score = score

        return best_score
