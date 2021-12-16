import math

import pygame
import os


def load_image(path):
    full_path = os.path.join('data', path)
    if not os.path.exists(full_path):
        print(f"Файл с изображением '{full_path}' не найден")
        exit()
    im = pygame.image.load(full_path)
    return im


def boat_run():
    pygame.init()
    size = width, height = 1000, 800
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("boat")
    screen.fill('blue')
    boat_image = load_image('boat.png')
    x, y = boat_image.get_size()
    all_sprites = pygame.sprite.Group()
    boat = pygame.sprite.Sprite()
    boat.image = boat_image
    boat.rect = boat_image.get_rect()
    boat.rect.x = width // 2 - x / 2
    boat.rect.y = height // 2 - y / 2
    x = width // 2
    y = height // 2
    all_sprites.add(boat)
    clock = pygame.time.Clock()
    running = True
    allow_right = False
    allow_left = False
    allow_up = False
    allow_down = False
    angle = 0
    speed = 5
    while running:
        boat_temp_image = pygame.transform.rotate(boat_image, angle)
        new_rect = boat_temp_image.get_rect(center=(x, y))
        boat.image = boat_temp_image
        boat.rect = new_rect
        screen.fill('blue')
        if allow_right:
            angle -= 2
        elif allow_left:
            angle += 2
        if allow_up:
            a = math.radians(-angle)
            b = math.radians(-angle)
            x += math.sin(a) * speed
            y -= math.cos(b) * speed
        if allow_down:
            a = math.radians(-angle)
            b = math.radians(-angle)
            x -= math.sin(a) * speed
            y += math.cos(b) * speed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    allow_right = True
                elif event.key == pygame.K_LEFT:
                    allow_left = True
                elif event.key == pygame.K_UP:
                    allow_up = True
                elif event.key == pygame.K_DOWN:
                    allow_down = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    allow_right = False
                elif event.key == pygame.K_LEFT:
                    allow_left = False
                elif event.key == pygame.K_UP:
                    allow_up = False
                elif event.key == pygame.K_DOWN:
                    allow_down = False
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()


boat_run()