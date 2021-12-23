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
    sliding = False
    direction = ''
    sliding_counter = 60
    angle = 0
    speed = 5
    while running:
        boat_temp_image = pygame.transform.rotate(boat_image, angle)
        new_rect = boat_temp_image.get_rect(center=(x, y))
        boat.image = boat_temp_image
        boat.rect = new_rect
        screen.fill('blue')
        if allow_left and not allow_right:
            angle += 2
        if allow_right and not allow_left:
            angle -= 2
        if allow_up and not allow_down:
            a = math.radians(-angle)
            b = math.radians(-angle)
            x += math.sin(a) * speed
            y -= math.cos(b) * speed
        if allow_down and not allow_up:
            a = math.radians(-angle)
            b = math.radians(-angle)
            x -= math.sin(a) * speed
            y += math.cos(b) * speed
        if sliding and sliding_counter > 0:
            a = math.radians(-angle)
            b = math.radians(-angle)
            if direction == 'up':
                x += math.sin(a) * sliding_counter * 0.05
                y -= math.cos(b) * sliding_counter * 0.05
            elif direction == 'down':
                x -= math.sin(a) * sliding_counter * 0.05
                y += math.cos(b) * sliding_counter * 0.05
            sliding_counter -= 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not allow_right:
                    allow_left = True
                if event.key == pygame.K_RIGHT and not allow_left:
                    allow_right = True
                if event.key == pygame.K_UP and not allow_down:
                    allow_up = True
                if event.key == pygame.K_DOWN and not allow_up:
                    allow_down = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    allow_right = False
                if event.key == pygame.K_LEFT:
                    allow_left = False
                if event.key == pygame.K_UP:
                    direction = 'up'
                    sliding = True
                    allow_up = False
                    sliding_counter = speed * 10
                if event.key == pygame.K_DOWN:
                    direction = 'down'
                    sliding_counter = speed * 10
                    sliding = True
                    allow_down = False
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()


boat_run()