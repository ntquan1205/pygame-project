import pygame

class Hero:

    def __init__(self, health, damage, speed, x, y):
        self.health = health
        self.damage = damage
        self.speed = speed
        self.x = x
        self.y = y
    
    def move(self, speed):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y += speed
        if keys[pygame.K_a]:
            self.x -= speed
        if keys[pygame.K_s]:
            self.y -= speed
        if keys[pygame.K_d]:
           self.x += speed