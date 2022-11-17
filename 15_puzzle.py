from pynput import keyboard
from collections import deque
from os import sys
import heapq
import copy
import time
from rich.console import Console

console = Console()

#Non blocking keyboard input gets stored in a queue
keypresses = deque()
listener = keyboard.Listener(on_press=keypresses.append)
listener.start()

#Define board dimensions
board_width = 4
board_height = 4

#Initialize the puzzle from a given file

class Puzzle:
    def __init__(self, input_file, output_file, keypresses):
        """Initializes a puzzle from a given file

        Args:
            input_file (str): the location of the input file
            output_file (str, optional): the location of the output file
            keypresses (deque): the queue which contains the keypresses
        """
        self.board = [] #The 2D array that stores the current state
        self.empty_slot = None #The location of the empty slot within the current board
        self.goal_board = [] #The state that we are trying to reach
        self.output_file = output_file #The output file to write to; can be None for interactive mode
        self.keypresses = keypresses #The keypresses deque
        self.weight = 1.0
        
        #Read the input file
        with open(input_file) as f:
            i = 0 #line counter
            for line in f:
                if i == 0: #First line is the weight
                    self.weight = float(line)
                elif i > 1 and i < 6: #Second to fifth lines are the initial board
                    self.board.append([int(x) for x in line.split()])
                elif i > 6 and i < 11: #Seventh to tenth lines are the goal board
                    self.goal_board.append([int(x) for x in line.split()])
                i += 1
                
        #Find the empty slots
        self.empty_slot = [(i,j) for i in range(board_width) for j in range(board_height) if self.board[i][j] == 0][0]
#        self.goal_empty_slot = [(i,j) for i in range(board_width) for j in range(board_height) if self.goal_board[i][j] == 0][0]
        #TODO: Check if the initial state is solvable

        self.print()
    
    def _check_if_goal(self):
        """Helper function to check if the current board is the goal board

        Returns:
            bool: True if the current board is the goal board, False otherwise
        """
        for i in zip(self.board, self.goal_board):
            if i[0] != i[1]:
                return False
        return(True)
        
    def print(self, board = None):
        """Helper function to print the board

        Args:
            board (list[list[int]], optional): The board to print. If not included, will print the current state of the puzzle.
        """
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
        """Generates the result of performing a move on a given board

        Args:
            board (list[list[int]]): the board to perform the move on
            empty_slot (tuple(int, int)): the coordinates of the empty slot
            deltas (tuple(int, int)): the change in coordinates of the empty slot

        Returns:
            tuple(list[list[int]], tuple(int)): The resulting board and the coordinates of the empty slot
        """
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
        """Repeatedly takes in keypresses and performs the corresponding move on the board
        """
        watch = False
        while(1):
            if watch and not self.output_file:
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
                    watch = True
                    solution = self.solve()
                    for move in solution:
                        if move == (0, -1):
                            keypresses.append(keyboard.Key.left)
                        elif move == (0, 1):
                            keypresses.append(keyboard.Key.right)
                        elif move == (-1, 0):
                            keypresses.append(keyboard.Key.up)
                        elif move == (1, 0):
                            keypresses.append(keyboard.Key.down)
                    continue
                else:
                    continue
                
                new_board, new_empty = self._gen_output(self.board, self.empty_slot, deltas)
                self.board = new_board
                self.empty_slot = new_empty
                if not self.output_file:
                    self.print()
                if self._check_if_goal():
                    if not watch:
                        print("Congratulations! You solved the puzzle!")
                    sys.exit(0)            
    
    def solve(self):
        """Solves the puzzle using the Weighted A* algorithm

        Returns:
            list[tuple(int, int)]: a series of deltas (change in coordinates of the empty slot) to perform on the board to solve the puzzle
        """
        base_board = copy.deepcopy(self.board) #The starting board
        frontier = [] #A heap to keep track of the nodes to explore
        seen = set() #All states we've previously seen. This is done to avoid duplicates. Set is used for constant time find operations
        expanded = 1 #Counter for expanded nodes. Starts at 1 because we always expand the root node.
        
        #As per the assignment, heuristic is the chessboard distance
        def heuristic(board):
            """heuristic function that calculates the chessboard distance between the current board and the goal board

            Args:
                list[list[int]]: the board to assess

            Returns:
                int: the chessboard distance between the current board and the goal board
            """
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
        def gen_states(board, empty_slot, cost = 0, parent_seq = [], parent_seq_f = []):
            """Generates all states that are possible for a given board, and adds them to the frontier

            Args:
                board (list[list[int]]): the base state to generate states for
                empty_slot (tuple(int, int)): the empty slot of the board
                cost (int, optional): the cost to get to this point. Defaults to 0.
                parent_seq (list, optional): the sequence of moves to get to this point. Defaults to [].
                parent_seq_f (list, optional): the cost of each move to get to this point. Defaults to [].
            """

            for d in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                this_board = copy.deepcopy(board)
                deltas = d
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
                f = (self.weight * heuristic(output)) + cost + 1
                
                #Add this board to the frontier
                heapq.heappush(frontier, (f, cost + 1, output, out_empty, parent_seq + [deltas], parent_seq_f + [f]))
                
        #Generate the first set of moves
        gen_states(base_board, self.empty_slot)
        
        #Perform A* search
        solution = None
        psf = None
        while len(frontier) != 0:
            expanded += 1
            _, cost, result, result_empty, sequence, parent_seq_f = heapq.heappop(frontier)
            if result == self.goal_board:
                solution = sequence
                psf = parent_seq_f
                break
            gen_states(result, result_empty, cost, sequence, parent_seq_f)
        
        if not solution:
            print("No solution found")
            sys.exit(1)
        
        #Return solution if no output file (i.e. manual solve)
        if not self.output_file:
            return solution
        
        #Write to the output file if it's provided
        with open(self.output_file, 'w') as f:
            for i in self.board:
                for j in i:
                    f.write(str(j) + " ")
                f.write("\n")
            f.write("\n")
            for i in self.goal_board:
                for j in i:
                    f.write(str(j) + " ")
                f.write("\n")
            f.write("\n")
            f.write(str(self.weight) + "\n")
            f.write(str(len(solution)) + "\n") #depth
            f.write(str(expanded) + "\n") #nodes expanded
            for move in solution:
                if move == (0, -1):
                    f.write("L ")
                elif move == (0, 1):
                    f.write("R ")
                elif move == (-1, 0):
                    f.write("U ")
                elif move == (1, 0):
                    f.write("D ")
            f.write("\n")
            for f_value in psf:
                f.write(str(f_value) + " ")
        return solution
        

if len(sys.argv) < 2:
    print(f"Usage: python3 {sys.argv[0]} <input_file> [-s <output_file>]")
    exit(1)
    
out_file = None
if '-s' in sys.argv:
    keypresses.append(keyboard.KeyCode.from_char('s'))
    out_file = sys.argv[-1]
    
puzzle = Puzzle(sys.argv[1], out_file, keypresses)
puzzle.play()
