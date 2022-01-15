import os
import sys
import pygame

pygame.init()
FPS = 20

WIDTH = 1000
HEIGHT = 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
buttons = pygame.sprite.Group()
x, y = 0, 0


def load_image(name, color_key=None, way_to_file="try\\left"):
    fullname = os.path.join(way_to_file, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Button(pygame.sprite.Sprite):
    xm, ym, pushed = None, None, 0
    def __init__(self, x, y, w, h, screen, signaltype, signal,
                 imagepath=None, imagename=None,
                 ONtext=None, ONfontsize=60, ONtextcolor=(100, 255, 100),
                 UNDERtext=None, UNDERfontsize=30, UNDERtextcolor=(100, 255, 100)):
        super().__init__(all_sprites, buttons)
        self.screen = screen
        self.signaltype, self.signal = signaltype, signal
        self.x, self.y, self.w, self.h = x, y, w, h
        self.imagepath, self.imagename = imagepath, imagename
        self.ONtext, self.ONfontsize, self.ONtextcolor = ONtext, ONfontsize, ONtextcolor
        self.UNDERtext, self.UNDERfontsize, self.UNDERtextcolor = UNDERtext, UNDERfontsize, UNDERtextcolor
        self.xm, self.ym = None, None

        self.rect = pygame.Rect((0, 0), (self.w, self.h))
        self.rect = self.rect.move(x, y)

        if self.imagepath and self.imagename:
            self.image = self.load_image(self.imagename, way_to_file=self.imagepath)
            self.image = pygame.transform.scale(self.image, (self.w, self.h))
            self.image = self.image.subsurface(pygame.Rect((0, 0), self.rect.size))

        pygame.draw.rect(self.screen, self.ONtextcolor, (self.x - 2, self.y - 2,
                                               self.w + 4, self.h + 4), 1)

        if self.ONtext:
            self.ONfont = pygame.font.Font(None, self.ONfontsize)
            self.ONrendertext = self.ONfont.render(self.ONtext, True, self.ONtextcolor)
            self.ONw = self.ONrendertext.get_width()
            self.ONh = self.ONrendertext.get_height()
            self.ONx = self.x + self.w // 2 - self.ONw // 2
            self.ONy = self.y + self.h // 2 - self.ONh // 2
            self.screen.blit(self.ONrendertext, (self.ONx, self.ONy))

        if self.UNDERtext:
            self.UNDERfont = pygame.font.Font(None, self.UNDERfontsize)
            self.UNDERrendertext = self.UNDERfont.render(self.UNDERtext, True, self.UNDERtextcolor)
            self.UNDERw = self.UNDERrendertext.get_width()
            self.UNDERh = self.UNDERrendertext.get_height()
            self.UNDERx = self.x + self.w // 2 - self.UNDERw // 2
            self.UNDERy = self.y + self.h + int(self.h * 0.06)
            self.screen.blit(self.UNDERrendertext, (self.UNDERx, self.UNDERy))

    def update(self):
        self.pushed = Button.pushed
        self.xm, self.ym = Button.xm, Button.ym
        self.image = self.image.subsurface(pygame.Rect((0, 0), self.rect.size))
        if self.xm and self.ym:
            if self.x <= self.xm <= self.x + self.w and self.y <= self.ym <= self.y + self.h:
                pygame.draw.rect(self.screen, self.ONtextcolor, (int(self.x - self.h * 0.05),
                                                                 int(self.y - self.h * 0.05),
                                                                 int(self.w + self.h * 0.1),
                                                                 int(self.h + self.h * 0.1)), 1)
                if self.pushed:
                    self.send_signal()
            else:
                pygame.draw.rect(self.screen, self.ONtextcolor, (self.x - 2, self.y - 2,
                                                                 self.w + 4, self.h + 4), 1)
        self.screen.blit(self.UNDERrendertext, (self.UNDERx, self.UNDERy))
        self.screen.blit(self.ONrendertext, (self.ONx, self.ONy))

    def load_image(self, name, color_key=None, way_to_file="try\\left"):
        fullname = os.path.join(way_to_file, name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as message:
            print('Cannot load image:', name)
            raise SystemExit(message)
        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image = image.convert_alpha()
        return image

    def send_signal(self):
        print(self.signaltype, self.signal)


counting = 0
for i in range(300, 750, 250):
    for j in range(120, 880, 130):
        counting += 1
        button = Button(j, i, 100, 100, screen, 1, counting, imagepath="data", imagename="иконка228.png", ONtext=f"{counting}",
                ONtextcolor=(34, 139, 34), UNDERtext=f"level {counting}", UNDERtextcolor=(232, 194, 44))


running = True
flagDown = 0
flagUp = 0
while running:
    WIDTH, HEIGHT = pygame.display.get_window_size()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            Button.xm, Button.ym = event.pos
            x, y = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                flagDown = 1
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                flagUp = 1
    if flagDown and flagUp:
        Button.pushed = 1
        flagDown, flagUp = 0, 0
    else:
        Button.pushed = 0
    screen.fill(pygame.Color("white"))
    image = screen.blit(load_image("123.png", way_to_file="data"), pygame.Rect((0, 0), (WIDTH, HEIGHT)))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(FPS)
