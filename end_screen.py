import pygame


size = width, height = 1000, 800
screen = pygame.display.set_mode(size)
screen.blit()
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 100)
result = 'complete'
running = True
while running:
    pygame.display.flip()
    if result == 'complete':
        textsurface = myfont.render('Вы прошли уровень!', False, (255, 255, 255))
    if result == 'fail':
        textsurface = myfont.render('Вы разбились(', False, (255, 255, 255))
    screen.blit(textsurface, (3, 100))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False