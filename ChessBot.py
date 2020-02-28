import copy
import random
from datetime import datetime
import sys
import multiprocessing as mp


class ChessBot:

    def __init__(self,board):
        self.board = board
        self.RAMIFICATION_FACTOR = 50
        self.NUM_THREADS = 4

    class Node:
        def __init__(self, board, value):
            self.board=board
            self.value=value

    def evaluation(self, board):
        value = 0
        for pice in self.board.white_pices:
            value += pice.value
        for pice in self.board.black_pices:
            value -= pice.value
        return value

    def get_neightbor(self, new_board, side):
        current_board = copy.deepcopy(new_board)
        if side == 'white':
            pices = current_board.white_pices
        else:
            pices = current_board.black_pices
        random.seed(datetime.now())
        moves = pices[random.randint(0,len(pices)-1)].get_possible_moves(current_board.board)
        while moves==[]:
            moves = pices[random.randint(0,len(pices)-1)].get_possible_moves(current_board.board)
        move = moves[random.randint(0,len(moves)-1)]
        current_board.movePice(move)
        return current_board

    def bot_move(self):
        output = mp.Queue()
        
        def move_conc(output): 
            boards=[]  
            for j in range(self.RAMIFICATION_FACTOR):
                neightbor=self.get_neightbor(self.board,'black')
                boards.append(self.Node(neightbor,self.minimax(2, False, neightbor, -sys.maxsize, sys.maxsize)))
            output.put(min(boards, key = lambda t: t.value))
        
        processes=[mp.Process(target=move_conc, args=(output,), daemon = True) for i in range(self.NUM_THREADS)]
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        results = [output.get() for p in processes]
        return min(results, key = lambda t: t.value).board

    def minimax(self, depth, maxTurn, board, alpha, beta):
        current_board = copy.deepcopy(board)
        if depth == 0 or not current_board.check_kings_alive():
            return self.evaluation(current_board.board)
        if maxTurn:
            maxEval = -sys.maxsize
            for i in range(self.RAMIFICATION_FACTOR):
                eval = self.minimax(depth - 1, False, self.get_neightbor(current_board,'white'), alpha, beta)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval
        else:
            minEval = +sys.maxsize
            for i in range(self.RAMIFICATION_FACTOR):
                eval = self.minimax(depth - 1, True, self.get_neightbor(current_board,'black'), alpha, beta)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval