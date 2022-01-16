from boat import boat_run
from MainMenu.MainMenu import *


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
        all_sprites.draw(screen)
        try:
            all_sprites.update()
        except pygame.error:
            return
        pygame.display.flip()
        clock.tick(FPS)


def main():
    load_menu_with_buttons()


if __name__ == "__main__":
    main()
