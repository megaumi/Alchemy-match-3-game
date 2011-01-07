#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Game(object):
    def __init__(self):
        self.grid = [["0" for x in range(10)] for y in range(10)]
        
    def run(self):
        while True:
            row, col = self.input()
            self.grid[row][col] = "."
            self.calculate(row, col)
            for row in self.grid: print " ".join(row)
        
    def input(self):
        row, col = [int(var) for var in raw_input()]
        return row, col
        
    def calculate(self, row, col):
        
        def check_direction(row, col, dir, counter, to_del_coords):
            nrow = row + dir[0]
            ncol = col + dir[1]
            if not (nrow < 0 or ncol < 0 or nrow >= len(self.grid) or ncol >= len(self.grid)):
                print "I'm in %i, %i, counter is %i, checking (%i, %i)" %(row, col, counter, dir[0], dir[1])
                if self.grid[nrow][ncol] == ".":
                    to_del_coords.append([nrow, ncol])
                    counter += 1
                    print "found same, incrementing counter"
                    counter, to_del_coords = check_direction(nrow, ncol, dir, counter, to_del_coords)
            
            return counter, to_del_coords

        up = -1, 0
        down = 1, 0
        left = 0, -1
        right = 0, 1 
                
        match_found = False

        counter = 0
        to_del_coords = []
       
        counter, to_del_coords = check_direction(row, col, up, counter, to_del_coords)
        counter, to_del_coords  = check_direction(row, col, down, counter, to_del_coords)

        if counter >= 2: 
            match_found = True
            for drow, dcol in to_del_coords: self.grid[drow][dcol] = "0"

        counter = 0
        to_del_coords = []

        counter, to_del_coords = check_direction(row, col, left, counter, to_del_coords)
        counter, to_del_coords = check_direction(row, col, right, counter, to_del_coords)

        if counter >= 2: 
            match_found = True
            for drow, dcol in to_del_coords: self.grid[drow][dcol] = "0"         
        
        if match_found: self.grid[row][col] = "0"
            
def main():
	
    game = Game()
    game.run()
    
if __name__ == '__main__':
	main()
