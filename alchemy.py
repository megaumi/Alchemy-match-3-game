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
import shutil
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


def img_load(dir, file):
    '''Helper function for loading images'''
    return pygame.image.load(os.path.join(dir, file)).convert_alpha()    


class Game(object):
    def __init__(self):
        '''Initialize the game, load resources and show the main menu'''        
        pygame.init()
        
        # Create the game window, set icon and window title
        pygame.display.set_icon(pygame.image.load(os.path.join("images","icon.png")))
        self.screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
        pygame.display.set_caption("Alchemy")
        
        # Clock will be used for polling events
        self.clock = pygame.time.Clock()
        
        self.load_resources()
        self.main_menu()

    def load_resources(self):
        '''Load images, fonts, sounds, etc'''
        self.images = {}
        
        # In-game images
        self.images['grid'] = img_load("images", "grid.jpg")
        self.images['shadow'] = img_load("images", "shadow.png")
        self.images['border'] = img_load("images", "border.png")
        self.images['grid_border'] = img_load("images", "grid_border.png")
        
        # In-game element images
        for element in ELEMENTS.values():
            self.images[element] = img_load("images", element + ".png")
                    
        # GUI images
        self.images['menu_bg'] = img_load("images", "menu_bg.png")
        self.images['msg'] = img_load("images", "msg.png")
        self.images['level_menu'] = img_load("images", "level_menu.png")
        self.images['new_user'] = img_load("images", "new_user.png")
        self.images['ok'] = img_load("images", "ok.png")
        
        # Fonts
        self.big_font = pygame.font.Font("fonts/eufm10.ttf", 26)
        self.smaller_font = pygame.font.Font("fonts/eufm10.ttf", 22)
        self.biggest_font = pygame.font.Font("fonts/eufm10.ttf", 106)
        
        # Level labels used in self.game_screen()
        for level in LEVELS:
            self.images['level_%i' %level] = self.smaller_font.render("Level %i" %level, 1, (255,255,255))

        # ./settings_init file contains initial game settings.
        # ./settings is the file that we actually work with.
        # If ./settings does not exist, we create it from ./settings_init.
        if not os.path.exists("settings"): shutil.copyfile("settings_init", "settings")

    def main_menu(self):
        '''Load game settings from file.
           If there are no user profiles, ask user to create one.
           Load user progress from file.
           Show the main game menu:
                Continue Quest
                New Quest
                Options         - not implemented yet
                High Scores     - not implemented yet
                Exit            - not implemented yet
           User can select another profile here as well (not implemented yet).'''
        
        # Show the background image and the "Alchemy" logo with the shadow
        self.screen.blit(self.images["menu_bg"], (0,0))        
        logo_l = self.biggest_font.render("Alchemy", 1, (255,255,255))
        logo_ls = self.biggest_font.render("Alchemy", 1, (70,70,70))
        title_l = self.smaller_font.render("In search of the Philosopher's Stone", 1, (255,255,255))
        self.screen.blit(logo_ls, (324, 93))
        self.screen.blit(logo_l, (320, 90))
        self.screen.blit(title_l, (345, 190))
        
        # Load main game settings from file
        # Example settings: {"sound": 3, "music": 3, "user": "umi"}
        settings_file = open("settings", "r")
        self.settings = json.loads(settings_file.read())
        settings_file.close()
        
        new_user = False
        
        # If there are no user profiles, create one
        if self.settings["user"] == "None":
            self.create_new_user()
            new_user = True
        
        self.username = self.settings["user"]
        
        # Load user progress file
        # Example: {"score": 700, "locked": [4]}
        user_file = open("%s_progress" %self.username, "r")
        self.user = json.loads(user_file.read())
        user_file.close()
        
        # Construct the main menu: show the menu bg image and some labels
        self.screen.blit(self.images["msg"], (360,340))        
        new_quest_b = self.big_font.render("New Quest", 1, (255,255,255))
        new_quest_b_rect = new_quest_b.get_rect(topleft = (380, 410))
        # If we just created a user profile, "Continue Quest" should look (and be) disabled
        if new_user:
            continue_quest_b = self.big_font.render("Continue Quest", 1, (50,50,50))
        else:
            continue_quest_b = self.big_font.render("Continue Quest", 1, (255,255,255))
        continue_quest_b_rect = continue_quest_b.get_rect(topleft = (380, 360))        
        self.screen.blit(new_quest_b, new_quest_b_rect)
        self.screen.blit(continue_quest_b, continue_quest_b_rect)
        
        pygame.display.update()
        
        # Wait for user input
        while True:
            self.clock.tick(60)
            event = pygame.event.poll()
            pygame.event.clear()
            
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
            # User can select any menu item
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if new_quest_b_rect.collidepoint(event.pos):
                    # User selected "New Quest": reinitialize the user progress file
                    self.user = {"score": 0, "locked": [2,3,4]}
                    user_file = open("%s_progress" %self.username, "w")
                    user_file.write(json.dumps(self.user))
                    user_file.close()
                    # Load game
                    self.game_screen()
                # New users cannot select "Continue Quest"
                if continue_quest_b_rect.collidepoint(event.pos) and not new_user:
                    self.game_screen()

    def create_new_user(self):
        self.screen.blit(self.images["new_user"], (360,340))
        self.screen.blit(self.images["ok"], (600,390))
        pygame.display.update()
        chars = ""
        widths = []
        while True:
            self.clock.tick(60)
            event = pygame.event.poll()
            pygame.event.clear()
            
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if 123 > event.key > 96:
                    if sum(widths) < 193:
                        char = chr(event.key) if chars else chr(event.key).upper()
                        chars += char
                        char_img = self.smaller_font.render(char, 1, (255,255,255))
                        self.screen.blit(char_img, (393 + sum(widths), 397))
                        pygame.display.update((393 + sum(widths),397, 32, 32))
                        widths.append(char_img.get_width()+1)
                    
                if event.key == pygame.K_BACKSPACE and chars:
                    chars = chars[:-1]
                    widths.pop(len(chars))                        
                    self.screen.blit(self.images["new_user"], (393 + sum(widths), 397), (33 + sum(widths), 57, 22, 32))
                    pygame.display.update((393 + sum(widths), 397, 22, 32))

                if event.key == pygame.K_ESCAPE:
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if (self.images["ok"].get_rect(topleft = (600, 390)).collidepoint(event.pos)
                    and chars):
                    username = chars.lower()
                    
                    settings_file = open("settings", "w")
                    self.settings["user"] = username
                    settings_file.write(json.dumps(self.settings))
                    settings_file.close()
                    
                    user_file = os.open("%s_progress" %username, os.O_CREAT|os.O_WRONLY)
                    os.write(user_file, json.dumps({"Score": 0, "locked": [2,3,4]}))
                    os.close(user_file)
                                        
                    return
                    
    def game_screen(self):
        '''Show the main in-game screen. User can select a level from 
           the list of unlocked levels here.'''
        
        level_image_rects = {}
        self.screen.blit(self.images["menu_bg"], (0,0))
        
        logo_l = self.biggest_font.render("Alchemy", 1, (255,255,255))
        logo_ls = self.biggest_font.render("Alchemy", 1, (70,70,70))
        title_l = self.smaller_font.render("In search of the Philosopher's Stone", 1, (255,255,255))
        self.screen.blit(logo_ls, (324, 93))
        self.screen.blit(logo_l, (320, 90))
        self.screen.blit(title_l, (345, 190))
        
        self.screen.blit(self.images["level_menu"], (360,340))
        
        self.score = self.user["score"]
        self.locked_levels = self.user["locked"]
        
        score_l = self.smaller_font.render("Score: %i" % self.score, 1, (255,255,255))
        self.screen.blit(score_l, (20, 760))

        for i in LEVELS:
            image = self.images['level_%i' %i]
            if i in self.locked_levels:
                image.fill((205, 205, 205), None, pygame.BLEND_SUB)
            level_image_rects[i] = (image.get_rect(topleft = (380, 320+i*40)))
            self.screen.blit(image, (380, 320+i*40))

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
                            level = Level(self.screen, self.images, self.big_font, self.smaller_font, self.score, "level_%i" %i)
                            won, self.score = level.run()
                            if won:
                                self.user["score"] = self.score
                                user_file = open("%s_progress" %self.username, "w")
                                if i+1 in self.locked_levels:
                                    self.locked_levels.remove(i+1)
                                    self.images['level_%i' %(i+1)].fill((255, 255, 255), None, pygame.BLEND_ADD)
                                    self.user["locked"] = self.locked_levels
                                user_file.write(json.dumps(self.user))
                                user_file.close()
                            self.game_screen()    
            pygame.display.update()


class Level(object):
    def __init__(self, screen, images, big_font, smaller_font, score, level_id):
        '''Load a level from a text file and run it'''
        self.screen = screen
        self.level_id = level_id
        level_file = open(os.path.join("levels", level_id), "r")
        level = json.loads(level_file.read())
        
        self.grid_size = 15
        self.figure_max_size = level["figure_max_size"]
        
        self.elements = level["elements"]
        self.spoilt = level["spoilt"]
        self.locked = level["locked"]
        
        self.goal = level["goal"]
        self.init_score = self.score = score        
        self.bonus = 0
        
        self.images = images
        
        self.images["bg_image"] = img_load("images", level["bg_image"])
        
        self.big_font = big_font
        self.smaller_font = smaller_font
        
        self.clock = pygame.time.Clock()
        
        self.grid = [[str(cell) for cell in row] for row in level["field"]]
        
        self.timer_grid = [[0 for cell in row ] for row in level["field"]]
        now = pygame.time.get_ticks()/1000
        for rnum, row in enumerate(self.grid):
            for cnum, cell in enumerate(row):
                if cell <> "0" and cell <> "4" and cell <> "7" and cell <> "b":
                    self.timer_grid[rnum][cnum] = now + 60 + random.randint(0,5)

    def run(self):
        '''Game cycle'''

        self.victory = False
        self.defeat = False
        
        self.figure = self.get_next_figure()
        self.next_figure = self.get_next_figure()
        self.global_check_place()
        
        self.set_screen()
        self.create_figure_img()
        coords_checked = self.check_place(self.mouse_pos)
        self.update_screen()
        
        while True:
            
            self.clock.tick(60)
            event = pygame.event.poll()
            pygame.event.clear()
            
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.mouse_visible:
                        pygame.mouse.set_visible(True)
                        self.mouse_visible = True
                    return False, self.init_score
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if self.grid_area_rect.collidepoint(event.pos):
                    # Right mouse click rotates the figure
                    self.figure = zip(*self.figure[::-1])
                    self.mouse_pos = event.pos[0] - GRID_OFFSET[0], event.pos[1] - GRID_OFFSET[1]
                    self.create_figure_img()
                    coords_checked = self.check_place(self.mouse_pos)
                    self.update_screen()
                            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.grid_area_rect.collidepoint(event.pos) and coords_checked:
                    # Left mouse click places the figure
                    self.mouse_pos = event.pos[0] - GRID_OFFSET[0], event.pos[1] - GRID_OFFSET[1]
                    self.place_figure(self.mouse_pos)
                    coords_checked = self.check_place(self.mouse_pos)
                    self.update_screen()
                
            if event.type == pygame.MOUSEMOTION:
                # Mouse moved above the grid area
                if self.grid_area_rect.collidepoint(event.pos):
                    pygame.mouse.set_visible(False)
                    mouse_visible = False
                    self.mouse_pos = event.pos[0] - GRID_OFFSET[0], event.pos[1] - GRID_OFFSET[1]
                    self.create_figure_img()
                    coords_checked = self.check_place(self.mouse_pos)
                    self.update_screen()
                    
                else:
                    self.show_grid()
                    if not mouse_visible:
                        pygame.mouse.set_visible(True)
                        mouse_visible = True

            self.age_metal()
            
            if self.victory:
                self.on_victory()
                return True, self.score
                
            if self.defeat:
                self.on_defeat()
                return False, self.init_score
    
    def on_victory(self):
        '''Show a "Well done!" message to the user'''
        
        if not self.mouse_visible:
            pygame.mouse.set_visible(True)
            self.mouse_visible = True
        
        # Remove the image of the figure and its shadow from the grid
        self.show_grid()
        
        # Darken the game screen
        self.screen.fill((100, 100, 100), None, pygame.BLEND_MULT)
        
        # Show the message window and the "Well done!" label
        self.screen.blit(self.images["msg"], (360, 340))
        win_label = self.big_font.render("Well done!", 1, (255, 255, 255))
        self.screen.blit(win_label, (445, 380))
        
        pygame.display.update()
        
        # Wait for the user's input
        while True:
            self.clock.tick(60)
            event = pygame.event.poll()
            pygame.event.clear()
            
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
            # Left mouse click returns us to the games screen
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return
                    
    def get_next_figure(self):
        '''Generate a new figure.
           This function is called from self.run() to generate 2 initial figures
           and then from self.place_figure() every time we need a new figure.'''
        
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

    def on_defeat(self):
        '''Show a "Try again!" message to the user'''
        
        if not self.mouse_visible:
            pygame.mouse.set_visible(True)
            self.mouse_visible = True
        
        # Remove the image of the figure and its shadow from the grid
        self.show_grid()
        
        # Darken the game screen
        self.screen.fill((100, 100, 100), None, pygame.BLEND_MULT)
        
        # Show the message window and the "Try again!" label
        self.screen.blit(self.images["msg"], (360, 340))
        win_label = self.big_font.render("Try again!", 1, (255, 255, 255))
        self.screen.blit(win_label, (445, 380))
        
        pygame.display.update()
        
        # Wait for the user's input
        while True:
            self.clock.tick(60)
            event = pygame.event.poll()
            pygame.event.clear()
            
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
            # Left mouse click returns us to the games screen
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return
 
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
        
        score_l = self.smaller_font.render("Score: %i" % self.score, 1, (255,255,255))
        self.screen.blit(score_l, (20, 760))
        bonus_l = self.smaller_font.render("Bonus: %i" % self.bonus, 1, (255,255,255))
        self.screen.blit(bonus_l, (900, 760))
        self.update_rects.append((20, 760, 120, 25))
        self.update_rects.append((900, 760, 120, 25))
                
        init_mouse = pygame.mouse.get_pos()
        
        if self.grid_area_rect.collidepoint(init_mouse):
            pygame.mouse.set_visible(False)
            self.mouse_visible = False
            self.mouse_pos = init_mouse[0] - GRID_OFFSET[0], init_mouse[1] - GRID_OFFSET[1]

        pygame.display.update()
       
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
    
    def check_place(self, pos):
        '''Check whether the figure can be placed in current mouse position.
           If not, update shadow and darken appropriate cells of the 
           current figure.'''
        row, col = self.get_row_col(pos)
        
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
    
    def global_check_place(self):
        '''Check if there is enough free space on the grid for current figure.
           If not, user lost this game.'''

        # Store all possible rotations of the figure in a list
        rotations = [self.figure]
        for i in range(3):
            rotations.append(zip(*rotations[i][::-1]))
        
        # We look for a place for any rotation of the figure
        for figure in rotations:
            # These two loops iterate through the grid
            for g_rnum, gc_row in enumerate(self.grid):
                for g_cnum, g_cell in enumerate(gc_row):
                    
                    check_results = []
                    
                    # These two loops iterate through current figure, cell by cell.
                    # Results are stored in check_results.
                    for rnum, c_row in enumerate(figure):
                        for cnum, cell in enumerate(c_row):
                            if not cell: continue       # No need to check an empty cell
                            try:
                                if self.grid[g_rnum + rnum][g_cnum + cnum] == "0":
                                    check_results.append(True)
                                else:
                                    check_results.append(False)
                            except IndexError:
                                check_results.append(False)
                    
                    # Check if all cells of current figure can be placed in current position of the grid.
                    # If yes, then there is no need to check any other rotation or positions.
                    can_place = all(check_results)
                    if can_place:
                        return
        
        # If we did not return at some point then no place was found for current figure => the game is lost
        self.defeat = True
    
    def update_screen(self):
        '''Update the grid, the figure image and its shadow.
           This function is called every time the user moves or left-clicks
           his mouse or rotates the figure.
           It is also called before the game loop (right after the screen
           has been set), and from self.age_metal().'''
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

    def place_figure(self, pos):
        '''Add new values to the grid, handle matches for new values, generate
           the next figure and show it in the next_area'''
        row, col = self.get_row_col(pos)
        
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
        
        # Check if the new figure can be placed anywhere
        self.global_check_place()
        
        # Update visuals
        self.show_next()
    
    def age_metal(self):
        '''Check if one or more pieces of metal aged. 
           If yes, update the timers and the screen.'''
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
        '''Return row and column numbers for current mouse position'''
        col, row = (pos[0]+16)/32, (pos[1]+16)/32
        return row, col

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
        
        score_l = self.smaller_font.render("Score: %i" % self.score, 1, (255,255,255))
        self.screen.blit(self.images["bg_image"], (20, 760), (20, 760, 120, 25))
        self.screen.blit(score_l, (20, 760))
        
        bonus_l = self.smaller_font.render("Bonus: %i" % self.bonus, 1, (255,255,255))
        self.screen.blit(self.images["bg_image"], (900, 760), (900, 760, 120, 25))
        self.screen.blit(bonus_l, (900, 760))
        
    
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
        
    def handle_matches(self, row, col, cell):
        '''Find all matches with the current cell and destroy all matching cells'''
        
        def check_direction(row, col, dir, cell, counter, to_del_coords):
            '''Check the next cell in given direction. If it has the same color as the current cell,
            store its coords (to delete it later) and pass it to this function recursively
            with an incremented counter'''
            
            n_row = row + dir[0]
            n_col = col + dir[1]            
            
            # We don't want to get outside of our grid
            if not (n_row < 0 or n_col < 0 or n_row >= len(self.grid) or n_col >= len(self.grid)):
                # If the last character is "l" (which indicates a locked cell)
                # then there's no match for sure
                if self.grid[n_row][n_col][-1] == "l" or cell[-1] == "l":
                    return counter, to_del_coords
                # We compare only the first character, so that "1" and "1s"
                # (which are mercury and spoilt mercury) will make a match
                if self.grid[n_row][n_col][0] == cell[0]:
                    to_del_coords.append([n_row, n_col])
                    counter += 1
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
            for d_row, d_col in to_del_coords: 
                self.grid[d_row][d_col] = "0"
                self.timer_grid[d_row][d_col] = 0
            print "Element: %s" % element
            self.score += 50 * counter
            self.bonus += counter - 2
            print self.score, self.bonus

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
            print "Element: %s" % element
            self.score += 50 * counter
            self.bonus += counter - 2
            print self.score, self.bonus
                                
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
