import os
import pygame
from boat import boat_run


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
    def __init__(self, button_sprites, x, y, pos):
        super(Button, self).__init__(button_sprites)
        self.image = load_image('EndScreen/data/иконка228.png')
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
            if self.pos == 'again':
                pass
            if self.pos == 'menu':
                return


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
    but1 = Button(button_sprites, 0.25 * width, 0.4 * height, 'menu')
    but2 = Button(button_sprites, 0.25 * width, 0.7 * height, 'again')
    button_sprites.add(but1)
    button_sprites.add(but2)
    x, y = 0, 0
    while running:
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x1, y1 = event.pos
                but1.click(x1, y1)
                but2.click(x1, y1)
        but1.shining(x, y, screen)
        but2.shining(x, y, screen)
        button_sprites.draw(screen)
        screen.blit(back_in_menu, (0.35 * width, 0.4 * height + 35))
        screen.blit(again, (0.38 * width, 0.7 * height + 35))
        pygame.display.flip()
    pygame.quit()