#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, json, os.path, sys
import pygame

GRID_OFFSET = (500, 280)
NEXT_OFFSET = (20, 20)

class Game(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_icon(pygame.image.load(os.path.join("images","icon.png")))
        self.screen = pygame.display.set_mode((1024, 800), 0, 32)
        pygame.display.set_caption("Alchemy")
        
        self.update_rects = []
        
        self.images = {}
                
        self.load_level("level_1")
    
    @staticmethod
    def img_load(dir, file):
        return pygame.image.load(os.path.join(dir, file)).convert_alpha()        
    
    def load_level(self, level_id):
        level_file = open(os.path.join("levels", "level_1"), "r")
        level = json.loads(level_file.read())
        
        self.grid_size = 15
        self.figure_max_size = level["figure_max_size"]
        
        self.elements = {}
        
        for i, element in level["elements"].items():
            self.elements[int(i)] = element
            self.images[element] = self.img_load("images", element + ".png")
        
        self.images["bg_image"] = self.img_load("images", level["bg_image"])
        
        self.grid = [["0" for x in range(self.grid_size)] for y in range(self.grid_size)]

    def set_screen(self):
        self.images['grid'] = self.img_load("images", "grid.jpg")
        self.images['shadow'] = self.img_load("images", "shadow.png")
        
        self.screen.blit(self.images["bg_image"], (0,0))
        
        self.grid_area = self.images['grid'].copy()
        self.grid_area_rect = self.grid_area.get_rect(topleft = GRID_OFFSET)
        self.update_rects.append(self.grid_area_rect)
        self.show_grid()
        
        self.next_area = pygame.Surface((128, 128))
        self.update_rects.append(self.next_area.get_rect(topleft = NEXT_OFFSET))
        self.show_next()
        pygame.display.update()
                
    def run(self):
        '''Game cycle'''
        
        # Generate a new figure
        self.figure = self.get_next_figure()
        self.next_figure = self.get_next_figure()
        
        mouse_visible = True
        
        self.set_screen()
        self.clock = pygame.time.Clock()
        while True:
            
            self.clock.tick(60)

            event = pygame.event.poll()
            pygame.event.clear()
            
            if event.type == pygame.QUIT:
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.figure = zip(*self.figure[::-1])

                mouse = event.pos[0] - GRID_OFFSET[0], event.pos[1] - GRID_OFFSET[1]
                col, row = (mouse[0]+16)/32, (mouse[1]+16)/32
                coords_checked = self.check_place(row, col, mouse)
                            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and coords_checked:
                mouse = event.pos[0] - GRID_OFFSET[0], event.pos[1] - GRID_OFFSET[1]
                col, row = (mouse[0]+16)/32, (mouse[1]+16)/32
                self.place_figure(row, col, mouse)
                
            if event.type == pygame.MOUSEMOTION:
                # Mouse moved above the grid area
                if self.grid_area_rect.collidepoint(event.pos):
                    pygame.mouse.set_visible(False)
                    mouse_visible = False

                    mouse = event.pos[0] - GRID_OFFSET[0], event.pos[1] - GRID_OFFSET[1]
                    col, row = (mouse[0]+16)/32, (mouse[1]+16)/32
                    coords_checked = self.check_place(row, col, mouse)
                else:
                    if not mouse_visible:
                        pygame.mouse.set_visible(True)
                        mouse_visible = True
            
            pygame.display.update(self.update_rects)
    
    def update_screen(self):
        pass
    
    def show_next(self):
        self.next_area.fill((0,0,0))
        for rnum, c_row in enumerate(self.next_figure):
            for cnum, cell in enumerate(c_row):
                if cell:
                    self.next_area.blit(self.images[self.elements[int(cell)]], (cnum*32,rnum*32))
                    self.screen.blit(self.next_area, NEXT_OFFSET)

    def show_grid(self):
        '''Update screen in the grid area cell by cell'''
        for rnum, row in enumerate(self.grid):
            for cnum, cell in enumerate(row):
                if cell == "0":
                    self.grid_area.blit(self.images['grid'], (cnum * 32, rnum * 32), (cnum * 32, rnum * 32, 32, 32))
                else:                    
                    self.grid_area.blit(self.images[self.elements[int(cell)]], (cnum * 32, rnum * 32))
        self.screen.blit(self.grid_area, GRID_OFFSET)
        
        
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
        temp_arr = [random.choice(self.elements.keys()) for i in range(size)]
        temp_arr.extend([""] * empty)
        
        # Generate the next figure
        for row in range(rows):
            for col in range(cols):
                cell = random.choice(temp_arr)
                temp_arr.remove(cell)
                next_figure[row][col] = cell
 
        return next_figure
        
    def check_place(self, row, col, mouse):
        check_results = []
        figure_image = []
        self.show_grid()
        for rnum, c_row in enumerate(self.figure):
            for cnum, cell in enumerate(c_row):
                if cell:
                    cell_image = self.images[self.elements[int(cell)]].copy()
                else: continue       # If the cell is '' it can be placed anywhere
                
                try:
                    if self.grid[row + rnum][col + cnum] == "0":
                        check_results.append(True)
                        self.grid_area.blit(self.images['shadow'], ((col+cnum)*32, (row+rnum)*32))
                    else:
                        #print "Oops! You are trying to place %s above %s in (%i, %i)!" %(cell, self.grid[row+rnum][col+cnum], row+rnum, col+cnum)
                        check_results.append(False)
                        cell_image.fill((50, 50,50), None, pygame.BLEND_SUB)
                except IndexError: 
                    #print "Oops! You are trying to place %s to (%i, %i) which is outside of the grid!" %(cell, row+rnum, col+cnum)
                    check_results.append(False)
                    
                figure_image.append((cell_image, (mouse[0] + cnum*32, mouse[1] + rnum*32)))
        
        for cell in figure_image:
            self.grid_area.blit(*cell)
                
        self.screen.blit(self.grid_area, GRID_OFFSET)

        coords_checked = all(check_results)
        return coords_checked       

    def place_figure(self, row, col, mouse):
        # Update grid values
        for rnum, c_row in enumerate(self.figure):
            for cnum, cell in enumerate(c_row):
                if cell: 
                    self.grid[row + rnum][col + cnum] = cell
                   
        # Find and destroy matches for every cell of the figure
        for rnum, c_row in enumerate(self.figure):
            for cnum, cell in enumerate(c_row):
                if cell: self.handle_matches(row + rnum, col + cnum, cell)
        # Generate a new figure
        self.figure = self.next_figure
        self.next_figure = self.get_next_figure()
        
        # Update visuals
        self.show_next()
        self.check_place(row, col, mouse)

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
