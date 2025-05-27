import pygame
import math

class Gun(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.base_image = pygame.image.load("assets/Weapons/AK.png").convert_alpha()
        self.image = self.base_image
        self.rect = self.image.get_rect()

        # Смещение от центра игрока до точки, где крепится пушка (на теле)
        self.offset = pygame.math.Vector2(30, -10)  # подбери под свою модель

    def update(self):
        # Угол игрока
        angle = self.player.angle

        # Повернули пушку
        self.image = pygame.transform.rotate(self.base_image, -angle)

        # Центр игрока (его спрайта) — реальная точка привязки
        player_center = pygame.math.Vector2(self.player.hitbox_rect.center)

        # Смещаем пушку от центра игрока, с учётом поворота
        rotated_offset = self.offset.rotate(-angle)
        gun_center = player_center + rotated_offset

        # Обновляем rect пушки
        self.rect = self.image.get_rect(center=gun_center)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
