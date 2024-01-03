import os
import sys

import pygame


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def level_selection(surface, width, height):
    '''Выбор уровня'''
    intro_text = ['1 level',
                  '2 level']

    fon = pygame.transform.scale(load_image('start_screen.jpg'), (width, height))
    surface.blit(fon, (0, 0))

    curr_x, curr_y = 70, 100
    rect_w, rect_h = 130, 40
    distance_rect = 60
    for i in range(2):
        rect = pygame.Rect(curr_x, curr_y, rect_w, rect_h)
        pygame.draw.rect(surface, pygame.Color('dark blue'), rect, 0)
        curr_y += distance_rect

    font = pygame.font.Font(None, 30)
    text_coord = 65
    distance_text = 43
    for line in intro_text:
        string_rendered = font.render(line, 1, (98, 99, 155))
        intro_rect = string_rendered.get_rect()
        text_coord += distance_text
        intro_rect.top = text_coord
        intro_rect.x = curr_x + 23
        text_coord += intro_rect.height
        surface.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if curr_x <= x <= curr_x + rect_w and 100 <= y <= 100 + rect_h:  # 100 - самый первый у для прямоугольников
                    # print(1)
                    return 'map1.txt'
                elif curr_x <= x <= curr_x + rect_w and curr_y - distance_rect <= y <= curr_y + rect_h:
                    # print(2)
                    return 'map2.txt'
        pygame.display.flip()
