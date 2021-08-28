#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 13 17:37:31 2020

@author: robertopitz
"""
import numpy as np
from random import randrange
from math import isnan
import pygame as pg

def get_new_prey_pos(pos, board):
    while True:
        c = randrange(1,len(board)-1)
        r = randrange(1,len(board[0])-1)
        if c != pos[0] or r != pos[1]:
            if board[c][r] == 0:
                return np.array([c,r])

def get_next_move(pos, board):
    c = pos[0]
    r = pos[1]
    gradient = np.array([board[c+1][r], board[c-1][r], 
                         board[c][r-1], board[c][r+1]])
    i = np.argmin(gradient)
    move = ["RIGHT", "LEFT", "UP", "DOWN"]
    return move[i]
    
def move_bot(bot_pos, prey_pos, board, penalty_board):
    c = bot_pos[0]
    r = bot_pos[1]
    move = get_next_move(bot_pos, penalty_board)
    step_size = 1
    if move == "UP":
        if board[c][r-1] == 0:
            bot_pos[1] -= step_size
    elif move == "DOWN":
        if board[c][r+1] == 0:
            bot_pos[1] += step_size
    elif move == "LEFT":
        if board[c-1][r] == 0:
            bot_pos[0] -= step_size
    elif move == "RIGHT":
        if board[c+1][r] == 0:
            bot_pos[0] += step_size
            
def convert_board(board):
    new_board = np.zeros(board.shape)
    new_board = new_board.astype(float)
    new_board[board == 0.] = np.nan
    new_board[board == 1.] = float('inf')
    return new_board

def convert_to_draw_board(board):
    new_board = np.zeros(board.shape)
    for c in range(np.size(board,0)):
        for r in range(np.size(board,1)):
            b = board[c][r]
            if b == "o" or b == "O" or b == " ":
                new_board[c,r] = 0
            else:
                new_board[c,r] = 1
    return new_board
            
def create_gradient(board):
    # border is Inf
    # empty field is NaN
    step_penalty = 1
    nans_present = True
    border = float('inf')
    while nans_present:
        nans_present = False
        for c in range(1,len(board)-1):
            for r in range(1,len(board[0])-1):
                if isnan(board[c][r]):
                    nans_present = True
                    if isnan(board[c+1][r]) and isnan(board[c][r+1]):
                        pass
                    elif isnan(board[c+1][r]) and not isnan(board[c][r+1]):
                      if board[c][r+1] != border:
                        board[c][r] = board[c][r+1] + step_penalty
                    elif not isnan(board[c+1][r]) and isnan(board[c][r+1]):
                      if board[c+1][r] != border:
                        board[c][r] = board[c+1][r] + step_penalty
                    else:
                      if board[c+1][r] != border and \
                         board[c][r+1] != border:
                        board[c][r] = int(0.5 * (board[c+1][r] + \
                                                  board[c][r+1]) + step_penalty)
                      elif board[c+1][r] == border and \
                           board[c][r+1] != border:
                        board[c][r] = board[c][r+1] + step_penalty
                      elif board[c+1][r] != border and \
                           board[c][r+1] == border:
                        board[c][r] = board[c+1][r] + step_penalty
                else:
                  if board[c][r] != border:
                    if isnan(board[c+1][r]):
                        board[c+1][r] = board[c][r] + step_penalty
                    if isnan(board[c][r+1]):
                        board[c][r+1] = board[c][r] + step_penalty
    return board

def nint(f):
   return int(round(f))
            
def get_penalty_board(board, prey_pos):
    new_board = np.copy(board)
    c = nint(prey_pos[0])
    r = nint(prey_pos[1])
    new_board[c, r] = 0.0
    penalty_board = create_gradient(new_board)
    return penalty_board
    
def draw_board(screen, board, rs):
    for c in range(np.size(board,0)):
        for r in range(np.size(board,1)):
            if board[c,r] == 1:
                pg.draw.rect(screen,
                             pg.Color("blue"),
                             pg.Rect(c * rs,
                                     r * rs,
                                     rs, rs))
                
def draw_bot(screen, pos, rs):
    pg.draw.rect(screen,
                 pg.Color("red"),
                 pg.Rect(pos[0] * rs,
                         pos[1] * rs,
                         rs, rs))
    
def draw_prey(screen, pos, rs):
    pg.draw.rect(screen,
                 pg.Color("yellow"),
                 pg.Rect(pos[0] * rs,
                         pos[1] * rs,
                         rs, rs))

def play_game(bot_pos_start, board_extern):
    
    board = convert_to_draw_board(board_extern)
    penalty_board_blue_print = convert_board(board)
    
    rect_size = 15
    bot_pos = np.copy(bot_pos_start)
    
    pg.init()
    screen_color = pg.Color("black")

    screen = pg.display.set_mode((np.size(board,0) * rect_size,
                                  np.size(board,1) * rect_size))
    clock = pg.time.Clock()

    pg.display.set_caption("Clean Bot AI")

    running = True
    prey_pos = get_new_prey_pos(bot_pos, board)
    penalty_board = get_penalty_board(penalty_board_blue_print, prey_pos)
    while running:
    
        move_bot(bot_pos, prey_pos, board, penalty_board)
    
        if bot_pos[0] == prey_pos[0] and bot_pos[1] == prey_pos[1]:
            prey_pos = get_new_prey_pos(bot_pos, board)
            penalty_board = get_penalty_board(penalty_board_blue_print, 
                                              prey_pos)
    
        screen.fill(screen_color)
    
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
    
        draw_board(screen, board, rect_size)
        draw_prey(screen, prey_pos, rect_size)
        draw_bot(screen, bot_pos, rect_size)
            
        clock.tick(60)
            
        pg.display.flip()

    pg.quit()
    
#==MAIN CODE==================================================================


board = [list("x--------x---|-|---x----xx----x"),#1
         list("|ooOooooo|---| |---|oooO||oooo|"),#2
         list("|ox-xo--o|---| |---|o--o--o--o|"),#3
         list("|o|-|o||o|---| |---|o||oooo||o|"),#4
         list("|o|-|o||o|---| |---|o|x--|o||o|"),#5
         list("|ox-xo--ox---x x---xo----|o||o|"),#6
         list("|oooooooooooooooooooooooooo||o|"),#7
         list("|ox-xo|------| |---|o--o|--x|o|"),#8
         list("|o|-|o|--xx--| |---|o||o|--x|o|"),#9
         list("|o|-|oooo||         o||oooo||o|"),#10
         list("|o|-|o--o|| x---x --o||o--o||o|"),#11
         list("|ox-xo||o-- |x-x| ||o--o||o--o|"),#12
         list("|ooooo||o   ||-|| ||oooo||oooo|"),#13
         list("x---|o|x--| |--|| |x--|o|x--|o|"),#14
         list("x---|o|x--| |--|| |x--|o|x--|o|"),#15
         list("|ooooo||o   ||-|| ||oooo||oooo|"),#16
         list("|ox-xo||o-- |x-x| ||o--o||o--o|"),#17
         list("|o|-|o--o|| x---x --o||o--o||o|"),#18
         list("|o|-|oooo||         o||oooo||o|"),#19
         list("|o|-|o|--xx--| |---|o||o|--x|o|"),#20
         list("|ox-xo|------| |---|o--o|--x|o|"),#21
         list("|oooooooooooooooooooooooooo||o|"),#22
         list("|ox-xo--ox---x x---xox---|o||o|"),#23
         list("|o|-|o||o|---| |---|o|x--|o||o|"),#24
         list("|o|-|o||o|---| |---|o||oooo||o|"),#25
         list("|ox-xo--o|---| |---|o--o--o--o|"),#26
         list("|ooOooooo|---| |---|oooO||oooo|"),#27
         list("x--------x---|-|---x----xx----x")#28
         ]

# board = [[1,1,1,1,1,1,1,1,1],
#          [1,0,0,0,1,0,0,0,1],
#          [1,0,0,0,1,0,1,0,1],
#          [1,0,1,1,1,0,1,0,1],
#          [1,0,1,0,1,1,1,0,1],
#          [1,0,0,0,0,0,0,0,1],
#          [1,0,0,0,1,1,1,0,1],
#          [1,0,1,0,1,0,1,0,1],
#          [1,0,1,1,1,0,1,0,1],
#          [1,0,0,0,1,0,1,0,1],
#          [1,0,0,0,1,0,0,0,1],
#          [1,1,1,1,1,1,1,1,1]]

board = np.array(board)

bot_pos_start = np.array([1,1])

play_game(bot_pos_start, board)
