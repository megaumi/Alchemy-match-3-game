#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import pygame

class Game(object):
    def __init__(self, grid_size = 10):
        
        pygame.init()
        pygame.display.set_icon(pygame.image.load("images/icon.png"))
        self.screen = pygame.display.set_mode((1280, 1024), 0, 32)
        pygame.display.set_caption("Alchemy")
        #pygame.mouse.set_visible(False)
        
        self.grid_area = pygame.Surface((320,320))
        
        self.images = {}
        
        self.grid = [["0" for x in range(grid_size)] for y in range(grid_size)]
        self.images['cell_bg'] = pygame.image.load("images/cell.png").convert()

        #self.elements = ('mercury', 'saturn', 'jupiter', 'moon', 'venus', 'mars', 'sun')
        self.elements = ('mercury', 'saturn', 'jupiter', 'moon', 'venus')
        for element in self.elements:
            self.images[element] = pygame.image.load("images/%s.png" % element).convert()
        
        
        #self.colors = ('1', '2', '3', '4', '5', '6', '7')
        self.colors = ('1', '2', '3', '4', '5')
        self.figure_max_size = 4
        
        self.prev_pos = 0, 0
    
    def run(self):
        '''Game cycle'''
        while True:
            self.clock = pygame.time.Clock()
            # Show the grid
            self.show_grid()
            
            pygame.display.update((0,0, 320, 320))
            
            # Generate a new figure
            self.next_figure = self.get_next_figure()

            # Let the user rotate and place the figure
            row, col = self.place_figure()
                       
            # Find and destroy matches for every cell of the figure
            for rnum, c_row in enumerate(self.next_figure):
                for cnum, cell in enumerate(c_row):
                    if cell: self.handle_matches(row + rnum, col + cnum, cell)
       
    def show_grid(self):
        
        
        for rnum, row in enumerate(self.grid):
            for cnum, cell in enumerate(row):
                if cell == "0":
                    self.grid_area.blit(self.images['cell_bg'], (cnum * 32, rnum * 32))
                else:                    
                    self.grid_area.blit(self.images[self.elements[int(cell)-1]], (cnum * 32, rnum * 32))
        #self.screen.fill((0,0,0))
        self.screen.blit(self.grid_area, (0, 0))
        
        
    def get_next_figure(self):
        '''Generate a new figure'''
        
        # Based on size of the figure and number of rows get number of cols and empty cells.
        # FIXME: Sometimes this algorithm generates wrong polyominoes (with non-adjacent cells)
        size = random.randint(1, self.figure_max_size)
        rows = random.randint(1, size)
         
        if rows == size: cols = 1
        elif size == 4:
            if rows == 3: cols = 2
            elif rows == 2: cols = random.choice((2, 3))
            else: cols = 4
        elif size == 3:
            if rows == 2: cols = 2
            else: cols = 3
        elif size == 2: cols = 2
 
        empty = cols * rows - size
        
        next_figure = [["" for col in range(cols)] for row in range(rows)]
        
        # Generate cells (including empties) for the next figure and store them in a temporary array
        temp_arr = [random.choice(self.colors) for i in range(size)]
        temp_arr.extend([""] * empty)
        
        # Generate the next figure
        for row in range(rows):
            for col in range(cols):
                cell = random.choice(temp_arr)
                temp_arr.remove(cell)
                next_figure[row][col] = cell
        
        return next_figure
        
    def place_figure(self):
        '''Check if the figure can be placed on the grid using rotation and coords that user provides.
           In case of success place the figure to the grid and return its coords.'''
        
        # Check if every cell of the figure can be placed on the grid using the coordinates
        # that user provided. If any of the cells cannot be placed (the place is already taken or 
        # it's outside of the grid), user must provide new coords.

        def try_it(row, col, mouse):
            check_results = []
            self.show_grid()
            for rnum, c_row in enumerate(self.next_figure):
                for cnum, cell in enumerate(c_row):
                    if cell:
                        image = self.images[self.elements[int(cell)-1]].copy()
                    else: continue       # If the cell is '' it can be placed anywhere
                    
                    try:
                        if self.grid[row + rnum][col + cnum] == "0":
                            check_results.append(True)
                            image = self.images[self.elements[int(cell)-1]].copy()
                        else:
                            print "Oops! You are trying to place %s above %s in (%i, %i)!" %(cell, self.grid[row+rnum][col+cnum], row+rnum, col+cnum)
                            check_results.append(False)
                            image.fill((50, 50,50), None, pygame.BLEND_SUB)
                    except IndexError: 
                        print "Oops! You are trying to place %s to (%i, %i) which is outside of the grid!" %(cell, row+rnum, col+cnum)
                        check_results.append(False)
                        image.fill((50, 50, 50), None, pygame.BLEND_SUB)
                    if cell:
                        self.grid_area.blit(image, (mouse[0]+ cnum*32, mouse[1] + rnum*32))
                        self.screen.blit(self.grid_area, (0, 0))

            coords_checked = all(check_results)
            pygame.display.update((0,0,320,320))
            return coords_checked

        # Put every cell of the figure on the grid
        def put_it(row, col):
            for rnum, c_row in enumerate(self.next_figure):
                for cnum, cell in enumerate(c_row):
                    if cell: 
                        self.grid[row + rnum][col + cnum] = cell                        

        coords_checked = False
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    self.next_figure = zip(*self.next_figure[::-1])
                    self.show_grid()
                    for rnum, c_row in enumerate(self.next_figure):
                        for cnum, cell in enumerate(c_row):
                            if cell:                                
                                self.grid_area.blit(self.images[self.elements[int(cell)-1]], (event.pos[0]/32*32+ cnum*32, event.pos[1]/32*32 + rnum*32))
                                self.screen.blit(self.grid_area, (0, 0))
                    pygame.display.update()
                elif event.type == pygame.MOUSEBUTTONDOWN and coords_checked:
                    print "button: %i" %event.button
                    col, row = event.pos[0]/32, event.pos[1]/32
                    put_it(row, col)
                    return row, col
                if event.type == pygame.MOUSEMOTION:
                    if abs(self.prev_pos[0] - event.pos[0]) >= 16 or abs(self.prev_pos[1] - event.pos[1]) >= 16:
                        col, row = [i/32 for i in event.pos]
                        coords_checked = try_it(row, col, [i/32*32 for i in event.pos])
                        self.prev_pos = [i for i in event.pos]

        
    def handle_matches(self, row, col, cell):
        '''Find all matches with the current cell and destroy all matching cells'''
        
        def check_direction(row, col, dir, cell, counter, to_del_coords):
            '''Check the next cell in given direction. If it has the same color as the current cell,
            store its coords (to delete it later) and pass it to this function recursively
            with incremented counter'''
            
            n_row = row + dir[0]
            n_col = col + dir[1]            
            
            # We don't want to get outside of our grid
            if not (n_row < 0 or n_col < 0 or n_row >= len(self.grid) or n_col >= len(self.grid)):
                #print "I'm in (%i, %i), counter = %i, checking (%i, %i)..." %(row, col, counter, n_row, n_col)
                if self.grid[n_row][n_col] == cell:
                    to_del_coords.append([n_row, n_col])
                    counter += 1
                    #print "Found a cell of the same color, incrementing counter..."
                    counter, to_del_coords = check_direction(n_row, n_col, dir, cell, counter, to_del_coords)
            
            return counter, to_del_coords

        up = -1, 0
        down = 1, 0
        left = 0, -1
        right = 0, 1 
                
        match_found = False
        
        # Check adjacent cells in vertical direction (up, then down)
        counter = 0
        to_del_coords = []
       
        counter, to_del_coords = check_direction(row, col, up, cell, counter, to_del_coords)
        counter, to_del_coords  = check_direction(row, col, down, cell, counter, to_del_coords)

        if counter >= 2: 
            match_found = True
            for d_row, d_col in to_del_coords: self.grid[d_row][d_col] = "0"

        # Check adjacent cells in horizontal direction (left, then right)
        counter = 0
        to_del_coords = []

        counter, to_del_coords = check_direction(row, col, left, cell, counter, to_del_coords)
        counter, to_del_coords = check_direction(row, col, right, cell, counter, to_del_coords)

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
