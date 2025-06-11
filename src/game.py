# game.py
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
        spawn_x, spawn_y = self.game_map.spawn_point
        self.player = Hero(spawn_x, spawn_y, self.game_map)

        self.enemy_boss = Boss1(1000, 200, self.player)
        self.enemy_boss.set_room_boundaries(570, 100, 1500, 335) #Large Room 4
        enemy_group.add(self.enemy_boss)
        
        self.enemy_boss_6 = Boss4(1300, 200, self.player)
        self.enemy_boss_6.set_room_boundaries(570, 100, 1500, 335) #Large Room 4
        enemy_group.add(self.enemy_boss_6)
    
        self.enemy_boss_2 = Boss3(300, 1500, self.player)
        self.enemy_boss_2.set_room_boundaries(10, 1370, 425, 1600) #Room 1
        enemy_group.add(self.enemy_boss_2)
    
        self.enemy_boss_3 = Boss2(800, 1100, self.player)
        self.enemy_boss_3.set_room_boundaries(340, 1050, 1450, 1195) #Large Room 2
        enemy_group.add(self.enemy_boss_3)
        
    
        self.enemy_boss_4 = Boss2(1250, 750, self.player)
        self.enemy_boss_4.set_room_boundaries(1000, 750, 1480, 810) #Room 6
        enemy_group.add(self.enemy_boss_4)
    
        self.enemy_boss_5 = Boss5(1400, 1500, self.player)
        self.enemy_boss_5.set_room_boundaries(1210, 1370, 1520, 1520) #Room 3
        enemy_group.add(self.enemy_boss_5)
    
        #self.enemy_boss_6 = Boss1(200, 750, self.player)
        #self.enemy_boss_6.set_room_boundaries(150, 700, 250, 800)
        #enemy_group.add(self.enemy_boss_6)
        
        

        self.camera = Camera(self.WIDTH, self.HEIGHT, self.game_map.map_width, self.game_map.map_height)

    def run_game(self):
        if self.player.is_dead() and not self.game_over:
            self.game_over = True
            self.menu.state = "main"
            bullet_group.empty()
            enemy_group.empty()
            return
            
        if not self.game_over:
            self.player.update(self.game_map)
            self.camera.update(self.player)
            bullet_group.update(self.game_map.collision_objects)
            
            self.game_map.Draw(self.screen, self.camera.camera)
            
            for bullet in bullet_group:
                bullet_pos = (bullet.rect.x - self.camera.camera.x, bullet.rect.y - self.camera.camera.y)
                self.screen.blit(bullet.image, bullet_pos)
            
            self.player.draw(self.screen, self.camera.camera)
            
            enemy_group.update("game")
            
            for enemy in enemy_group:
                self.screen.blit(enemy.image, (enemy.rect.x - self.camera.camera.x, enemy.rect.y - self.camera.camera.y))
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