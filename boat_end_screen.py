import math
import os
import random
import time
import pygame
from MainMenu.MainMenu import *
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


def boat_run(screen, level_id):
    pygame.display.set_caption("boat")
    screen.fill('blue')
    boat = Boat()
    save = False

    if save:
        rg = RiverGeneration(river_size, 100)
        river_geom = rg.get_river_geom(river_width, smooth=True)

        og = ObstaclesGeneration(river_geom, boat_size=(boat_width, 300))
        obstacle_groups = og.get_obstacle_groups()
        save_river_data_by_id(river_geom, obstacle_groups, level_id)
    else:
        river_geom, obstacle_groups = load_river_data_by_id(level_id)
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
            show_end_screen('complete', toc - tic)
        if allow_left:
            if boat.angle < 90:
                boat.angle += 2
        if allow_right:
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
                if event.key == pygame.K_LEFT and not allow_right:
                    allow_left = True
                if event.key == pygame.K_RIGHT and not allow_left:
                    allow_right = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    allow_right = False
                if event.key == pygame.K_LEFT:
                    allow_left = False
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


def load_image2(path):
    full_path = os.path.join(path)
    if not os.path.exists(full_path):
        print(f"Файл с изображением '{full_path}' не найден")
        exit()
    im = pygame.image.load(full_path)
    im = im.convert_alpha()
    return im


def func():
    pass


def show_end_screen(result, time=0):
    button_sprites = pygame.sprite.Group()
    screen = pygame.display.set_mode(size)
    sc = load_image2('EndScreen/data/end_screen.jpg')
    screen.blit(sc, (0, 0))
    pygame.font.init()
    myfont = pygame.font.SysFont('Comic Sans MS', 100)
    myfont2 = pygame.font.SysFont('Comic Sans MS', 80)
    back_in_menu = myfont2.render('В меню', False, (255, 255, 255))
    again = myfont2.render('Снова', False, (255, 255, 255))
    running = True
    but1 = Button(0.25 * width, 0.4 * height, width / 2, height / 4, screen, 2, 1,
                  imagepath="EndScreen\\data",
                  imagename="иконка228.png", ONtext="В меню", ONtextcolor=(34, 139, 34),
                  groups=(button_sprites,))
    but2 = Button(0.25 * width, 0.7 * height, width / 2, height / 4, screen, 2, 2,
                  imagepath="EndScreen\\data",
                  imagename="иконка228.png", ONtext="Снова", ONtextcolor=(34, 139, 34),
                  groups=(button_sprites,))
    but1.signal.connect(func)
    but2.signal.connect(func)
    x, y = 0, 0
    flagDown = 0
    flagUp = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                Button.xm, Button.ym = event.pos
                x, y = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    flagDown = 1
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    flagUp = 1
        if flagDown and flagUp:
            if 0.25 * width < x < 0.25 * width + width / 2 and 0.4 * height < y < 0.4 * height + height / 4:
                but1.pushed = 1
            elif 0.25 * width < x < 0.25 * width + width / 2 and 0.7 * height < y < 0.7 * height + height / 4:
                but2.pushed = 1
            flagDown, flagUp = 0, 0
        else:
            Button.pushed = 0
        if but1.pushed == 1:
            return
        elif but2.pushed == 1:
            return boat_run(screen, 1)
        screen.blit(sc, (0, 0))
        if result == 'complete':
            time = str(time)[:5]
            time_surface = myfont2.render(f'Ваше время {time} сек', False, (255, 255, 255))
            textsurface = myfont.render('Вы прошли уровень!', False, (255, 255, 255))
            screen.blit(textsurface, (3, 0))
            screen.blit(time_surface, (70, 150))
        if result == 'fail':
            textsurface = myfont.render('Вы разбили лодку(', False, (255, 255, 255))
            screen.blit(textsurface, (60, 80))
        button_sprites.draw(screen)
        button_sprites.update()
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    screen = pygame.display.set_mode(size)
    boat_run(screen, 1)