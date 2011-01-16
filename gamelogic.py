#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       "Alchemy: In search of the Philosopher's stone" is a fantasy 
#       "match three" puzzle game.
#       
#       Copyright 2011 Valentina Mukhamedzhanova <umi@ubuntu.ru>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import random
import json
import os.path
import sys
import math
import pygame

SCREEN_SIZE = 1024, 800
GRID_OFFSET = (300, 180)
NEXT_OFFSET = (20, 40)

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

LEVELS = (1, 2, 3, 4)

class Game(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_icon(pygame.image.load(os.path.join("images","icon.png")))
        self.screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
        pygame.display.set_caption("Alchemy")
        
        self.load_resources()
        self.main_menu()
    
    def main_menu(self):
        self.locked_levels = list(LEVELS[1:])
           
        self.screen.blit(self.images["menu_bg"], (0,0))
        
        logo_l = self.biggest_font.render("Alchemy", 1, (255,255,255))
        title_l = self.smaller_font.render("In search of the Philosopher's Stone", 1, (255,255,255))
        self.screen.blit(logo_l, (320, 90))
        self.screen.blit(title_l, (345, 190))
        
        self.screen.blit(self.images["menu"], (360,340))
        #pygame.draw.rect(self.screen, (50,50,50), (360, 340, 290, 110))
        
        new_quest_b = self.big_font.render("NEW QUEST", 1, (255,255,255))
        new_quest_b_rect = new_quest_b.get_rect(topleft = (380, 360))
        continue_quest_b = self.big_font.render("CONTINUE QUEST", 1, (255,255,255))
        continue_quest_b_rect = continue_quest_b.get_rect(topleft = (380, 410))
        
        self.screen.blit(new_quest_b, new_quest_b_rect)
        self.screen.blit(continue_quest_b, continue_quest_b_rect)
        
        self.clock = pygame.time.Clock()
        pygame.display.update()
        
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
                if new_quest_b_rect.collidepoint(event.pos):
                    self.load_game_screen()
    
    def load_game_screen(self):
        '''Show main in-game screen. User can select a level from a list of
           unlocked levels here.'''
        self.screen.fill((50,50,50))

        
        level_image_rects = {}
        
        for i in LEVELS:
            image = self.images['level_%i' %i]
            if i not in self.locked_levels:
                image.fill((255, 255,255), None, pygame.BLEND_ADD)
            level_image_rects[i] = (image.get_rect(topleft = (40, i*40)))
            self.screen.blit(image, (40, i*40))

        
        while True:
            self.clock.tick(60)
            event = pygame.event.poll()
            pygame.event.clear()
            
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.main_menu()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i in LEVELS:
                    if level_image_rects[i].collidepoint(event.pos):
                        if not i in self.locked_levels:
                            won = self.load_level("level_%i" %i)
                            if won and (i+1 in self.locked_levels):
                                self.locked_levels.remove(i+1)
                            self.load_game_screen()    
            pygame.display.update()
    
    @staticmethod
    def img_load(dir, file):
        '''Helper function for loading images'''
        return pygame.image.load(os.path.join(dir, file)).convert_alpha()        
    
    def load_resources(self):
        '''Load images, fonts, sounds, etc'''
        self.images = {}
        self.images['grid'] = self.img_load("images", "grid.jpg")
        self.images['shadow'] = self.img_load("images", "shadow.png")
        self.images['border'] = self.img_load("images", "border.png")
        self.images['grid_border'] = self.img_load("images", "grid_border.png")
        for element in ELEMENTS.values():
            self.images[element] = self.img_load("images", element + ".png")
        
        self.biggest_font = pygame.font.Font("fonts/eufm10.ttf", 106)
        self.big_font = pygame.font.Font("fonts/eufm10.ttf", 26)
        self.smaller_font = pygame.font.Font("fonts/eufm10.ttf", 22)
        
        for level in LEVELS:
            self.images['level_%i' %level] = self.smaller_font.render("Level %i" %level, 1, (255,0,0))
            
        self.images['menu_bg'] = self.img_load("images", "menu_bg.png")
        self.images['menu'] = self.img_load("images", "menu.png")
    
    def load_level(self, level_id):
        '''Load level from a text file and run it'''
        #level_file = open(os.path.join("levels", level_id), "r")
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
        
        self.timer_grid = [[0 for cell in row ] for row in level["field"]]
        now = pygame.time.get_ticks()/1000
        for rnum, row in enumerate(self.grid):
            for cnum, cell in enumerate(row):
                if cell <> "0" and cell <> "4" and cell <> "7" and cell <> "b":
                    self.timer_grid[rnum][cnum] = now + 60 + random.randint(0,5)
        return self.run_level()

    def set_screen(self):
        '''Set screen for current level'''
        self.update_rects = []
        self.screen.blit(self.images["bg_image"], (0, 0))
        self.screen.blit(self.images['grid_border'], (GRID_OFFSET[0]-32, GRID_OFFSET[1]-32))
        
        self.grid_area = self.images['grid'].copy()
        self.grid_area_rect = self.grid_area.get_rect(topleft = GRID_OFFSET)
        self.update_rects.append(self.grid_area_rect)
        self.show_grid()
        
        next_label = self.big_font.render("Next:", 1, (255, 255, 255))
        self.screen.blit(next_label, (20, 10))
        
        self.next_area = pygame.Surface((128, 128))
        self.update_rects.append(self.next_area.get_rect(topleft = NEXT_OFFSET))
        self.show_next()
        
        goal_label = self.big_font.render("Metals to transmute:", 1, (255, 255, 255))
        self.screen.blit(goal_label, (20, 170))
        self.show_goal()
        
        pygame.display.update()

    def run_level(self):
        '''Game cycle'''
        self.mouse_pos = GRID_OFFSET
        mouse_visible = True
        
        self.figure = self.get_next_figure()
        self.create_figure_img()
        self.next_figure = self.get_next_figure()
        
        self.victory = False
        
        self.set_screen()

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
                    self.create_figure_img()
                    coords_checked = self.check_place(event.pos)
                    self.update_screen()
                            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.grid_area_rect.collidepoint(event.pos) and coords_checked:
                    # Left mouse click places the figure
                    self.place_figure(event.pos)
                    coords_checked = self.check_place(event.pos)
                    self.update_screen()
                
            if event.type == pygame.MOUSEMOTION:
                # Mouse moved above the grid area
                if self.grid_area_rect.collidepoint(event.pos):
                    pygame.mouse.set_visible(False)
                    mouse_visible = False
                    self.mouse_pos = event.pos[0] - GRID_OFFSET[0], event.pos[1] - GRID_OFFSET[1]
                    self.create_figure_img()
                    coords_checked = self.check_place(event.pos)
                    self.update_screen()
                    
                else:
                    self.show_grid()
                    if not mouse_visible:
                        pygame.mouse.set_visible(True)
                        mouse_visible = True

            self.age_metal()
            
            if self.victory:
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
                    if self.grid[rnum][cnum][-1] <> "s" and self.grid[rnum][cnum] <> "o" and self.grid[rnum][cnum] <> "b":
                        self.grid[rnum][cnum] = self.grid[rnum][cnum] + "s"
                        self.timer_grid[rnum][cnum] = now + 60 + random.randint(0,5)
                    else:
                        self.grid[rnum][cnum] = "o" 
                        self.timer_grid[rnum][cnum] = 0
                    changed = True
        if changed: self.update_screen()
    
    @staticmethod
    def get_row_col(pos):
        '''Transform absolute mouse coordinates into grid-relative
           and return respective row and column numbers'''
        mouse = pos[0] - GRID_OFFSET[0], pos[1] - GRID_OFFSET[1]
        col, row = (mouse[0]+16)/32, (mouse[1]+16)/32
        return row, col, mouse
    
    def update_screen(self):
        # Update the grid area
        self.show_grid()

        # Show the shadow of the current figure
        for coords in self.shadow:
            self.grid_area.blit(self.images['shadow'], coords)

        # Show the figure
        for cell in self.figure_image.values():
            self.grid_area.blit(*cell)
        self.screen.blit(self.grid_area, GRID_OFFSET)

        pygame.display.update(self.update_rects)

    def show_goal(self):
        '''Update screen in the goal area''' 
        goal_labels = []
        # Create labels for the level goal
        for metal, quantity in self.goal.items():
            goal_label = "%s: %i" %(ELEMENTS[metal].capitalize(), quantity)
            goal_labels.append(self.smaller_font.render(goal_label, 1, (255,255,255)))
        # Show labels
        for i, label in enumerate(goal_labels):
            self.screen.blit(self.images["bg_image"], (20, 205 + i*25), (20, 205 + i*25, 120, 25))
            self.screen.blit(label, (20, 205 + i*25))
            rect = (20, 205 + i*25, 120, 25)
            if rect not in self.update_rects: self.update_rects.append(rect)
    
    def show_next(self):
        '''Update screen in the next figure area'''
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
        
    def check_place(self, pos):
        '''Check whether the figure can be placed in current position.
           If not, update shadow and darken appropriate cells of the 
           current figure.'''
        row, col, mouse = self.get_row_col(pos)
        
        check_results = []
        
        for rnum, c_row in enumerate(self.figure):
            for cnum, cell in enumerate(c_row):
                if not cell: continue       # No need to check an empty cell
                try:
                    if self.grid[row + rnum][col + cnum] == "0":
                        check_results.append(True)
                        self.shadow.append(((col+cnum)*32, (row+rnum)*32))
                    else:
                        check_results.append(False)
                        self.figure_image[rnum, cnum][0].fill((50, 50,50), None, pygame.BLEND_SUB)
                except IndexError:
                    check_results.append(False)

        coords_checked = all(check_results)
        return coords_checked       

    def place_figure(self, pos):
        '''Add new values to the grid, handle matches for new values, generate
           the next figure and show it in the next_area'''
        row, col, mouse = self.get_row_col(pos)
        
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
        self.create_figure_img()
        self.next_figure = self.get_next_figure()
        
        # Update visuals
        self.show_next()
        
    def create_figure_img(self):
        '''Create a dict containing images for every cell of the figure and their
           coordinates in order to blit all cell images when updating screen.'''
        self.figure_image = {}
        for rnum, c_row in enumerate(self.figure):
            for cnum, cell in enumerate(c_row):
                if cell:
                    cell_image = self.images[ELEMENTS[cell]].copy()
                else: continue       # No need to check an empty cell
                self.figure_image[rnum, cnum] = [cell_image, [self.mouse_pos[0] + cnum*32, self.mouse_pos[1] + rnum*32]]
        self.shadow = []
    
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
            element = cell[0]
            if element in self.goal:
                if self.goal[element] <= 0:
                    self.goal[element] = 0
                else:
                    self.goal[element] -=1
                #if self.goal[element] == 0: self.goal.pop(element)
            for d_row, d_col in to_del_coords: 
                self.grid[d_row][d_col] = "0"
                self.timer_grid[d_row][d_col] = 0

        # Check adjacent cells in horizontal direction (left, then right)
        counter = 0
        to_del_coords = []

        counter, to_del_coords = check_direction(row, col, left, cell, counter, to_del_coords)
        counter, to_del_coords = check_direction(row, col, right, cell, counter, to_del_coords)

        if counter >= 2:
            element = cell[0]
            match_found = True
            if element in self.goal:
                if self.goal[element] <= 0:
                    self.goal[element] = 0
                else:
                    self.goal[element] -=1
            for d_row, d_col in to_del_coords:
                self.grid[d_row][d_col] = "0"         
                self.timer_grid[d_row][d_col] = 0
        
        # If there was a match, destroy the cell itself
        if match_found: 
            self.grid[row][col] = "0"
            self.timer_grid[row][col] = 0
            self.show_goal()
            if all([quantity == 0 for quantity in self.goal.values()]): self.victory = True

def main():
    game = Game()
    
if __name__ == '__main__':
	main()
