import os
import sys
from random import randrange

import pygame

FPS = 30
SIZE = WIDTH, HEIGHT = 600, 450
tile_width, tile_height = 45, 45
GRAVITY = 0.7
jump_power = tile_width * 1.7

pygame.init()
screen = pygame.display.set_mode(SIZE)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
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
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
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
            elif level[y][x] == '*':
                Enemy(x, y)
            elif level[y][x] == '@':
                xp, yp = x * w, y * h
    # вернем игрока, а также размер поля в клетках
    new_player = Player()
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
        if tile_type in ['grass', 'earth', 'platform']:
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
    def __init__(self):
        super().__init__(player_group, all_sprites)
        self.image = pygame.transform.scale(load_image('player/stand.png', colorkey=(255, 255, 255)),
                                            (tile_height, tile_width))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.frames = {'attack': 9, 'hurt': 4, 'jump': 6,
                       'stand': 1, 'walking': 7,
                       'attack_l': 9, 'hurt_l': 4, 'jump_l': 6,
                       'stand_l': 1, 'walking_l': 7,
                       }
        self.load_images()
        self.frames_cnt = 0

        self.is_grounded = False
        self.vx = 10
        self.is_jump = False
        self.jump_cnt = 0
        self.vy = 0

        # stand - стоит, attack - атакует, hurt - получает урон, jump - прыгает, walking - идет; аналогично с walking_l и др
        self.status = ['stand', 'stand']

        self.ис_ударилась_головой_об_что_нибудь_сверху = False

        self.health = 100
        self.damage = 20

    def load_images(self):
        for key in self.frames:
            n = self.frames[key]
            clrkey = 'white' if 'stand' in key else 'black'
            if '_l' not in key:
                self.frames[key] = self.cut_sheet(
                    load_image(f'player/{key}.png', colorkey=clrkey), n, 1)
            else:
                orig = self.cut_sheet(
                    load_image(f'player/{key[:-2]}.png', colorkey=clrkey), n, 1)
                for i in range(n):
                    orig[i] = pygame.transform.flip(orig[i], True, False)
                self.frames[key] = orig

    def cut_sheet(self, sheet, columns, rows):
        frames = []
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
        return frames

    def death(self):  # TODO
        self.kill()

    def hurt(self):
        self.health -= 0.1
        self.status.append('hurt_l' if '_l' in self.status[-2] else 'hurt')

    def update(self, move_type):
        self.frames_cnt += 1
        self.check_collision_y()

        if self.health <= 0:
            self.death()

        if move_type is not None:

            if move_type == 'right':
                if self.status[-2] != 'walking':
                    self.frames_cnt = 0
                self.step_right()
                self.status.append('walking')

            elif move_type == 'left':
                if self.status[-2] != 'walking_l':
                    self.frames_cnt = 0
                self.step_left()
                self.status.append('walking_l')

            elif move_type == 'down':
                self.go_down_the_ladder()

            elif move_type == 'jump':
                if pygame.sprite.spritecollideany(self, ladders_group):
                    self.go_up_the_ladder()
                else:
                    if self.status[-2] != 'jump':
                        self.frames_cnt = 0
                    self.jump()
                    self.status.append('jump')

            elif move_type == 'attack':
                if self.status[-2][-1] == 'l':
                    status = 'attack_l'
                else:
                    status = 'attack'

                if self.status[-2] != status:
                    self.frames_cnt = 0
                self.status.append(status)
                self.attack()

        self.gravitation()
        self.cur_frame = self.frames[self.status[-1]][self.frames_cnt % len(self.frames[self.status[-1]])]
        self.image = self.cur_frame
        self.status.append('stand' if self.status[-1][-1] != 'l' else 'stand_l')

    def step_right(self):
        old = self.rect.copy()
        self.rect.x += self.vx
        for wall in walls_group:
            if pygame.sprite.collide_mask(self, wall):
                self.rect = old
                self.is_jump = False
                return

    def step_left(self):
        old = self.rect.copy()
        self.rect.x -= self.vx
        for wall in walls_group:
            if pygame.sprite.collide_mask(self, wall):
                self.rect = old
                self.is_jump = False
                return

    def go_down_the_ladder(self):
        self.rect.y += tile_height
        for ladder in ladders_group:
            if pygame.sprite.collide_mask(self, ladder):
                for wall in walls_group:
                    while pygame.sprite.collide_mask(self, wall):
                        self.rect.y -= 1
                return
        else:
            self.rect.y -= tile_height

    def go_up_the_ladder(self):
        self.rect.y -= tile_height // 2

    def jump(self):
        self.rect.y += 2
        if pygame.sprite.spritecollideany(self, tiles_group):
            self.is_jump = True
            self.vy = 1
            self.jump_cnt = 0
        else:
            self.is_jump = False
        self.rect.y -= 2

    def check_collision_y(self):
        # есть ли что-то сверху
        self.rect.y -= tile_height
        if pygame.sprite.spritecollideany(self, walls_group) or \
                pygame.sprite.spritecollideany(self, ladders_group) or pygame.sprite.spritecollideany(self, fire_group):
            self.rect.y += tile_height
            self.ис_ударилась_головой_об_что_нибудь_сверху = True
            self.vy = -self.vy
            self.is_jump = False
        else:
            self.rect.y += tile_height
            self.ис_ударилась_головой_об_что_нибудь_сверху = False

    def gravitation(self):
        if self.is_jump and self.jump_cnt <= 60:
            self.vy -= GRAVITY
            self.rect.y += self.vy
            self.jump_cnt += 5
            if pygame.sprite.spritecollideany(self, tiles_group):
                self.rect.y -= self.vy
                self.vy = 0
                self.is_jump = False
                self.jump_cnt = 0
        else:
            self.vy += GRAVITY
            self.rect.y += self.vy
            if pygame.sprite.spritecollideany(self, tiles_group):
                if pygame.sprite.spritecollideany(self, fire_group):
                    self.hurt()
                self.rect.y -= self.vy
                self.vy = 0
                return

    def attack(self):
        for enemy in enemy_group:
            if abs(enemy.rect.x - self.rect.x) <= 40:
                enemy.health -= self.damage
            if enemy.health <= 0:
                enemy.kill()


def draw_health(obj: Player):
    rect = pygame.Rect(WIDTH // 10, HEIGHT // 16, WIDTH // 2 - WIDTH // 8, HEIGHT // 14)
    pygame.draw.rect(screen, 'black', rect, 2)

    im = load_image('other/heart.png', colorkey=-1)
    curr_x, curr_y = WIDTH // 15, HEIGHT // 24
    for _ in range(int((obj.health + 9) // 10)):
        screen.blit(im, (curr_x, curr_y))
        curr_x += WIDTH // 27


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group)

        self.health = 40
        self.damage = 3
        self.vx = randrange(1, 4)

        self.frames = []
        self.frames_l = []

        self.cut_sheet(self.frames, load_image('enemy/walking.png'), 7, 1)
        self.cut_sheet(self.frames_l, pygame.transform.flip(load_image('enemy/walking.png'), True, False), 7, 1)
        self.cur_frame = 0
        self.attack_time_cnt = 0

        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(pos_x, pos_y)

        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, arr: list, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                arr.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.go_to_the_player(args[0])
        if self.health <= 0:
            self.kill()
        self.attack()

    def go_to_the_player(self, player: Player):
        if player.rect.x - tile_width < self.rect.x:
            self.image = self.frames_l[self.cur_frame]
            self.rect.x -= self.vx
        elif player.rect.x - tile_width > self.rect.x:
            self.image = self.frames[self.cur_frame]
            self.rect.x += self.vx
        if player.rect.y - tile_height > self.rect.y:
            self.rect.y += 1
        elif player.rect.y - tile_height < self.rect.y:
            self.rect.y -= 1

    def attack(self):
        for player in player_group:
            if pygame.sprite.collide_mask(self, player):
                self.attack_time_cnt += 1
                player.health -= self.damage if self.attack_time_cnt % 10 == 0 else 0
                player.hurt()


class Star(pygame.sprite.Sprite):
    pass


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

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
                    return 'map1.txt'
                elif curr_x <= x <= curr_x + rect_w and curr_y - distance_rect <= y <= curr_y + rect_h:
                    return 'map2.txt'
        pygame.display.flip()


def screen_of_death(surface, width, height):
    '''Выбор уровня'''
    intro_text = ['Вы умерли!',
                  'Попробовать снова',
                  'Выход']

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
                    return 'map1.txt'
                elif curr_x <= x <= curr_x + rect_w and curr_y - distance_rect <= y <= curr_y + rect_h:
                    return 'map2.txt'
        pygame.display.flip()


def start_game():
    global running, move_type
    screen.fill('black')
    fon = pygame.transform.scale(load_image('other/background.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    draw_health(player)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        move_type = 'right'
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        move_type = 'left'
    elif keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]:
        move_type = 'jump'
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        move_type = 'down'
    elif keys[pygame.K_r]:
        move_type = 'attack'

    all_sprites.update(move_type)
    move_type = None
    all_sprites.draw(screen)
    player_group.draw(screen)
    enemy_group.update(player)
    enemy_group.draw(screen)
    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)
    for sprite in enemy_group:
        camera.apply(sprite)

    clock.tick(FPS)
    pygame.display.flip()


if __name__ == '__main__':
    running = True
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
        # map_name = level_selection(screen, WIDTH, HEIGHT)
        map_name = 'map1.txt'
        player, level_x, level_y = generate_level(load_level(map_name))
        camera = Camera()
        move_type = None
    except FileNotFoundError:
        print('Файл не найден')
        sys.exit()

    while running:
        start_game()
