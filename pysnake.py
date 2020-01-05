#!/usr/bin/env python3
import random
from enum import Enum

import pygame
from pygame.rect import Rect
from pygame.time import Clock

SCREEN_RESOLUTION = (800, 600)
GRID_DIMENSIONS = (10, 10)
CELL_WIDTH = 20
GRID_PIXEL_DIMENSIONS = (GRID_DIMENSIONS[0] * CELL_WIDTH, GRID_DIMENSIONS[1] * CELL_WIDTH)
GRID_POSITION_ON_SCREEN = (SCREEN_RESOLUTION[0] // 2 - GRID_PIXEL_DIMENSIONS[0] // 2, 300)
COLOR_GRID = (100, 100, 100)
COLOR_SNAKE = (200, 200, 250)
COLOR_FOOD = (250, 150, 150)
COLOR_BG = (0, 0, 0)
COLOR_TEXT = (250, 250, 250)


def add_vecs(a, b):
  return a[0] + b[0], a[1] + b[1]


def mult_vec(vec, factor):
  return vec[0] * factor, vec[1] * factor


def are_vecs_opposite(a, b):
  return add_vecs(a, b) == (0, 0)


class State(Enum):
  PLAYING = 0
  DEAD = 1


class Snake:
  MOVEMENT_COOLDOWN = 200

  def __init__(self):
    self.body = [(0, GRID_DIMENSIONS[1] // 2)]
    self._next_direction = (1, 0)
    self._direction = self._next_direction
    self._time_since_movement = 0
    self._did_just_eat = False
    self.is_dead = False

  def update(self, elapsed_time):
    self._time_since_movement += elapsed_time
    if self._time_since_movement > Snake.MOVEMENT_COOLDOWN:
      self._direction = self._next_direction
      self._time_since_movement -= Snake.MOVEMENT_COOLDOWN
      head = self.body[0]
      new_head = add_vecs(head, self._direction)

      if self._did_just_eat:
        last = None
        self._did_just_eat = False
      else:
        # Only discard the last cell of the snake tail if it didn't just eat
        last = self.body.pop(len(self.body) - 1)

      self_collision = new_head in self.body
      on_grid = 0 <= new_head[0] < GRID_DIMENSIONS[0] and 0 <= new_head[1] < GRID_DIMENSIONS[1]
      if self_collision or not on_grid:
        if last:
          # It looks better visually if the snake stops dead in its track on death
          self.body.append(last)
        self.is_dead = True
        return

      self.body.insert(0, new_head)
      return new_head

  def steer_in_direction(self, direction):
    if are_vecs_opposite(direction, self._direction):
      # Cannot make a 180 degree turn in-place!
      return
    self._next_direction = direction

  def on_eat(self):
    self._did_just_eat = True


def get_random_food_position():
  x = random.randint(0, GRID_DIMENSIONS[0] - 1)
  y = random.randint(1, GRID_DIMENSIONS[1] - 1)
  return x, y


def main():
  screen = pygame.display.set_mode(SCREEN_RESOLUTION, pygame.DOUBLEBUF)
  pygame.font.init()
  snake = Snake()
  clock = Clock()
  state = State.PLAYING
  food_position = get_random_food_position()
  font = pygame.font.Font('Courier New Bold.ttf', 14)
  score = 0

  while True:

    # EVENTS
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        exit(0)
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
          snake.steer_in_direction((1, 0))
        elif event.key == pygame.K_DOWN:
          snake.steer_in_direction((0, 1))
        elif event.key == pygame.K_LEFT:
          snake.steer_in_direction((-1, 0))
        elif event.key == pygame.K_UP:
          snake.steer_in_direction((0, -1))
        elif event.key == pygame.K_RETURN:
          if state == State.DEAD:
            score = 0
            snake = Snake()
            food_position = get_random_food_position()
            state = State.PLAYING
            clock.tick()

    # GAME LOGIC
    if state == State.PLAYING:
      clock.tick()
      elapsed_time = clock.get_time()
      new_head_position = snake.update(elapsed_time)
      if snake.is_dead:
        state = State.DEAD
        print("YOU DIED!")
      if new_head_position and new_head_position == food_position:
        snake.on_eat()
        food_position = get_random_food_position()
        score += 1

    # RENDERING
    screen.fill(COLOR_BG)
    for y in range(0, GRID_DIMENSIONS[1] + 1):
      render_grid_line(screen, COLOR_GRID, (0, y), (GRID_DIMENSIONS[0], y))
    for x in range(0, GRID_DIMENSIONS[0] + 1):
      render_grid_line(screen, COLOR_GRID, (x, 0), (x, GRID_DIMENSIONS[1]))
    for cell in snake.body:
      render_filled_grid_rect(screen, COLOR_SNAKE, cell)
    if food_position:
      render_filled_grid_rect(screen, COLOR_FOOD, food_position)
    render_text(screen, font, COLOR_TEXT, "PYSNAKE", (SCREEN_RESOLUTION[0] // 2, 50))
    render_text(screen, font, COLOR_TEXT, "Score: %i" % score, (SCREEN_RESOLUTION[0] // 2, 80))
    if state == State.DEAD:
      render_text(screen, font, COLOR_TEXT, "GAME OVER! PRESS ENTER TO RESTART", (SCREEN_RESOLUTION[0] // 2, 160))
    pygame.display.flip()


def render_text(screen, font, color, text, center_position):
  width = font.size(text)[0]
  position = add_vecs(center_position, (-width // 2, 0))
  screen.blit(font.render(text, True, color), position)


def render_filled_grid_rect(screen, color, cell):
  rect = Rect(
      GRID_POSITION_ON_SCREEN[0] + cell[0] * CELL_WIDTH,
      GRID_POSITION_ON_SCREEN[1] + cell[1] * CELL_WIDTH,
      CELL_WIDTH,
      CELL_WIDTH)
  pygame.draw.rect(screen, color, rect)


def render_grid_line(screen, color, start, end):
  pygame.draw.line(
      screen,
      color,
      add_vecs(GRID_POSITION_ON_SCREEN, mult_vec(start, CELL_WIDTH)),
      add_vecs(GRID_POSITION_ON_SCREEN, mult_vec(end, CELL_WIDTH)))


if __name__ == "__main__":
  main()
