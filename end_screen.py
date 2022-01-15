import os

import pygame


size = width, height = 1000, 800


def load_image(path):
    full_path = os.path.join(path)
    if not os.path.exists(full_path):
        print(f"Файл с изображением '{full_path}' не найден")
        exit()
    im = pygame.image.load(full_path)
    im = im.convert_alpha()
    return im


class Button(pygame.sprite.Sprite):
    def __init__(self, button_sprites, x, y):
        super(Button, self).__init__(button_sprites)
        self.image = load_image('EndScreen/data/иконка228.png')
        self.image = pygame.transform.scale(self.image, (width / 2, height / 4))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def show_end_screen(result, time=0):
    button_sprites = pygame.sprite.Group()
    screen = pygame.display.set_mode(size)
    screen.blit(load_image('EndScreen/data/end_screen.jpg'), (0, 0))
    pygame.font.init()
    myfont = pygame.font.SysFont('Comic Sans MS', 100)
    myfont2 = pygame.font.SysFont('Comic Sans MS', 80)
    back_in_menu = myfont2.render('В меню', False, (255, 255, 255))
    again = myfont2.render('Снова', False, (255, 255, 255))
    running = True
    but1 = Button(button_sprites, 0.25 * width, 0.4 * height)
    but2 = Button(button_sprites, 0.25 * width, 0.7 * height)
    button_sprites.add(but1)
    button_sprites.add(but2)
    while running:
        pygame.display.flip()
        if result == 'complete':
            time = str(time)[:5]
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
        button_sprites.draw(screen)
        screen.blit(back_in_menu, (0.35 * width, 0.4 * height + 35))
        screen.blit(again, (0.38 * width, 0.7 * height + 35))