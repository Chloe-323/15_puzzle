from pynput import keyboard
from collections import deque
from os import sys
import heapq
import copy



#Non blocking keyboard input gets stored in the deque
keypresses = deque()
listener = keyboard.Listener(on_press=keypresses.append)
listener.start()



#Initialize the puzzle from a given file

class Puzzle:
    def __init__(self, initial, goal, keypresses):
        with open(initial) as f:
            try:
                self.board = [list(map(int, line.split())) for line in f]
                self.empty_slot = [(i,j) for i in range(4) for j in range(4) if self.board[i][j] == 0][0]
            except:
                print("Invalid puzzle file format for initial state. Please refer to the documentation for more information.")
                sys.exit(1)
        with open(goal) as f:
            try:
                self.goal_board = [list(map(int, line.split())) for line in f]
                self.goal_empty_slot = [(i,j) for i in range(4) for j in range(4) if self.goal_board[i][j] == 0][0]
            except:
                print("Invalid puzzle file format for goal state. Please refer to the documentation for more information.")
                sys.exit(1)
        #TODO: Check if the initial state is solvable
        self.keypresses = keypresses
        self.print()
        
    def check_if_goal(self):
        for i in zip(self.board, self.goal_board):
            if i[0] != i[1]:
                return False
        return(True)
        
    def print(self, board = None):
        if not board:
            board = self.board
        print()
        for i in board:
            for j in i:
                print("{0:2d}".format(j), end=' ')
            print()
        print()
            
    #Not the most efficient way to do this, but it lets us predict state changes without actually changing the state; this is necessary for the solver
    def _gen_output(self, board, empty_slot, deltas):
        new_board = copy.deepcopy(board)
        #Check no out of bounds error
        if deltas[0] + empty_slot[0] < 0 or deltas[0] + empty_slot[0] > 3 or deltas[1] + empty_slot[1] < 0 or deltas[1] + empty_slot[1] > 3:
            return None, None
        #Generate new board off of the old one
        board[empty_slot[0]][empty_slot[1]] = board[empty_slot[0]+deltas[0]][empty_slot[1]+deltas[1]]
        board[empty_slot[0]+deltas[0]][empty_slot[1]+deltas[1]] = 0
        empty_slot = (empty_slot[0]+deltas[0], empty_slot[1]+deltas[1])
        return board, empty_slot
    
    def play(self):
        while(1):
            if len(self.keypresses) != 0:
                keypress = self.keypresses.popleft()
                deltas = [0, 0]
                if keypress == keyboard.Key.up:
                    if self.empty_slot[0] == 0:
                        continue
                    deltas = [-1, 0]

                elif keypress == keyboard.Key.down:
                    if self.empty_slot[0] == 3:
                        continue
                    deltas = [1, 0]
                elif keypress == keyboard.Key.left:
                    if self.empty_slot[1] == 0:
                        continue
                    deltas = [0, -1]
                elif keypress == keyboard.Key.right:
                    if self.empty_slot[1] == 3:
                        continue
                    deltas = [0, 1]
                elif keypress == keyboard.KeyCode.from_char('s'):
                    print("Solving...")
                    self.solve()
                    continue
                else:
                    continue
                
                new_board, new_empty = self._gen_output(self.board, self.empty_slot, deltas)
                self.board = new_board
                self.empty_slot = new_empty
                self.print()
                if self.check_if_goal():
                    print("Congratulations! You solved the puzzle!")
                    sys.exit(0)            
    
    def solve(self):
        base_board = copy.deepcopy(self.board)
        frontier = []
        
        #TODO: Calculate chessboard distance
        def heuristic(board, goal_board):
            #Chessboard distance
            cbd = 0
            for i in board:
                for j in i:
                    pass
            return cbd
        print(heuristic(self.board, self.goal_board))
        
        #TODO: Make sure we don't generate duplicates
        def gen_moves(board, empty_slot, cost = 0, parent_seq = []):
            possible_deltas = [[-1, 0], [1, 0], [0, -1], [0, 1]]
            for i in range(4):
                this_board = copy.deepcopy(board)
                deltas = possible_deltas[i]
                output, out_empty = self._gen_output(this_board, empty_slot, deltas)
                if not output:
                    continue
                f = heuristic(output, self.goal_board) + cost + 1
                heapq.heappush(frontier, (f, output, out_empty, parent_seq + deltas))
        gen_moves(base_board, self.empty_slot)
        for i in frontier:
            print(i)
            
        #TODO: Implement Weighted A* search
        

if len(sys.argv) < 5:
    print("Usage: python3 15_puzzle.py -i <initial_state_file> -g <goal_state_file>")
    sys.exit(1)
    
puzzle = Puzzle(sys.argv[2], sys.argv[4], keypresses)
puzzle.play()