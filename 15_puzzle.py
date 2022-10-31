from pynput import keyboard
from collections import deque
from os import sys
import heapq
import copy
import time
from rich.console import Console

console = Console()

#Non blocking keyboard input gets stored in the deque
keypresses = deque()
listener = keyboard.Listener(on_press=keypresses.append)
listener.start()

board_width = 4
board_height = 4

#Initialize the puzzle from a given file

class Puzzle:
    def __init__(self, initial, goal, keypresses):
        with open(initial) as f:
            try:
                self.board = [list(map(int, line.split())) for line in f]
                self.empty_slot = [(i,j) for i in range(board_width) for j in range(board_height) if self.board[i][j] == 0][0]
            except:
                print("Invalid puzzle file format for initial state. Please refer to the documentation for more information.")
                sys.exit(1)
        with open(goal) as f:
            try:
                self.goal_board = [list(map(int, line.split())) for line in f]
                self.goal_empty_slot = [(i,j) for i in range(board_width) for j in range(board_height) if self.goal_board[i][j] == 0][0]
            except:
                print("Invalid puzzle file format for goal state. Please refer to the documentation for more information.")
                sys.exit(1)
        #TODO: Check if the initial state is solvable
        self.keypresses = keypresses
        self.watch = False
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
                if j == 0:
                    console.print('[bold red] 0[/bold red]', end=' ')
                else:
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
            if self.watch:
                time.sleep(1)
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
                    self.watch = True
                    solution = self.solve()
                    translated_moves = []
                    for move in solution:
                        if move == (0, -1):
                            translated_moves.append("left")
                            keypresses.append(keyboard.Key.left)
                        elif move == (0, 1):
                            translated_moves.append("right")
                            keypresses.append(keyboard.Key.right)
                        elif move == (-1, 0):
                            translated_moves.append("up")
                            keypresses.append(keyboard.Key.up)
                        elif move == (1, 0):
                            translated_moves.append("down")
                            keypresses.append(keyboard.Key.down)
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
        seen = set()
        
        #As per the assignment, heuristic is the chessboard distance
        def heuristic(board):
            #Chessboard distance
            cbd = 0
            cur_locations = {}  #Map of current locations of each number
            goal_locations = {} #Map of goal locations of each number
            for i in range(board_width):
                for j in range(board_height):
                    number = board[i][j]
                    cur_locations[number] = (i, j)
                    number = self.goal_board[i][j]
                    goal_locations[number] = (i, j)
            
            for i in range(board_width*board_height):
                cbd += max(abs(cur_locations[i][0] - goal_locations[i][0]), abs(cur_locations[i][1] - goal_locations[i][1])) #Chessboard distance is defined as the maximum of the x and y distances between the two points
            return cbd
        
        #Generate moves and add them to the frontier
        def gen_moves(board, empty_slot, cost = 0, parent_seq = []):
            possible_deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for i in range(4):
                this_board = copy.deepcopy(board)
                deltas = possible_deltas[i]
                output, out_empty = self._gen_output(this_board, empty_slot, deltas)
                
                #If we can't move in this direction, skip it
                if not output:
                    continue
                
                #If we've already seen this board, skip it
                hashable_output  = tuple(tuple(i) for i in output)
                if hashable_output in seen:
                    continue
                seen.add(hashable_output)
                
                #Calculate f as g(n) + h(n) -> cost + heuristic
                f = heuristic(output) + cost + 1
                
                #Add this board to the frontier
                heapq.heappush(frontier, (f, cost + 1, output, out_empty, parent_seq + [deltas]))
                
        #Generate the first set of moves
        gen_moves(base_board, self.empty_slot)
        
        #Perform A* search
        while len(frontier) != 0:
            _, cost, result, result_empty, sequence = heapq.heappop(frontier)
            if result == self.goal_board:
                return sequence
            gen_moves(result, result_empty, cost, sequence)
        return None #No solution found
        

if len(sys.argv) < 5:
    print("Usage: python3 15_puzzle.py -i <initial_state_file> -g <goal_state_file>")
    sys.exit(1)
    
puzzle = Puzzle(sys.argv[2], sys.argv[4], keypresses)
puzzle.play()