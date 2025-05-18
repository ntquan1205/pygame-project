import pygame

class Hero:

    def __init__(self, health, damage, speed, x, y):
        self.health = health
        self.damage = damage
        self.speed = speed
        self.x = x
        self.y = y
    
    def move(self, x, y, speed):
        x += speed
        y += speed
