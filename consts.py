import pygame

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

FPS = 30
SIZE = WIDTH, HEIGHT = 600, 450
tile_width, tile_height = 45, 45
GRAVITY = 0.7
jump_power = tile_width * 1.7

path_to_sounds = 'data/sounds/'

get_star_sound = pygame.mixer.Sound(path_to_sounds + 'star.ogg')
hurt_sound = pygame.mixer.Sound(path_to_sounds + 'fires_sound.ogg')
jump_sound = pygame.mixer.Sound(path_to_sounds + 'jump.ogg')
sword_hit_sound = pygame.mixer.Sound(path_to_sounds + 'sword_hit.ogg')
