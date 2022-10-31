from pynput import keyboard
from collections import deque
from os import sys
import heapq



#Non blocking keyboard input gets stored in the deque
keypresses = deque()
listener = keyboard.Listener(on_press=keypresses.append)
listener.start()



#Initialize the puzzle from a given file

class Puzzle:
    def __init__(self, filename, keypresses):
        with open(filename) as f:
            try:
                self.board = [list(map(int, line.split())) for line in f]
                self.empty_slot = [(i,j) for i in range(4) for j in range(4) if self.board[i][j] == 0][0]
            except:
                print("Invalid puzzle file format. Please refer to the documentation for more information.")
                sys.exit(1)
        self.keypresses = keypresses
        self.print()
        
    def print(self):
        print()
        for i in self.board:
            for j in i:
                print("{0:2d}".format(j), end=' ')
            print()
        print()
            
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
                elif keypress == 's':
                    pass
                self.board[self.empty_slot[0]][self.empty_slot[1]] = self.board[self.empty_slot[0]+deltas[0]][self.empty_slot[1]+deltas[1]]
                self.board[self.empty_slot[0]+deltas[0]][self.empty_slot[1]+deltas[1]] = 0
                self.empty_slot = (self.empty_slot[0]+deltas[0], self.empty_slot[1]+deltas[1])
                self.print()
    
    def solve(self):
        pass
        

if len(sys.argv) < 2:
    print("Usage: python3 15_puzzle.py -f <puzzle_file>")
    sys.exit(1)
    
puzzle = Puzzle(sys.argv[2], keypresses)
puzzle.play()