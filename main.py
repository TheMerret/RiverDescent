from MainMenu.MainMenu import *
from boat import boat_run


def show_loading_screen():
    screen.fill('black')
    background = load_image('123.png', way_to_file='MainMenu/data')
    screen.blit(background, (0, 0))
    text_color = (158, 218, 155)
    pygame.font.init()
    font = pygame.font.SysFont('Comic Sans MS', 100)
    lines = 'Подождите...\nИгра загружается...'.splitlines()
    for ind, text in zip(range(-1, 2, 2), lines):
        text_surface = font.render(text, False, text_color)
        width, height = text_surface.get_size()
        center = WIDTH / 2, HEIGHT * (1 / 3)
        top_left_text_corner = center[0] - width / 2, center[1] + ind * (height / 2)
        screen.blit(text_surface, top_left_text_corner)
    pygame.display.flip()


def load_menu_with_buttons():
    counting = 0
    for i in range(300, 750, 250):
        for j in range(120, 880, 130):
            counting += 1
            button = Button(j, i, 100, 100, screen, 1, counting, imagepath="MainMenu\\data",
                            imagename="иконка228.png", ONtext=f"{counting}",
                            ONtextcolor=(34, 139, 34), UNDERtext=f"level {counting}",
                            UNDERtextcolor=(232, 194, 44), groups=(all_sprites, buttons))

            def slot(scrn=screen, id_=button.signal.id_):
                show_loading_screen()
                res = boat_run(scrn, id_)
                if res == 'retry':
                    slot(scrn, id_)

            button.signal.connect(slot)

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
        image = screen.blit(load_image("123.png", way_to_file="MainMenu/data"),
                            pygame.Rect((0, 0), (WIDTH, HEIGHT)))
        ONtext = "RiverDescent"
        ONfont = pygame.font.Font(None, 120)
        ONrendertext = ONfont.render(ONtext, True, (232, 194, 44))
        ONw = ONrendertext.get_width()
        ONh = ONrendertext.get_height()
        ONx = 500 - ONw // 2
        ONy = 100
        screen.blit(ONrendertext, (ONx, ONy))
        all_sprites.draw(screen)
        try:
            all_sprites.update()
        except pygame.error:
            return
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    button = Button(300, 600, 400, 150, screen, 0, 1, ONtext=f"ИГРАТЬ",
                    imagepath="MainMenu\\data", imagename="иконка228.png",
                    ONtextcolor=(34, 139, 34), groups=(all_sprites, buttons))
    running = True

    def ex():
        nonlocal running
        running = False
        button.kill()

    button.signal.connect(ex)

    flagDown = 0
    flagUp = 0
    while running:
        WIDTH, HEIGHT = pygame.display.get_window_size()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                button.kill()
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
        image = screen.blit(load_image("start_screen.png", way_to_file="assets/start_screen"),
                            pygame.Rect((0, 0), (WIDTH, HEIGHT)))
        all_sprites.draw(screen)
        try:
            all_sprites.update()
        except pygame.error:
            return
        pygame.display.flip()
        clock.tick(FPS)


def main():
    start_screen()
    load_menu_with_buttons()


if __name__ == "__main__":
    main()
