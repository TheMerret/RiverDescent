import math
import os
import random
import time
import pygame
from river_generation import RiverGeneration, ObstaclesGeneration, save_river_data, load_river_data


size = width, height = 1000, 800
river_size = 10000
river_width = 300
all_sprites = pygame.sprite.Group()
river_sprites = pygame.sprite.Group()
obst_sprites = pygame.sprite.Group()
river_curvature = 10000
levels_base_path = os.path.normpath('./river_data/levels')
current_level_id = 2
frames_count = 104


def load_image(path):
    full_path = os.path.join('assets', path)
    if not os.path.exists(full_path):
        print(f"Файл с изображением '{full_path}' не найден")
        exit()
    im = pygame.image.load(full_path)
    return im


speed = 5


class Boat(pygame.sprite.Sprite):
    def __init__(self):
        super(Boat, self).__init__(all_sprites)
        self.frame = 1
        self.image = pygame.transform.scale(load_image(f'boat/change/{self.frame}.png'), (150, 300))
        self.rect = self.image.get_rect()
        self.boat_image = self.image
        self.rect.x = width // 2 - 150 / 2
        self.rect.y = height // 2 - 300 / 2
        self.angle = 0
        self.x = width // 2
        self.y = height // 2
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

    def rotate(self):
        im = pygame.transform.scale(self.boat_image, (150, 300))
        boat_temp_image = pygame.transform.rotate(im, self.angle)
        new_rect = boat_temp_image.get_rect(center=(self.x, self.y))
        self.image = boat_temp_image
        self.rect = new_rect
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, beach1, beach2, obsts):
        if pygame.sprite.collide_mask(self, beach1) or pygame.sprite.collide_mask(self, beach2):
            return False
        for i in obsts:
            if pygame.sprite.collide_mask(self, i):
                return False
        return True


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, rect):
        super(Obstacle, self).__init__(obst_sprites)
        a = random.choice(['hut/хатка5.1.png', 'smallstone/smallstone.png', 'bigstone/bigstoun.png'])
        self.image = load_image(f'barriers/{a}')
        if a == 'smallstone/smallstone.png':
            self.image = pygame.transform.scale(self.image, (70, 70))
        elif a == 'hut/хатка5.1.png':
            self.image = pygame.transform.scale(self.image, (100, 100))
        else:
            self.image = pygame.transform.scale(self.image, (110, 110))
        self.image = pygame.transform.rotate(self.image, random.randint(-360, 360))
        self.rect = self.image.get_rect()
        self.rect.x = round(rect[0][0], 0)
        self.rect.y = round(rect[0][1], 0)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, site, angle, multiplier=2):
        a = math.radians(angle)
        b = math.radians(angle)
        if site == 'down':
            self.rect.x -= math.sin(a) * speed * multiplier
            self.rect.y -= math.cos(b) * speed * multiplier
        if site == 'up':
            self.rect.x += round(math.sin(a) * speed * multiplier, 0)
            self.rect.y += round(math.cos(b) * speed * multiplier, 0)


class Finish(pygame.sprite.Sprite):
    def __init__(self):
        super(Finish, self).__init__(river_sprites)
        self.image = pygame.transform.scale(load_image('finish.png'), (river_size, 100))
        self.rect = self.image.get_rect()
        self.rect.y = -river_size
        self.mask = pygame.mask.from_surface(self.image)


class Pier(pygame.sprite.Sprite):
    def __init__(self):
        super(Pier, self).__init__(river_sprites)
        self.image = pygame.transform.scale(load_image('pier/1.png'), (width * 1.5, 1 * height))
        self.rect = self.image.get_rect()
        self.rect.x = - 0.25 * width
        self.rect.y = 0
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, angle, multiplier=2):
        a = math.radians(angle)
        self.rect.x += round(math.sin(a) * speed * multiplier, 0)
        self.rect.y += round(math.cos(a) * speed * multiplier, 0)


class River(pygame.sprite.Sprite):
    def __init__(self, polygon):
        super(River, self).__init__(river_sprites)
        self.image = pygame.Surface([5000, 5000], pygame.SRCALPHA, 32)
        pygame.draw.polygon(self.image, 'blue', (polygon))
        self.rect = self.image.get_rect()
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, site, angle, multiplier=2):
        a = math.radians(angle)
        b = math.radians(angle)
        if site == 'down':
            self.rect.x -= math.sin(a) * speed * multiplier
            self.rect.y -= math.cos(b) * speed * multiplier
        if site == 'up':
            self.rect.x += round(math.sin(a) * speed * multiplier, 0)
            self.rect.y += round(math.cos(b) * speed * multiplier, 0)


class Beach(River):
    def __init__(self, polygon, site):
        super(River, self).__init__(river_sprites)
        self.image = pygame.Surface([river_size + width, river_size + height], pygame.SRCALPHA, 32)
        if site == 'left':
            polygon = [(river_size + width, river_size * 2)] + [(river_size + width, 0)] + polygon
            for i in range(len(polygon)):
                polygon[i] = (polygon[i][0], polygon[i][1])
        if site == 'right':
            polygon = [(-width, 0)] + [(-width, river_size * 2)] + polygon
        pygame.draw.polygon(self.image, 'orange', (polygon))
        self.rect = self.image.get_rect()
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)


def save_river_data_by_id(river_geom, obstacle_groups, identifier: int):
    file_type = '.json'
    save_path = os.path.join(levels_base_path, str(identifier) + file_type)
    save_river_data(river_geom, obstacle_groups, save_path)


def load_river_data_by_id(identifier: int):
    file_type = '.json'
    load_path = os.path.join(levels_base_path, str(identifier) + file_type)
    river_geom, obstacle_groups = load_river_data(load_path)
    return river_geom, obstacle_groups


def boat_run():
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("boat")
    screen.fill('blue')
    boat = Boat()
    save = True

    if save:
        rg = RiverGeneration(river_size, 100)
        river_geom = rg.get_river_geom(river_width, smooth=True)

        og = ObstaclesGeneration(river_geom, boat_size=(70, 300))
        obstacle_groups = og.get_obstacle_groups()
        save_river_data_by_id(river_geom, obstacle_groups, current_level_id)
    else:
        river_geom, obstacle_groups = load_river_data_by_id(current_level_id)
    obstacles = [obstacle for obstacle_group in obstacle_groups for obstacle
                 in obstacle_group.obstacles]

    a = (river_geom.left_bank, river_geom.right_bank)
    pol1, pol2 = a[0], a[1]
    delta_x = pol1[0][0] - boat.x
    delta_y = pol1[0][1] - boat.y
    beach1 = Beach(pol1, 'right')  # сюда правого берега
    beach2 = Beach(pol2, 'left')  # сюда левого береша
    pier = Pier()
    for i in obstacles:
        if random.randint(0, 2) == 1:
            obst = Obstacle(i.normalized_rect)
    beach1.rect.x = round(-delta_x - river_width, 0)
    beach2.rect.x = round(-delta_x - river_width, 0)
    beach1.rect.y = round(-delta_y, 0)
    beach2.rect.y = round(-delta_y, 0)
    for i in obst_sprites:
        i.rect.x = i.rect.x - delta_x - river_width
        i.rect.y = i.rect.y - delta_y
        i.mask = pygame.mask.from_surface(i.image)
        if pygame.sprite.collide_mask(i, beach1) or pygame.sprite.collide_mask(i, beach2):
            obst_sprites.remove(i)
    all_sprites.add(boat)
    clock = pygame.time.Clock()
    running = True
    allow_right = False
    allow_left = False
    main = ''
    cnt = 150
    pygame.font.init()
    myfont = pygame.font.SysFont('Comic Sans MS', 100)
    num = 3
    allow = False
    textsurface = myfont.render(str(num), False, (255, 255, 255))
    finish = Finish()
    river_sprites.add(finish)
    f = True
    tic = time.perf_counter()
    while running:
        if allow:
            if boat.frame < frames_count:
                boat.frame += 1
            else:
                boat.frame = 1
            boat.image = load_image(f'boat/change/{boat.frame}.png')
            boat.boat_image = boat.image
        boat.rotate()
        screen.fill('blue')
        if pygame.sprite.collide_mask(boat, finish):
            toc = time.perf_counter()
            running = False
            for i in all_sprites:
                i.kill()
            for i in river_sprites:
                i.kill()
            for i in obst_sprites:
                i.kill()
            return show_end_screen('complete', toc - tic)
        if allow_left is True:
            if boat.angle < 90:
                boat.angle += 2
        if allow_right is True:
            if boat.angle > - 90:
                boat.angle -= 2
        if allow:
            for i in obst_sprites:
                i.move('up', boat.angle)
                if i.rect.y > height:
                    obst_sprites.remove(i)
            beach1.move('up', boat.angle)
            beach2.move('up', boat.angle)
            finish.rect.x = beach1.rect.x
            finish.rect.y = beach1.rect.y
            pier.move(boat.angle)
        elif not allow:
            if cnt > 100:
                textsurface = myfont.render('3', False, (255, 255, 255))
            elif cnt > 50:
                textsurface = myfont.render('2', False, (255, 255, 255))
            elif cnt > 0:
                textsurface = myfont.render('1', False, (255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    allow_left = True
                    if allow_right is True:
                        allow_right = 'prev'
                if event.key == pygame.K_RIGHT:
                    allow_right = True
                    if allow_left is True:
                        allow_left = 'prev'

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    allow_right = False
                    if allow_left == 'prev':
                        allow_left = True
                if event.key == pygame.K_LEFT:
                    allow_left = False
                    if allow_right == 'prev':
                        allow_right = True
        if cnt > 0:
            cnt -= 1
        else:
            allow = True
            boat.update(beach1, beach2, obst_sprites)
            a = boat.update(beach1, beach2, obst_sprites)
        obst_sprites.draw(screen)
        river_sprites.draw(screen)
        all_sprites.draw(screen)
        if not allow:
            screen.blit(textsurface, (width - 100, height - 150))
        pygame.display.flip()
        if allow:
            clock.tick(50)
        if not a:
           running = False
           for i in all_sprites:
               i.kill()
           for i in river_sprites:
               i.kill()
           for i in obst_sprites:
               i.kill()
           return show_end_screen('fail')
    pygame.quit()


def load_image_2(path):
    full_path = os.path.join(path)
    if not os.path.exists(full_path):
        print(f"Файл с изображением '{full_path}' не найден")
        exit()
    im = pygame.image.load(full_path)
    im = im.convert_alpha()
    return im


class Button(pygame.sprite.Sprite):
    def __init__(self, button_sprites, x, y, pos):
        super(Button, self).__init__(button_sprites)
        self.image = load_image_2('EndScreen/data/иконка228.png')
        self.image = pygame.transform.scale(self.image, (width / 2, height / 4))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pos = pos

    def shining(self, x, y, screen):
        if self.rect.x <= x <= self.rect.x + self.rect[2] and self.rect.y <= y <= self.rect.y + self.rect[3]:
            pygame.draw.rect(screen, (0, 255, 50), (self.rect.x - 3, self.rect.y - 3, self.rect[2] + 6, self.rect[3] + 6))

    def click(self, x, y):
        if self.rect.x <= x <= self.rect.x + self.rect[2] and self.rect.y <= y <= self.rect.y + self.rect[3]:
            return self.pos


def show_end_screen(result, time=0):
    button_sprites = pygame.sprite.Group()
    screen = pygame.display.set_mode(size)
    sc = load_image_2('EndScreen/data/end_screen.jpg')
    screen.blit(sc, (0, 0))
    pygame.font.init()
    myfont = pygame.font.SysFont('Comic Sans MS', 100)
    myfont2 = pygame.font.SysFont('Comic Sans MS', 80)
    back_in_menu = myfont2.render('В меню', False, (255, 255, 255))
    again = myfont2.render('Снова', False, (255, 255, 255))
    running = True
    but1 = Button(button_sprites, 0.25 * width, 0.4 * height, 'menu')
    but2 = Button(button_sprites, 0.25 * width, 0.7 * height, 'again')
    button_sprites.add(but1)
    button_sprites.add(but2)
    x, y = 0, 0
    a = ''
    while running:
        screen.blit(sc, (0, 0))
        if result == 'complete':
            time = str(time)[:5].replace('.', ':')
            time_surface = myfont2.render(f'Ваше время {time} сек', False, (255, 255, 255))
            textsurface = myfont.render('Вы прошли уровень!', False, (255, 255, 255))
            screen.blit(textsurface, (3, 0))
            screen.blit(time_surface, (70, 150))
        if result == 'fail':
            textsurface = myfont.render('Вы разбили лодку(', False, (255, 255, 255))
            screen.blit(textsurface, (60, 80))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x1, y1 = event.pos
                a = but1.click(x1, y1)
                b = but2.click(x1, y1)
                if b == 'again':
                    return boat_run()
                if a == 'menu':
                    return
        but1.shining(x, y, screen)
        but2.shining(x, y, screen)
        button_sprites.draw(screen)
        screen.blit(back_in_menu, (0.35 * width, 0.4 * height + 35))
        screen.blit(again, (0.38 * width, 0.7 * height + 35))
        pygame.display.flip()
    pygame.quit()


boat_run()