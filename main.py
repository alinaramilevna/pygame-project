import os
import random
import sys
import pygame
from functions import *




FPS = 50
SIZE = WIDTH, HEIGHT = 400, 500

pygame.init()
screen = pygame.display.set_mode(SIZE)
tile_width = tile_height = 50





class Tile(pygame.sprite.Sprite):
    pass


class Player(pygame.sprite.Sprite):
    pass


def generate_level(level):
    pass


if __name__ == '__main__':
    running = True
    fps = 30
    clock = pygame.time.Clock()

    tiles_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    map = level_selection(screen, WIDTH, HEIGHT)
    player, level_x, level_y = generate_level(load_level(map))
    move_type = None

    while running:
        screen.fill('black')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update(move_type)
        move_type = None
        all_sprites.draw(screen)
        player_group.draw(screen)
        clock.tick(fps)
        pygame.display.flip()
