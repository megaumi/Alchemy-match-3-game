#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import json
import os.path
import sys
import pygame

GRID_OFFSET = (280, 180)
NEXT_OFFSET = (20, 20)
ELEMENTS = {
    "1": "mercury",
    "2": "saturn",
    "3": "jupiter",
    "4": "moon",
    "5": "venus",
    "6": "mars",
    "7": "sun",
    "1s": "mercury_spoilt",
    "2s": "saturn_spoilt",
    "3s": "jupiter_spoilt",
    "5s": "venus_spoilt",
    "6s": "mars_spoilt",
    "o": "old"
    }

class Game(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_icon(pygame.image.load(os.path.join("images","icon.png")))
        self.screen = pygame.display.set_mode((1024, 800), 0, 32)
        pygame.display.set_caption("Alchemy")
        
        self.update_rects = []
        
        
        self.load_resources()
        self.main_menu()
        self.load_game_screen()
    
    def main_menu(self):
        self.levels = [1,2,3]
        self.locked_levels = self.levels[1:]

    
    def load_game_screen(self):
        
        self.screen.fill((50,50,50))
        for i in self.levels: self.screen.blit(self.images['level_%i' %i], (400, 150 + i*100))
        level_images = [self.images['level_%i' %i] for i in self.levels]
        self.clock = pygame.time.Clock()
        while True:
            self.clock.tick(60)
            event = pygame.event.poll()
            pygame.event.clear()
            
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, image in enumerate(level_images):
                    if image.get_rect(topleft = (400, 150 + (i+1)*100)).collidepoint(event.pos):
                        if not i+1 in self.locked_levels:
                            won = self.load_level("level_%i" %(i+1))
                            if won and (i+2 in self.locked_levels):
                                print "here"
                                self.locked_levels.remove(i+2)
                            self.load_game_screen()
                        else: print "This level is blocked!"
        
            pygame.display.update()
    
    @staticmethod
    def img_load(dir, file):
        return pygame.image.load(os.path.join(dir, file)).convert_alpha()        
    
    def load_resources(self):
        self.images = {}
        self.images['grid'] = self.img_load("images", "grid.jpg")
        self.images['shadow'] = self.img_load("images", "shadow.png")
        self.images['border'] = self.img_load("images", "border.png")
        self.images['grid_border'] = self.img_load("images", "grid_border.png")
        for element in ELEMENTS.values():
            self.images[element] = self.img_load("images", element + ".png")
        self.images['level_1'] = self.img_load("images", "level_1.png")
        self.images['level_2'] = self.img_load("images", "level_2.png")
        self.images['level_3'] = self.img_load("images", "level_3.png")
    
    def load_level(self, level_id):
        level_file = open(os.path.join("levels", level_id), "r")
        level = json.loads(level_file.read())
        
        self.grid_size = 15
        self.figure_max_size = level["figure_max_size"]
        
        self.elements = level["elements"]
        self.spoilt = level["spoilt"]
        self.locked = level["locked"]
        
        self.goal = level["goal"]
        
        self.images["bg_image"] = self.img_load("images", level["bg_image"])
        
        self.grid = [[str(cell) for cell in row] for row in level["field"]]
        now = pygame.time.get_ticks()/1000
        
        self.timer_grid = [[0 for cell in row ] for row in level["field"]]
        
        for rnum, row in enumerate(self.grid):
            for cnum, cell in enumerate(row):
                if cell <> "0" and cell <> "4" and cell <> "7":
                    self.timer_grid[rnum][cnum] = now + 60
        return self.run_level()
        

    def set_screen(self):        
        self.screen.blit(self.images["bg_image"], (0,0))
        self.screen.blit(self.images['grid_border'], (GRID_OFFSET[0]-32, GRID_OFFSET[1]-32))
        
        self.grid_area = self.images['grid'].copy()
        self.grid_area_rect = self.grid_area.get_rect(topleft = GRID_OFFSET)
        self.update_rects.append(self.grid_area_rect)
        self.show_grid()
        
        
        self.next_area = pygame.Surface((128, 128))
        self.update_rects.append(self.next_area.get_rect(topleft = NEXT_OFFSET))
        self.show_next()
        
        pygame.display.update()
                
    def run_level(self):
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not mouse_visible:
                        pygame.mouse.set_visible(True)
                        mouse_visible = True
                    return
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if self.grid_area_rect.collidepoint(event.pos):
                    # Right mouse click rotates the figure
                    self.figure = zip(*self.figure[::-1])
                    row, col, mouse = self.get_row_col(event.pos)
                    coords_checked = self.check_place(row, col, mouse)
                            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.grid_area_rect.collidepoint(event.pos) and coords_checked:
                    # Left mouse click places the figure
                    row, col, mouse = self.get_row_col(event.pos)
                    self.place_figure(row, col, mouse)
                    coords_checked = self.check_place(row, col, mouse)
                
            if event.type == pygame.MOUSEMOTION:
                # Mouse moved above the grid area
                if self.grid_area_rect.collidepoint(event.pos):
                    pygame.mouse.set_visible(False)
                    mouse_visible = False
                    row, col, mouse = self.get_row_col(event.pos)
                    coords_checked = self.check_place(row, col, mouse)
                else:
                    self.show_grid()
                    if not mouse_visible:
                        pygame.mouse.set_visible(True)
                        mouse_visible = True
            self.age_metal()
            pygame.display.update(self.update_rects)
            
            if not self.goal:
                if not mouse_visible:
                    pygame.mouse.set_visible(True)
                    mouse_visible = True
                return True
    
    def age_metal(self):
        changed = False
        now = pygame.time.get_ticks()/1000
        for rnum, row in enumerate(self.timer_grid):
            for cnum, cell in enumerate(row):
                if cell and cell <= now:
                    if self.grid[rnum][cnum][-1] <> "s" and self.grid[rnum][cnum] <> "o":
                        self.grid[rnum][cnum] = self.grid[rnum][cnum] + "s"
                        self.timer_grid[rnum][cnum] = now + 60
                    else:
                        self.grid[rnum][cnum] = "o"
                        self.timer_grid[rnum][cnum] = 0
                    changed = True
        if changed: self.show_grid()
    
    @staticmethod
    def get_row_col(pos):
        '''Transform absolute mouse coordinates into grid-relative
           and return respective row and column numbers'''
        mouse = pos[0] - GRID_OFFSET[0], pos[1] - GRID_OFFSET[1]
        col, row = (mouse[0]+16)/32, (mouse[1]+16)/32
        return row, col, mouse
    
    def update_screen(self):
        pass
    
    def show_next(self):
        self.next_area.fill((0,0,0))
        for rnum, c_row in enumerate(self.next_figure):
            for cnum, cell in enumerate(c_row):
                if cell:
                    self.next_area.blit(self.images[ELEMENTS[cell]], (cnum*32,rnum*32))
                    self.screen.blit(self.next_area, NEXT_OFFSET)

    def show_grid(self):
        '''Update screen in the grid area cell by cell'''
        for rnum, row in enumerate(self.grid):
            for cnum, cell in enumerate(row):
                if cell == "0":
                    self.grid_area.blit(self.images['grid'], (cnum * 32, rnum * 32), (cnum * 32, rnum * 32, 32, 32))
                elif cell == "b":
                    self.grid_area.blit(self.images["border"], (cnum * 32, rnum * 32))
                else:                    
                    self.grid_area.blit(self.images[ELEMENTS[cell]], (cnum * 32, rnum * 32))
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
        temp_arr = [random.choice(self.elements) for i in range(size)]
        for i, element in enumerate(temp_arr):
            if element in self.spoilt:
                temp_arr[i] = random.choice((element, element+"s"))
        temp_arr.extend([""] * empty)
        
        # Generate the next figure
        for row in range(rows):
            for col in range(cols):
                cell = random.choice(temp_arr)
                temp_arr.remove(cell)
                next_figure[row][col] = cell
        
        return next_figure
        
    def check_place(self, row, col, mouse):
        '''Update the grid area, show shadow under the figure, darken cells
           that cannot be placed, blit figure image on the grid area and
           return True if the figure can be placed in current position.
           Obviously this should be refactored.'''
        check_results = []
        figure_image = []
        self.show_grid()
        for rnum, c_row in enumerate(self.figure):
            for cnum, cell in enumerate(c_row):
                if cell:
                    cell_image = self.images[ELEMENTS[cell]].copy()
                else: continue       # No need to check an empty cell
                try:
                    if self.grid[row + rnum][col + cnum] == "0":
                        check_results.append(True)
                        self.grid_area.blit(self.images['shadow'], ((col+cnum)*32, (row+rnum)*32))
                    else:
                        check_results.append(False)
                        cell_image.fill((50, 50,50), None, pygame.BLEND_SUB)
                except IndexError:
                    check_results.append(False)
                 # We don't blit the figure cell by cell, but create a list
                # of cell images instead, in order to blit them all at once later.
                # Otherwise cell images will be overlapped by shadow images.
                figure_image.append((cell_image, (mouse[0] + cnum*32, mouse[1] + rnum*32)))
        # Now we blit the figure to the grid area an blit the grid area to the screen
        for cell in figure_image:
            self.grid_area.blit(*cell)
        self.screen.blit(self.grid_area, GRID_OFFSET)

        coords_checked = all(check_results)
        return coords_checked       

    def place_figure(self, row, col, mouse):
        '''Add new values to the grid, handle matches for new values, generate
           the next figure and show it in the next_area'''
        # Update grid values
        for rnum, c_row in enumerate(self.figure):
            for cnum, cell in enumerate(c_row):
                if cell: 
                    self.grid[row + rnum][col + cnum] = cell
                    if cell <> "4" and cell <> "7":
                        self.timer_grid[row + rnum][col + cnum] = pygame.time.get_ticks()/1000 + 60
                    
        # Find and destroy matches for every cell of the figure
        for rnum, c_row in enumerate(self.figure):
            for cnum, cell in enumerate(c_row):
                if cell: self.handle_matches(row + rnum, col + cnum, cell)
                
        # Generate a new figure
        self.figure = self.next_figure
        self.next_figure = self.get_next_figure()
        
        # Update visuals
        self.show_next()

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
                # If the last character is "l" (which indicates a locked cell)
                # then there's no match for sure
                if self.grid[n_row][n_col][-1] == "l" or cell[-1] == "l":
                    return counter, to_del_coords
                # We compare only the first character, so that "1" and "1s"
                # (which are mercury and spoilt mercury) will make a match
                if self.grid[n_row][n_col][0] == cell[0]:
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
            if cell[0] in self.goal:
                self.goal[cell[0]] -=1
                if self.goal[cell[0]] == 0: self.goal.pop(cell[0])
            for d_row, d_col in to_del_coords: 
                self.grid[d_row][d_col] = "0"
                self.timer_grid[d_row][d_col] = 0

        # Check adjacent cells in horizontal direction (left, then right)
        counter = 0
        to_del_coords = []

        counter, to_del_coords = check_direction(row, col, left, cell, counter, to_del_coords)
        counter, to_del_coords = check_direction(row, col, right, cell, counter, to_del_coords)

        if counter >= 2: 
            match_found = True
            if cell[0] in self.goal:
                self.goal[cell[0]] -=1
                if self.goal[cell[0]] == 0: self.goal.pop(cell[0])
            for d_row, d_col in to_del_coords:
                self.grid[d_row][d_col] = "0"         
                self.timer_grid[d_row][d_col] = 0
        
        # If there was a match, destroy the cell itself
        if match_found: 
            print "!" * 17 + "Yay! Match found!" + "!" * 17
            self.grid[row][col] = "0"
            self.timer_grid[row][col] = 0
            print self.goal
            if not self.goal: print "You won!"

def main():
    game = Game()
    
if __name__ == '__main__':
	main()
