import pygame


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Hello Pygame")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
