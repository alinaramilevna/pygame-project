import os
import sys
import pygame

FPS = 50
SIZE = WIDTH, HEIGHT = 600, 450
tile_width, tile_height = 45, 45

pygame.init()
screen = pygame.display.set_mode(SIZE)


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


def generate_level(level):
    w, h = tile_width, tile_height
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '=':
                Tile('fire', x, y, w, h)
            elif level[y][x] == '%':
                Tile('ladder', x, y, w, h)
            elif level[y][x] == '-':
                Tile('platform', x, y, w, h)
            elif level[y][x] == '/':
                Tile('saw', x, y, w, h)
            elif level[y][x] == '+':
                Tile('grass', x, y, w, h)
            elif level[y][x] == '#':
                Tile('earth', x, y, w, h)
            elif level[y][x] == '@':
                xp, yp = x, y
    # вернем игрока, а также размер поля в клетках
    new_player = Player(xp, yp)
    return new_player, x, y


tile_images = {
    'grass': load_image('tiles/earth.png'),
    'earth': load_image('tiles/earth_down.png'),
    'fire': load_image('tiles/fire.png'),
    'ladder': load_image('tiles/ladder.png'),
    'platform': load_image('tiles/platforms.png'),
    'saw': load_image('tiles/saw.png')
}


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, tile_width, tile_height):
        '''Здесь будет вся неживая природа'''
        if tile_type in ['grass', 'earth', 'platforms']:
            super().__init__(tiles_group, all_sprites, walls_group)
        elif tile_type == 'fire':
            super().__init__(tiles_group, all_sprites, fire_group)
        elif tile_type == 'saw':
            super().__init__(tiles_group, all_sprites, saw_group)
        elif tile_type == 'ladder':
            super().__init__(tiles_group, all_sprites, ladders_group)
        else:
            super().__init__(tiles_group, all_sprites)
        self.image = pygame.transform.scale(tile_images[tile_type], (tile_width, tile_height))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = pygame.transform.scale(load_image('player/person.png', colorkey=(255, 255, 255)),
                                            (tile_height, tile_width))
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, move_type: str):
        old = self.rect.copy()
        if move_type is not None:
            if move_type == 'right':
                self.rect.x += tile_width
            elif move_type == 'left':
                self.rect.x -= tile_width
            elif move_type == 'up':
                self.rect.y -= tile_height
            elif move_type == 'down':
                self.rect.y += tile_height
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect = old


class Enemy(pygame.sprite.Sprite):
    pass


class Star(pygame.sprite.Sprite):
    pass


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


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


if __name__ == '__main__':
    running = True
    fps = 30
    clock = pygame.time.Clock()

    tiles_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    ladders_group = pygame.sprite.Group()
    fire_group = pygame.sprite.Group()
    saw_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    try:
        map_name = level_selection(screen, WIDTH, HEIGHT)
        player, level_x, level_y = generate_level(load_level(map_name))
        camera = Camera()
        move_type = None
    except FileNotFoundError:
        print('Файл не найден')
        sys.exit()

    while running:
        screen.fill('black')
        fon = pygame.transform.scale(load_image('other/background.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                move_type = 'right'
            elif keys[pygame.K_LEFT]:
                move_type = 'left'
            elif keys[pygame.K_UP]:
                move_type = 'up'
            elif keys[pygame.K_DOWN]:
                move_type = 'down'

        all_sprites.update(move_type)
        move_type = None
        all_sprites.draw(screen)
        player_group.draw(screen)
        camera.update(player)

        for sprite in all_sprites:
            camera.apply(sprite)

        clock.tick(fps)
        pygame.display.flip()
