#!/usr/bin/env python3
import random
from enum import Enum

import pygame
from pygame.rect import Rect
from pygame.time import Clock

SCREEN_RESOLUTION = (800, 600)

COLOR_GRID = (100, 100, 100)
COLOR_SNAKE = (200, 200, 250)
COLOR_FOOD = (250, 150, 150)
COLOR_BG = (0, 0, 0)
COLOR_TEXT = (250, 250, 250)
COLOR_GRID_BORDER_PLAYING = (100, 100, 200)
COLOR_GRID_BORDER_DEAD = (200, 70, 70)


class Grid:
  def __init__(self, cell_size, dimensions, y):
    self.dimensions = dimensions
    self._screen_position = (0, y)
    self.cell_size = cell_size
    self._center()

  def set_width(self, width):
    self.dimensions = (width, self.dimensions[1])
    self._center()

  def set_height(self, height):
    self.dimensions = (self.dimensions[0], height)
    self._center()

  def set_cell_size(self, cell_size):
    self.cell_size = cell_size
    self._center()

  def _center(self):
    self._screen_position = (SCREEN_RESOLUTION[0] // 2 - self.dimensions[0] * self.cell_size // 2,
                             self._screen_position[1])

  def get_random_food_position(self):
    x = random.randint(0, self.dimensions[0] - 1)
    y = random.randint(1, self.dimensions[1] - 1)
    return x, y

  def render_filled_rect(self, screen, color, cell):
    rect = Rect(
        self._screen_position[0] + cell[0] * self.cell_size,
        self._screen_position[1] + cell[1] * self.cell_size,
        self.cell_size,
        self.cell_size)
    pygame.draw.rect(screen, color, rect)

  def render_line(self, screen, color, start, end):
    pygame.draw.line(
        screen,
        color,
        add_vecs(self._screen_position, mult_vec(start, self.cell_size)),
        add_vecs(self._screen_position, mult_vec(end, self.cell_size)))

  def render_border(self, screen, color):
    rect = Rect(self._screen_position[0],
                self._screen_position[1],
                self.dimensions[0] * self.cell_size,
                self.dimensions[1] * self.cell_size)
    pygame.draw.rect(screen, color, rect, 1)


class NumberInput:
  COLOR_BG = (50, 50, 50)
  COLOR_BORDER = (250, 250, 250)

  def __init__(self, rect, font, label, value, allowed_values):
    button_width = 40
    padding = 2
    self._rect = Rect(rect.x + button_width + padding, rect.y, rect.w - button_width * 2 - padding * 2, rect.h)
    self._button_minus = Rect(self._rect.x - button_width - padding, rect.y, button_width, rect.h)
    self._button_plus = Rect(self._rect.x + self._rect.w + padding, rect.y, button_width, rect.h)
    self._font = font
    self._label = label
    self._value = value
    self._allowed_values = allowed_values

  def render(self, screen):
    text = self._label + ": " + str(self._value)
    self._render_rect(screen, self._rect, text)
    self._render_rect(screen, self._button_minus, "-")
    self._render_rect(screen, self._button_plus, "+")

  def _render_rect(self, screen, rect, text):
    pygame.draw.rect(screen, NumberInput.COLOR_BG, rect)
    pygame.draw.rect(screen, NumberInput.COLOR_BORDER, rect, 1)
    text_position = (rect.x + rect.w // 2 - self._font.size(text)[0] // 2, rect.y + 2)
    screen.blit(self._font.render(text, True, COLOR_TEXT), text_position)

  def handle_mouse_click(self, mouse_position):
    new_value = None
    if self._button_minus.collidepoint(mouse_position[0], mouse_position[1]):
      new_value = self._value - 1
    if self._button_plus.collidepoint(mouse_position[0], mouse_position[1]):
      new_value = self._value + 1
    if new_value is not None and self._allowed_values[0] <= new_value <= self._allowed_values[1]:
      self._value = new_value
      return self._value

  def get_value(self):
    return self._value


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

  def __init__(self, position, speed):
    self.body = [position]
    self._next_direction = (1, 0)
    self._direction = self._next_direction
    self._time_since_movement = 0
    self._did_just_eat = False
    self.is_dead = False
    self._movement_cooldown = 1000 // speed

  def set_speed(self, speed):
    self._movement_cooldown = 1000 // speed

  def update(self, elapsed_time, grid_dimensions):
    self._time_since_movement += elapsed_time
    if self._time_since_movement > self._movement_cooldown:
      self._direction = self._next_direction
      self._time_since_movement -= self._movement_cooldown
      head = self.body[0]
      new_head = add_vecs(head, self._direction)

      if self._did_just_eat:
        last = None
        self._did_just_eat = False
      else:
        # Only discard the last cell of the snake tail if it didn't just eat
        last = self.body.pop(len(self.body) - 1)

      self_collision = new_head in self.body
      on_grid = 0 <= new_head[0] < grid_dimensions[0] and 0 <= new_head[1] < grid_dimensions[1]
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


def main():
  screen = pygame.display.set_mode(SCREEN_RESOLUTION, pygame.DOUBLEBUF)
  pygame.font.init()
  default_speed = 10
  grid = Grid(20, (10, 10), 150)
  snake = Snake((0, grid.dimensions[1] // 2), default_speed)
  clock = Clock()
  state = State.PLAYING
  font = pygame.font.Font('Courier New Bold.ttf', 14)
  score = 0
  width = 200
  food_position = grid.get_random_food_position()
  input_speed = NumberInput(
      rect=Rect(SCREEN_RESOLUTION[0] // 2 - width // 2, 475, width, 20),
      font=font,
      label="SPEED",
      value=default_speed,
      allowed_values=(1, 40))
  input_width = NumberInput(
      rect=Rect(SCREEN_RESOLUTION[0] // 2 - width // 2, 500, width, 20),
      font=font,
      label="WIDTH",
      value=grid.dimensions[0],
      allowed_values=(5, 60))
  input_height = NumberInput(
      rect=Rect(SCREEN_RESOLUTION[0] // 2 - width // 2, 525, width, 20),
      font=font,
      label="HEIGHT",
      value=grid.dimensions[1],
      allowed_values=(5, 30))
  input_cell_size = NumberInput(
      rect=Rect(SCREEN_RESOLUTION[0] // 2 - width // 2, 550, width, 20),
      font=font,
      label="CELL",
      value=grid.cell_size,
      allowed_values=(10, 40))

  while True:

    # EVENTS
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        exit_game()
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          exit_game()
        elif event.key == pygame.K_RIGHT:
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
            snake = Snake((0, grid.dimensions[1] // 2), input_speed.get_value())
            food_position = grid.get_random_food_position()
            state = State.PLAYING
            clock.tick()
      elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_position = pygame.mouse.get_pos()
        new_speed = input_speed.handle_mouse_click(mouse_position)
        if new_speed is not None:
          snake.set_speed(new_speed)
        new_width = input_width.handle_mouse_click(mouse_position)
        if new_width is not None:
          grid.set_width(new_width)
        new_height = input_height.handle_mouse_click(mouse_position)
        if new_height is not None:
          grid.set_height(new_height)
        new_cell_size = input_cell_size.handle_mouse_click(mouse_position)
        if new_cell_size is not None:
          grid.set_cell_size(new_cell_size)

    # GAME LOGIC
    if state == State.PLAYING:
      clock.tick()
      elapsed_time = clock.get_time()
      new_head_position = snake.update(elapsed_time, grid.dimensions)
      if snake.is_dead:
        state = State.DEAD
        print("YOU DIED!")
      if new_head_position and new_head_position == food_position:
        snake.on_eat()
        food_position = grid.get_random_food_position()
        score += 1

    # RENDERING
    screen.fill(COLOR_BG)
    for y in range(0, grid.dimensions[1] + 1):
      grid.render_line(screen, COLOR_GRID, (0, y), (grid.dimensions[0], y))
    for x in range(0, grid.dimensions[0] + 1):
      grid.render_line(screen, COLOR_GRID, (x, 0), (x, grid.dimensions[1]))
    for cell in snake.body:
      grid.render_filled_rect(screen, COLOR_SNAKE, cell)
    if food_position:
      grid.render_filled_rect(screen, COLOR_FOOD, food_position)
    border_color = COLOR_GRID_BORDER_PLAYING if state == State.PLAYING else COLOR_GRID_BORDER_DEAD
    grid.render_border(screen, border_color)
    render_text(screen, font, COLOR_TEXT, "PYSNAKE", (SCREEN_RESOLUTION[0] // 2, 20))
    render_text(screen, font, COLOR_TEXT, "Score: %i" % score, (SCREEN_RESOLUTION[0] // 2, 40))
    if state == State.DEAD:
      render_text(screen, font, COLOR_TEXT, "GAME OVER! PRESS ENTER TO RESTART", (SCREEN_RESOLUTION[0] // 2, 100))
    input_speed.render(screen)
    input_width.render(screen)
    input_height.render(screen)
    input_cell_size.render(screen)
    pygame.display.flip()


def exit_game():
  pygame.quit()
  exit(0)


def render_text(screen, font, color, text, center_position):
  width = font.size(text)[0]
  position = add_vecs(center_position, (-width // 2, 0))
  screen.blit(font.render(text, True, color), position)


if __name__ == "__main__":
  main()
