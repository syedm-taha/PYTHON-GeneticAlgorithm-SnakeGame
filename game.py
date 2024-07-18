import numpy as np
import tkinter as tk
import time as time
import random as rand

#Global
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)

MOVES = [UP, DOWN, LEFT, RIGHT]

EMPTY = 0
FOOD = 99

class Game:
    def __init__(self, size, num_snakes, players, gui=None, display=False, max_turns=100):
        self.size = size
        self.num_snakes = num_snakes
        self.players = players
        self.gui = gui
        self.display = display
        self.max_turns = max_turns

        self.num_food = 4
        self.turn = 0
        self.snake_size = 3

        self.snakes = [[((j + 1) * self.size // (2 * self.num_snakes), self.size // 2 + i) for i in range(self.snake_size)] for j in range(self.num_snakes)]
        self.food = [(self.size // 4, self.size // 4), (3 * self.size // 4, self.size // 4), (self.size // 4, 3 * self.size // 4), (3 * self.size // 4, 3 * self.size // 4)]
        self.player_ids = [i for i in range(self.num_snakes)]

        self.board = np.zeros([self.size, self.size])
        for i in self.player_ids:
            for tup in self.snakes[i]:
                self.board[tup[0]][tup[1]] = i + 1
        for tup in self.food:
            self.board[tup[0]][tup[1]] = FOOD

        self.food_index = 0
        self.food_xy = [(0, 5), (4, 0), (3, 2), (1, 4), (1, 1), (9, 6), (0, 6), (0, 2), (4, 0), (9, 4), (8, 8), (7, 9), (6, 2), (9, 8), (7, 4), (4, 5), (5, 4), (7, 6), (2, 0), (7, 0), (2, 1), (9, 3), (7, 9), (8, 3), (8, 4), (3, 1)]

    def move(self):
        moves = []
        #Moves the head
        for i in self.player_ids:
            snake_i = self.snakes[i]
            move_i = self.players[i].get_move(self.board, snake_i)
            moves.append(move_i)
            new_square = (snake_i[-1][0] + move_i[0], snake_i[-1][1] + move_i[1])
            snake_i.append(new_square)

        #update tail
        for i in self.player_ids:
            head_i = self.snakes[i][-1]
            if head_i not in self.food:
                self.board[self.snakes[i][0][0]][self.snakes[i][0][1]] = EMPTY
                self.snakes[i].pop(0)
            else:
                self.food.remove(head_i)

        #check out of bounds
        for i in self.player_ids:
            head_i = self.snakes[i][-1]
            if head_i[0] >= self.size or head_i[1] >= self.size or head_i[0] < 0 or head_i[1] < 0:
                self.player_ids.remove(i)
            else:
                self.board[head_i[0]][head_i[1]] = i + 1

        #check for collisons
        for i in self.player_ids:
            head_i = self.snakes[i][-1]
            for j in range(self.num_snakes):
                if i == j:
                    if head_i in self.snakes[i][:-1]:
                        self.player_ids.remove(i)

        #spawn new food
        while len(self.food) < self.num_food:
            x = self.food_xy[self.food_index][0]
            y = self.food_xy[self.food_index][1]
            while self.board[x][y] != EMPTY:
                self.food_index += 1
                x = self.food_xy[self.food_index][0]
                y = self.food_xy[self.food_index][1]
            self.food.append((x, y))
            self.board[x][y] = FOOD
            self.food_index += 1
        return moves

    def play(self, display, termination=False):
        if display:
            self.display_board()
        while True:
            if termination:
                for i in self.player_ids:
                    if len(self.snakes[0]) - self.turn / 20 <= 0:
                        self.player_ids.remove(i)
                        #remove return if more than 1 snakes
                        return -2
            if len(self.player_ids) == 0:
                return -1
            if self.turn >= self.max_turns:
                return 0
            moves = self.move()
            self.turn += 1
            if display:
                for move in moves:
                    if move == UP:
                        print("UP")
                    if move == RIGHT:
                        print("RIGHT")
                    if move == LEFT:
                        print("LEFT")
                    elif move == DOWN:
                        print("DOWN")
                self.display_board()
                if self.gui is not None:
                    self.gui.update()
                time.sleep(0.05)

    def display_board(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == EMPTY:
                    print("|_", end="")
                elif self.board[i][j] == FOOD:
                    print("|#", end="")
                else:
                    print("|" + str(int(self.board[i][j])), end="")
            print("|")


class Gui:
    def __init__(self, game, size):
        self.game = game
        self.game.gui = self
        self.size = size
        self.ratio = self.size / self.game.size


        self.app = tk.Tk()
        self.canvas = tk.Canvas(self.app, width=self.size, height=self.size)
        self.canvas.pack()

        for i in range(len(self.game.snakes)):
            color = '#' + '{0:03x}'.format((i + 1) * 500)
            snake = self.game.snakes[i]
            self.canvas.create_rectangle(self.ratio*(snake[-1][1]), self.ratio * (snake[-1][0]), self.ratio * (snake[-1][1] + 1), self.ratio * (snake[-1][0] + 1), fill=color)

            for j in range(len(snake) - 1):
                color = '#' + '{0:03x}'.format((i + 1) * 123)
                self.canvas.create_rectangle(self.ratio * (snake[j][1]), self.ratio * (snake[j][0]), self.ratio * (snake[j][1] + 1), self.ratio * (snake[j][0] + 1), fill=color)

        for food in self.game.food:
            self.canvas.create_rectangle(self.ratio * (food[1]), self.ratio * (food[0]), self.ratio * (food[1] + 1), self.ratio * (food[0] + 1), fill='#000000000')


    def update(self):
        self.canvas.delete("all")
        for i in range(len(self.game.snakes)):
            color = '#' + '{0:03x}'.format((i + 1) * 500)
            snake = self.game.snakes[i]
            self.canvas.create_rectangle(self.ratio * (snake[-1][1]), self.ratio * (snake[-1][0]), self.ratio * (snake[-1][1] + 1), self.ratio * (snake[-1][0] + 1), fill=color)

            for j in range(len(snake) - 1):
                color = '#' + '{0:03x}'.format((i + 1) * 123)
                self.canvas.create_rectangle(self.ratio * (snake[j][1]), self.ratio * (snake[j][0]), self.ratio * (snake[j][1] + 1), self.ratio * (snake[j][0] + 1), fill=color)

        for food in self.game.food:
            self.canvas.create_rectangle(self.ratio * (food[1]), self.ratio * (food[0]), self.ratio * (food[1] + 1), self.ratio * (food[0] + 1), fill='#000000000')

        self.canvas.pack()
        self.app.update()