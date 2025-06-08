import pygame
import random
import sys  
from menu import *
from hero import *
from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1200, 750
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Buttons!')

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.font = pygame.font.Font('freesansbold.ttf', 18)
        self.big_font = pygame.font.Font('freesansbold.ttf', 30)

        pygame.mixer.music.load('assets/Menu/MenuTrack.ogg')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.snow = [[random.randrange(0, self.WIDTH), random.randrange(0, self.HEIGHT)] for _ in range(50)]
        self.menu = MenuManager(self)
        
        self.game_map = None
        self.player = None
        self.enemy_boss = None
        self.enemy_minion = None
        self.camera = None

        self.game_over = False

    def init_game(self):
        self.game_over = False
        self.game_map = Map()
        self.player = Hero(600, 400)
        self.enemy_boss = Boss1(200, 200, self.player)  
        enemy_group.add(self.enemy_boss)
        self.enemy_minion = Boss2(800, 800, self.player)  
        enemy_group.add(self.enemy_minion)
        self.enemy_boss_3 = Boss3(800, 800, self.player)
        enemy_group.add(self.enemy_boss_3)
        self.camera = Camera(self.WIDTH, self.HEIGHT, self.game_map.map_width, self.game_map.map_height)

    def run_game(self):
        if self.player.is_dead() and not self.game_over:
            self.game_over = True
            self.menu.state = "main"
            bullet_group.empty()
            enemy_group.empty()
            
            return
            
        if not self.game_over:
            self.player.update(self.game_map.map_width, self.game_map.map_height)
            self.camera.update(self.player)
            bullet_group.update()
            
            self.game_map.Draw(self.screen, self.camera.camera)
            
            for bullet in bullet_group:
                bullet_pos = (bullet.rect.x - self.camera.camera.x, bullet.rect.y - self.camera.camera.y)
                self.screen.blit(bullet.image, bullet_pos)
            
            self.player.draw(self.screen, self.camera.camera)
            
            enemy_group.update("game")
            
            for enemy in enemy_group:
                self.screen.blit(enemy.image, (enemy.rect.x - self.camera.camera.x, enemy.rect.y - self.camera.camera.y))
                
            # Draw health bar
            self.draw_health_bar()
            
    def draw_health_bar(self):
        health_bar_width = 200
        health_bar_height = 20
        health_ratio = self.player.health / self.player.max_health
        current_health_width = health_bar_width * health_ratio
        
        outline_rect = pygame.Rect(10, 10, health_bar_width, health_bar_height)
        fill_rect = pygame.Rect(10, 10, current_health_width, health_bar_height)
        
        pygame.draw.rect(self.screen, (255, 0, 0), fill_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), outline_rect, 2)
        
        health_text = self.font.render(f"Health: {self.player.health}/{self.player.max_health}", True, (255, 255, 255))
        self.screen.blit(health_text, (10, 35))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.clock.tick(self.fps)
            self.screen.fill((0, 0, 0))

            if self.menu.state == "game":
                self.run_game()
            else:
                self.menu.update()

            pygame.display.flip()