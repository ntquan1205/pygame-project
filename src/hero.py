import pygame
from settings import *

class Hero:

    def __init__(self, screen, x = PLAYER_START_X, y = PLAYER_START_Y, health = 100, damage = 10, speed = PLAYER_SPEED):
        self.health = health
        self.damage = damage
        self.speed = speed
        self.screen = screen
        self.base_player_image = pygame.transform.rotozoom(pygame.image.load("assets/Hero/Hero.png").convert_alpha(), 0, PLAYER_SIZE)
        self.image = pygame.transform.rotozoom(self.base_player_image, 0, PLAYER_SIZE)
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()
        self.rect.x = x
        self.rect.y = y

    
    def output(self):

        self.screen.blit(self.image, self.rect)
        
    def move(self, speed = PLAYER_SPEED):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= speed
        if keys[pygame.K_a]:
            self.rect.x -= speed
        if keys[pygame.K_s]:
            self.rect.y += speed
        if keys[pygame.K_d]:
           self.rect.x += speed