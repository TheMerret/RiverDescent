import os

import pygame
from MainMenu.MainMenu import Button

__all__ = ['show_end_screen']

size = width, height = 1000, 800


def load_image(path):
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
    sc = load_image('EndScreen/data/end_screen.jpg')
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
                print(x, y)
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
            return 'menu'
        elif but2.pushed == 1:
            return 'retry'
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
