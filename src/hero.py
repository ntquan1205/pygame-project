import pygame
from settings import PLAYER_START_X, PLAYER_START_Y, PLAYER_SPEED

class Hero:

    def __init__(self, screen, x = PLAYER_START_X, y = PLAYER_START_Y, health = 100, damage = 10, speed = PLAYER_SPEED):
        self.health = health
        self.damage = damage
        self.speed = speed
        self.screen = screen
        self.image = pygame.image.load("assets/Hero/Hero.png")
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()
        self.rect.x = x
        self.rect.y = y

    
    def output(self):

        self.screen.blit(self.image, self.rect)
        
    def move(self, speed = PLAYER_SPEED):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y += speed
        if keys[pygame.K_a]:
            self.rect.x -= speed
        if keys[pygame.K_s]:
            self.rect.y -= speed
        if keys[pygame.K_d]:
           self.rect.x += speed