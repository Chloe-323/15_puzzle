# 15_puzzle
The 15 Puzzle Project for CS-UY 4613

# Puzzle Overview

The 15-puzzle is defined by a 4x4 grid of numbers, ranging from 1-15, and one empty slot, represented by a 0:
![15 puzzle](https://d1s2pua8v98dyj.cloudfront.net/mk/images/p312500b_2x.jpg)

```
 0  4  9 12 
 1  7 10  6 
15  5  3  2 
13 11 14  8
```

The goal is to move from the initial state to the goal state by sliding tiles into the empty slot, effectively swapping the empty slot with the tile.

Tiles can be slid up, down, left, or right, provided they are going into the empty slot.

# Program usage overview

The program represents the 15-puzzle with a 2d array of numbers, and represents the empty slot with a 0.

To use the program, you must first install the following dependencies:

## Python
- Windows: https://www.python.org/downloads/windows/
- Mac: https://www.python.org/downloads/macos/
- Debian-based distros: `sudo apt-get install python3 python3-pip`
- Arch-based distros: `sudo pacman -S python python-pip`

## Pip dependencies
- `pip install pynput rich`

# Usage
It is necessary to define an initial state and a final state, as well as a weight (to be discussed later) in an input file. The input file should be formatted as follows:

```
W

n n n n
n n n n
n n n n
n n n n

m m m m
m m m m
m m m m 
m m m m 
```

Where `W` is the weight, the grid of `n`s is the initial state, and the grid of `m`s is the final state. A number of sample input files are included.

## Interactive mode
To run the program in interactive mode (where you can play the puzzle), simply run `python 15_puzzle.py <input_file>` from a terminal. The commands for the interactive mode are defined below:

### Interactive Mode Controls:
- ⬅ Move left
- ➡ Move right
- ⬆ Move up
- ⬇ Move down
- S solve from here

## Solve mode
It is also possible to run the program in solve mode, where it will immediately solve the given input state and will not show the solution. Moreover, it will create an output file of the following format:

```
n n n n
n n n n
n n n n
n n n n

m m m m
m m m m
m m m m
m m m m

W
d
n
<Move list>
<Function cost for each move>
```

Where the grid of `n`s is the initial state, the grid of `m`s is the final state, `W` is the weight, `d` is the length of the solution, i.e. the depth of the solution node in the tree (discussed later), `n` is the number of expanded nodes, `move list` is a list of moves to solve the puzzle, where each move is one of `U` for up, `D` for down, `L` for left, and `R` for right. Finally, `function cost for each node` is the total computed cost (path + heuristic; discussed later) for each executed move.

To run the program in solve mode (to produce a gradeable output file, for example), you can use `python 15_puzzle.py <input_file> -s <output_file>`, where output_file will be the file that the described output will be written to.

# Implementation
We implement this using a weighted A* algorithm

## A*
The A* algorithm is used to find the optimal path from a given initial node to the solution node. It is a **heuristic best-first search algorithm**. A searching algrithm will run the following basic pseudocode

```
frontier = [options from initial state]
while options in frontier:
 current_option <- frontier
 if current option is goal:
  return
 for option stemming from current_option:
  frontier <- option
```
This will define a tree: a the initial node will spawn a number of child nodes, and each of those has their own child nodes that stem from them. This can be visualized as such:
```
  o <- parent (depth 0)
 / \
o   o <- children (depth 1)
   / \
  o   o <- children of child (depth 2)
 / \   \
o   o   o <- children of depth 3
 \ / \ /
 ....... <- tree continues on
```

Different searching algorithms will implement different datastructures for the frontier and `option`: namely, depth-first search will implement a stack, breadth-first search will implement a queue, and best-first will use a heap.

A heap is a special datastructure that is **self-sorting**. This means that insert operations are O(log(n)), but getting the smallest element is O(1). This is useful because we can access, in constant time, the option with the lowest cost.

To calculate the cost and be able to put cheaper nodes first, different algorithms can be used. The A* algorithm defines the cost function as follows:
```
f(x) = h(x) + g(x)
```
where `x` is the current node, `f` is the cost function, `h` is a heuristic function to make an educated guess, in constant time, as to how good the given node is. A better node will have a lower cost. `g` is the cost to get from the initial state to `x`.

A* Will always find the best option, but it may take a while and explore a lot of nodes. To use it, it is necessary to have a good heuristic function.

## Weighted A*
Weighted A* is a variant of A* where the heuristic function is assigned a weight that is greater than 1. As such, its cost function takes the following form:
```
f(x) = W * h(x) + g(x)
```
Where `W` is the weight that is greater than 1. This will significantly cut down the number of nodes explored, and thus speed up the algorithm, but at the cost of returning a sub-optimal result.

## 15-Puzzle Weighted A*
The solving algorithm uses weighted A*, taking in the weight through the input file, and using chessboard distance as the heuristic function. The chessboard distance is defined as follows:
```
h(x) = (max(vertical distance to goal, horizontal distance to goal))
```
By adding up the chessboard distance for each tile, we can get the heuristic function for the entire board. Then, we use the A* algorithm, which will prefer boards that are more similar to the correct solution, in order to find the series of moves that will solve the puzzle.

# Code overview
The puzzle class defines 6 methods that are used to run the puzzle:
- `def __init__(self, input_file, output_file, keypresses)`
- `def check_if_goal(self)`
- `def print(self)`
- `def _gen_output(self, board, empty_slot, deltas)`
- `def play(self)`
- `def solve(self)`

## `__init__`:
This method loads data from the input and output files to initialize the data for the class. It defines the following class variables:
- `self.board` - The current state
- `self.empty_slot` - The empty slot of the current state, used for similicity of code later on
- `self.goal_board` - The goal state; if the board reaches this state then it is solved
- `self.output_file` - Only used if run in solve mode; will output the solution to the output file; also used as an indicator that we are in fact in solve mode
- `self.keypresses` - The keypresses queue. Used to process user inputs in interactive mode; also used to store commands when solving the puzzle
- `self.weight` - The weight for the solver algorithm

## `check_if_goal`:
This is a helper method that checks if the current state is equal to the goal state.

## `print`:
This is a helper function that prints the current state

## `_gen_output`:
This is a helper function that predicts the output given a hypothetical board and a delta. The delta is the relative location that the empty slot will swap with. It is defined as `[-1, 0]` if the direction is **up**, `[1, 0]` if the direction is **down**, `[0, -1]` if the direction is **left**, and `[0, 1]` if the direction is **right**.

## `play`:
This is the main gameplay loop. If the output file is defined (i.e. we are in solve mode), then it will immediately call the solve method. If not, then it will read keypresses and change the board accordingly. Every iteration, it prints the current state using `rich.Console` to be able to highlight the empty slot in red for easier visibility.

## `solve`:
This is the actual implementation of the Weighted A* algorithm. It defines two helper functions: `heuristic` and `gen_states`. 

- `heuristic` calculates the sum of the chessboard distances for a given state as discussed above, and returns a score for that state. A lower score represents a more favorable position.
- `gen_states` takes an input state and generates all the output states that can be reached in one move. It calculates their score and then inserts them into the frontier.

The `frontier` is defined as a min-heap as discussed above, and contains all unexplored nodes. Each entry in the heap is a tuple with the following structure:
```
(f, length to get here, state, state_empty_slot, parent sequence, parent sequence costs)
```
Where `f` is the cost function (it is used first so that the heap will sort nodes by this value), `length to get here` is the number of moves required to reach this state, `state` and `state_empty_slot` represent the state we are defining and its empty slot, `parent sequence` is the sequence of moves to get to this state, and `parent sequence costs` is the cost of the `f` for each move to get to this state.

There is also a set `seen`, which stores all states that have been visited. This is used to avoid looking at duplicates states and getting caught in loops, and it is a set due to its O(1) lookup function, which can tell us if a given state has been seen before in constant time. To add something to a set, it must be *hashable*, meaning that every list must be converted into a tuple. 

The actual algorithm will follow the pseudocode defined previously, and pasted again here for legibility:
```
frontier = [options from initial state]
while options in frontier:
 current_option <- frontier
 if current option is goal:
  return
 for option stemming from current_option:
  frontier <- option
```

Once a solution is found, it will return it, optionally writing to the output file first.

# Full code

We are required to copy-paste the entire code into this file, so here it is:
```
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

```
