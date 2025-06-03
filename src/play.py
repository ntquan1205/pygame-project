import pygame
import sys
from pytmx.util_pygame import load_pygame

class Player:
    def __init__(self, x, y, size, speed):
        self.position = pygame.Vector2(x, y)
        self.size = size
        self.image = pygame.image.load(r"D:\sprites\sprite MH 1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size * 4, self.size * 4))
        self.speed = speed
        

    def Controls(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.position.y -= self.speed
        if keys[pygame.K_s]:
            self.position.y += self.speed
        if keys[pygame.K_a]:
            self.position.x -= self.speed
        if keys[pygame.K_d]:
            self.position.x += self.speed

        self.position.x = max(0, min(self.position.x, 1280 - self.size))
        self.position.y = max(0, min(self.position.y, 720 - self.size))

    def Draw(self, screen):
        screen.blit(self.image, (self.position.x, self.position.y))

class Map:

    def __init__(self, filename):
        self.tmx_data = load_pygame(r'D:\ucheba\From the Woods\map\dungeon1')
        
class Game:
    def __init__(self):
        pygame.init()
        screen_width = 1280
        screen_height = 720
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Dungeon Master")
        self.clock = pygame.time.Clock()

        self.player = Player(600, 400, 50, 5)

    def Run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.player.Controls()

            self.screen.fill('black')
            self.player.Draw(self.screen)
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.Run()