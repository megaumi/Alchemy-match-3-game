#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

class Game(object):
    def __init__(self, grid_size = 10):
        self.grid = [["0" for x in range(grid_size)] for y in range(grid_size)]
        self.colors = ["■", "□", "◆"]
        self.figure_max_size = 4
        
    def run(self):
        while True:
            self.next_figure = self.get_next_figure()
            row, col = self.get_user_input()
            
            for c_row, c_col, cell_color in self.next_figure: 
                self.grid[row + c_row][col + c_col] = cell_color
            for c_row, c_col, cell_color in self.next_figure:
                self.handle_matches(row + c_row, col + c_col, cell_color)
            
            for row in self.grid: print " ".join(row)
            
    def get_next_figure(self):
        '''Generate new figure and show it to user'''
        
        next_figure = [] 
        
        # Based on size of the figure and number of rows get number of cols and empty cells.
        # FIXME: Sometimes this algorithm generates wrong polyominoes (with non-adjacent cells)
        size = random.randint(1, self.figure_max_size)
        rows = random.randint(1, size)
        
        if rows == size: cols = 1
        elif size == 4:
            if rows == 3: cols = 2
            elif rows == 2: cols = 3
            else: cols = 4
        elif size == 3:
            if rows == 2: cols = 2
            else: cols = 3
        elif size == 2: cols = 2
            
        empty = cols * rows - size
        
        print size, rows, cols, empty
        
        # Generate colors (including empties) for next figure and store them in a temporary array
        temp_arr = [random.choice(self.colors) for i in range(size)]
        for i in range(empty): temp_arr.append("")
        
        # Generate next figure
        for row in range(rows):
            for col in range(cols):
                cell_color = random.choice(temp_arr)
                temp_arr.remove(cell_color)
                if cell_color: next_figure.append((row, col, cell_color))
        
        #next_figure = [(row, col, temp_arr.pop(random.randrange(0,len(temp_arr)))) for col in range(cols) for row in range(rows)]
                
        # Represent next figure in nice human-readable form
        repr_figure = [[" " for col in range(cols)] for row in range(rows)]
        
        for row, col, cell_color in next_figure:
            repr_figure[row][col] = cell_color
            
        print "Figure:"
        for row in repr_figure: print " ".join(row)
        
        return next_figure
        
    def get_user_input(self):
        row, col = [int(var) for var in raw_input("\nInput coords: ")]
        return row, col
        
    def handle_matches(self, row, col, cell_color):
        '''Find all matches with current cell and destroy all matching cells'''
        
        def check_direction(row, col, dir, cell_color, counter, to_del_coords):
            '''Check next cell in given direction. If it has same color as current cell,
            store its coords (to delete it later) and pass it to this function recursively
            with incremented counter'''
            
            n_row = row + dir[0]
            n_col = col + dir[1]            
            
            # We don't want to get outside of our grid
            if not (n_row < 0 or n_col < 0 or n_row >= len(self.grid) or n_col >= len(self.grid)):
                #print "I'm in (%i, %i), counter = %i, checking (%i, %i)..." %(row, col, counter, n_row, n_col)
                if self.grid[n_row][n_col] == cell_color:
                    to_del_coords.append([n_row, n_col])
                    counter += 1
                    #print "Found a cell of the same color, incrementing counter..."
                    counter, to_del_coords = check_direction(n_row, n_col, dir, cell_color, counter, to_del_coords)
            
            return counter, to_del_coords

        up = -1, 0
        down = 1, 0
        left = 0, -1
        right = 0, 1 
                
        match_found = False
        
        # Check adjacent cells in vertical direction (up, then down)
        counter = 0
        to_del_coords = []
       
        counter, to_del_coords = check_direction(row, col, up, cell_color, counter, to_del_coords)
        counter, to_del_coords  = check_direction(row, col, down, cell_color, counter, to_del_coords)

        if counter >= 2: 
            match_found = True
            for d_row, d_col in to_del_coords: self.grid[d_row][d_col] = "0"

        # Check adjacent cells in horizontal direction (left, then right)
        counter = 0
        to_del_coords = []

        counter, to_del_coords = check_direction(row, col, left, cell_color, counter, to_del_coords)
        counter, to_del_coords = check_direction(row, col, right, cell_color, counter, to_del_coords)

        if counter >= 2: 
            match_found = True
            for d_row, d_col in to_del_coords: self.grid[d_row][d_col] = "0"         
        
        # If there was a match, destroy the cell itself
        if match_found: 
            print "!" * 17 + "Yay! Match found!" + "!" * 17
            self.grid[row][col] = "0"
            
def main():
	
    game = Game()
    game.run()
    
if __name__ == '__main__':
	main()
