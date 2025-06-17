import pygame
import os
import random
import sys  
import time
import math
from menu import *
from characters import *
from settings import *


class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1200, 750
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('game')

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.font = pygame.font.Font('freesansbold.ttf', 18)
        self.big_font = pygame.font.Font('freesansbold.ttf', 30)

        pygame.mixer.music.load('assets/Menu/MenuTrack.ogg')
        pygame.mixer.music.set_volume(0.5)
        
        self.boss_music = pygame.mixer.Sound('assets/Music/08 Red Sun (Maniac Agenda Mix).mp3')  
        self.boss_music.set_volume(0.5)

        pygame.mixer.music.play(-1)

        self.snow = [[random.randrange(0, self.WIDTH), random.randrange(0, self.HEIGHT)] for _ in range(50)]
        self.menu = MenuManager(self)
        
        self.game_map = None
        self.player = None
        self.enemy_boss = None
        self.enemy_minion = None
        self.camera = None

        self.cat = Cat(160, 720, self)

        self.game_over = False
        self.boss_level = False 
        self.boss_level_initialized = False 

        self.enemies_killed = 0
        self.total_enemies = 30

        self.game_start_time = 0
        self.game_end_time = 0
        self.pause_start_time = 0
        self.total_pause_time = 0
        self.current_record = 0
        self.if_current_record_exist = True

        self.load_record()

        self.heart_image = pygame.image.load('assets/Hero/Untitled 06-08-2025 08-30-35.png').convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (32, 32))  

    def load_record(self):
        if os.path.exists("src/record.txt") and os.path.getsize("src/record.txt") > 0:
            with open('src/record.txt', 'r', encoding='utf-8') as file:
                self.current_record = float(file.read().strip())
        else:
            self.current_record = 100000000000000
            self.if_current_record_exist = False
            

    def save_record_if_better(self, new_time):
        if new_time < self.current_record:
            with open('src/record.txt', 'w', encoding='utf-8') as file:
                file.write(f"{new_time:.2f}")
            self.current_record = new_time
            return True
        return False

    def init_boss_level(self):
        self.boss_level = True
        self.boss_level_initialized = True
        bullet_group.empty()
        enemy_group.empty()
        
        pygame.mixer.music.stop()
        self.boss_music.play(-1)  
        self.boss_music.set_volume(self.menu.volume)
        
        self.game_map = Map("assets/Map/dungeon2BOSS.tmx")
        
        spawn_x, spawn_y = self.game_map.spawn_point
        
        self.player.pos = pygame.math.Vector2(spawn_x, spawn_y)
        self.player.rect.center = (spawn_x, spawn_y)
        self.player.hitbox_rect.center = (spawn_x, spawn_y)
        self.eye_boss = EYEBOSS(394, 184, self.player)
        enemy_group.add(self.eye_boss)
        all_sprites_group.add(self.eye_boss)
        
        self.camera = Camera(self.WIDTH, self.HEIGHT, self.game_map.map_width, self.game_map.map_height)

        self.enemies_killed = 0
        self.total_enemies = 30

    def init_game(self):
        bullet_group.empty()
        enemy_group.empty()
        all_sprites_group.empty()

        self.game_over = False
        self.boss_level = False  
        self.boss_level_initialized = False
        self.total_pause_time = 0  
        self.game_end_time = 0  

        self.game_map = Map("assets/Map/dungeon1.tmx")
        spawn_x, spawn_y = self.game_map.spawn_point

        self.player = Hero(spawn_x, spawn_y, self.game_map)
        self.cat = Cat(120, 750, self)

        self.enemy_1 = Skeleton2(400, 1150, self.player)
        self.enemy_1.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_1)

        self.enemy_2 = Skeleton1(600, 1200, self.player)
        self.enemy_2.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_2)

        self.enemy_3 = Skeleton3(800, 1050, self.player)
        self.enemy_3.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_3)

        self.enemy_4 = Skeleton4(1000, 1100, self.player)
        self.enemy_4.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_4)

        self.enemy_boss_5 = Boss(1200, 1150, self.player)
        self.enemy_boss_5.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_boss_5)

        self.enemy_6 = Skeleton1(300, 1500, self.player)
        self.enemy_6.set_room_boundaries(20, 1350, 440, 1560) #Room 1
        enemy_group.add(self.enemy_6)

        self.enemy_7 = Skeleton2(100, 1500, self.player)
        self.enemy_7.set_room_boundaries(20, 1350, 440, 1560) #Room 1
        enemy_group.add(self.enemy_7)

        self.enemy_8 = Skeleton3(1200, 1450, self.player)
        self.enemy_8.set_room_boundaries(1160, 1350, 1600, 1560) #Room 3
        enemy_group.add(self.enemy_8)

        self.enemy_9 = Skeleton4(1300, 1500, self.player)
        self.enemy_9.set_room_boundaries(1160, 1350, 1600, 1560) #Room 3
        enemy_group.add(self.enemy_9)

        self.enemy_10 = Skeleton1(1400, 1400, self.player)
        self.enemy_10.set_room_boundaries(1160, 1350, 1600, 1560) #Room 3
        enemy_group.add(self.enemy_10)
        
        self.enemy_11 = Skeleton2(1300, 1400, self.player)
        self.enemy_11.set_room_boundaries(1160, 1350, 1600, 1560) #Room 3
        enemy_group.add(self.enemy_11)

        self.enemy_12 = Skeleton2(1000, 200, self.player)
        self.enemy_12.set_room_boundaries(530, 90, 1540, 380) #Large Room 4
        enemy_group.add(self.enemy_12)
        
        self.enemy_13 = Skeleton3(1300, 200, self.player)
        self.enemy_13.set_room_boundaries(530, 90, 1540, 380) #Large Room 4
        enemy_group.add(self.enemy_13)

        self.enemy_14 = Skeleton4(1000, 200, self.player)
        self.enemy_14.set_room_boundaries(530, 90, 1540, 380) #Large Room 4
        enemy_group.add(self.enemy_14)

        self.enemy_15 = Skeleton2(1470, 1120, self.player)
        self.enemy_15.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_15)

        self.enemy_16 = Skeleton1(700, 1130, self.player)
        self.enemy_16.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_16)

        self.enemy_17 = Skeleton3(900, 1150, self.player)
        self.enemy_17.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_17)

        self.enemy_18 = Skeleton4(1500, 1100, self.player)
        self.enemy_18.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_18)

        self.enemy_19 = Skeleton3(400, 1430, self.player)
        self.enemy_19.set_room_boundaries(20, 1350, 440, 1560) #Room 1
        enemy_group.add(self.enemy_19)

        self.enemy_20 = Skeleton4(60, 1380, self.player)
        self.enemy_20.set_room_boundaries(20, 1350, 440, 1560) #Room 1
        enemy_group.add(self.enemy_20)


        self.enemy_boss_21 = Skeleton1(1000, 750, self.player)
        self.enemy_boss_21.set_room_boundaries(900, 700, 1600, 900) #Room 6
        enemy_group.add(self.enemy_boss_21)

        self.enemy_boss_22 = Skeleton2(1000, 800, self.player)
        self.enemy_boss_22.set_room_boundaries(900, 700, 1600, 900) #Room 6
        enemy_group.add(self.enemy_boss_22)

        self.enemy_boss_23 = Skeleton3(1300, 820, self.player)
        self.enemy_boss_23.set_room_boundaries(900, 700, 1600, 900) #Room 6
        enemy_group.add(self.enemy_boss_23)

        self.enemy_boss_24 = Skeleton4(1200, 750, self.player)
        self.enemy_boss_24.set_room_boundaries(900, 700, 1600, 900) #Room 6
        enemy_group.add(self.enemy_boss_24)

        self.enemy_25 = Skeleton2(600, 140, self.player)
        self.enemy_25.set_room_boundaries(530, 90, 1540, 380) #Large Room 4
        enemy_group.add(self.enemy_25)
        
        self.enemy_26 = Witch(750, 200, self.player)
        self.enemy_26.set_room_boundaries(530, 90, 1540, 380) #Large Room 4
        enemy_group.add(self.enemy_26)

        self.enemy_27 = Boss(890, 320, self.player)
        self.enemy_27.set_room_boundaries(530, 90, 1540, 380) #Large Room 4
        enemy_group.add(self.enemy_27)

        self.enemy_28 = Skeleton1(680, 120, self.player)
        self.enemy_28.set_room_boundaries(530, 90, 1540, 380) #Large Room 4
        enemy_group.add(self.enemy_28)
        
        self.enemy_29 = Skeleton3(1080, 270, self.player)
        self.enemy_29.set_room_boundaries(530, 90, 1540, 380) #Large Room 4
        enemy_group.add(self.enemy_29)

        self.enemy_30 = Boss(1420, 220, self.player)
        self.enemy_30.set_room_boundaries(530, 90, 1540, 380) #Large Room 4
        enemy_group.add(self.enemy_30)
    
    
        
        self.camera = Camera(self.WIDTH, self.HEIGHT, self.game_map.map_width, self.game_map.map_height)

        self.game_start_time = time.time()

    def run_game(self):
        if self.player.is_dead() and not self.game_over:
            self.game_over = True
            bullet_group.empty()
            enemy_group.empty()
            all_sprites_group.empty()
            
            if self.boss_level:
                self.boss_music.stop()
                self.boss_level = False
                self.boss_level_initialized = False
            pygame.mixer.music.play(-1)

            self.menu.state = "game_over"  
            return
            
        if not self.game_over:
            self.player.update(self.game_map)
            self.camera.update(self.player)
            bullet_group.update(self.game_map.collision_objects)

            for enemy in enemy_group:
                for bullet in bullet_group:
                    if bullet.rect.colliderect(enemy.rect):
                        if enemy.take_damage(bullet.damage):  
                            self.enemies_killed += 1
                        bullet.kill()
                        break 
            for enemy in enemy_group:
                if isinstance(enemy, EYEBOSS):
                    for shot in enemy.shots:
                        if shot.rect.colliderect(self.player.hitbox_rect):
                            self.player.take_damage(shot.damage)
                            shot.kill()
            
            for enemy in enemy_group:
                if isinstance(enemy, EYEBOSS) and enemy.laser:
                    laser_rect = pygame.Rect(
                        enemy.laser.rect.x - self.camera.camera.x,
                        enemy.laser.rect.y - self.camera.camera.y,
                        enemy.laser.rect.width,
                        enemy.laser.rect.height
                    )
                    
                    if laser_rect.colliderect(self.player.hitbox_rect):
                        current_time = pygame.time.get_ticks()
                        if current_time - enemy.laser.last_damage_time > 1000:  
                            self.player.take_damage(enemy.laser.damage)
                            enemy.laser.last_damage_time = current_time
            
            self.game_map.Draw(self.screen, self.camera.camera)
            
            for bullet in bullet_group:
                bullet_pos = (bullet.rect.x - self.camera.camera.x, bullet.rect.y - self.camera.camera.y)
                self.screen.blit(bullet.image, bullet_pos)
            
            self.player.draw(self.screen, self.camera.camera)
            
            enemy_group.update("game")
            
            for enemy in enemy_group:
                self.screen.blit(enemy.image, (enemy.rect.x - self.camera.camera.x, enemy.rect.y - self.camera.camera.y))
                
                if isinstance(enemy, EYEBOSS):
                    for shot in enemy.shots:
                        shot_pos = (shot.rect.x - self.camera.camera.x, shot.rect.y - self.camera.camera.y)
                        self.screen.blit(shot.image, shot_pos)
                    
                    if enemy.laser:
                        laser_pos = (enemy.laser.rect.x - self.camera.camera.x, enemy.laser.rect.y - self.camera.camera.y)
                        self.screen.blit(enemy.laser.image, laser_pos)
            
            self.draw_hearts()
            self.draw_game_time()

            if not self.boss_level:
                self.cat.update(self.camera.camera)  
                self.cat.draw(self.screen)
            
            if self.boss_level and hasattr(self, 'eye_boss') and self.eye_boss.health <= 0 and self.game_end_time == 0:
                self.game_end_time = time.time()
                total_time = self.game_end_time - self.game_start_time - self.total_pause_time
                
                if total_time < self.current_record:
                    self.save_record_if_better(total_time)
            
            if len(enemy_group) == 0 and self.menu.state == "game" and not self.boss_level_initialized:
                self.menu.state = "waiting_for_boss"
                self.enemies_killed = 0
                if self.boss_level:
                    self.boss_music.stop()
                    pygame.mixer.music.play(-1)

    def draw_hearts(self):
        for i in range(self.player.max_health):
            x = 10 + i * 40  
            y = 700
            if i < self.player.health:
                self.screen.blit(self.heart_image, (x, y))
            else:
                dark_heart = self.heart_image.copy()
                dark_heart.fill((100, 100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
                self.screen.blit(dark_heart, (x, y))

    def draw_game_time(self):
        if self.game_start_time == 0:
            return
            
        current_time = time.time()
        
        if self.game_end_time > 0:
            game_time = self.game_end_time - self.game_start_time - self.total_pause_time
            time_text = f"Time: {game_time:.1f}s (Final)"
        else: 
            game_time = current_time - self.game_start_time - self.total_pause_time
            time_text = f"Time: {game_time:.1f}s"
            

            if self.current_record > 0 and self.if_current_record_exist == True:
                time_text += f" | Record: {self.current_record:.1f}s"
        
        time_surface = self.font.render(time_text, True, (255, 255, 255))
        self.screen.blit(time_surface, (10, 10))

    def draw_boss_hp(self):
        if not self.boss_level or not hasattr(self, 'eye_boss') or self.eye_boss.is_dead:
            return

        bar_width = 600
        bar_height = 30
        x = (self.WIDTH - bar_width) // 2
        y = 20
        
        hp_percent = self.eye_boss.health / EYE_BOSS_HP

        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, bar_width, bar_height))
        
        if hp_percent < 0.3:
            pulse = (math.sin(pygame.time.get_ticks() * 0.005) * 55 + 200)
            health_color = (255, pulse, pulse)
        else:
            health_color = (255, 0, 0)
        
        pygame.draw.rect(self.screen, health_color, (x, y, bar_width * hp_percent, bar_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and (self.menu.state == "game" or self.boss_level):
                        self.pause_start_time = time.time()  
                        self.menu.state = "pause"

                    elif event.key == pygame.K_ESCAPE and self.menu.state == "pause":
                        self.total_pause_time += time.time() - self.pause_start_time
                        self.menu.state = "game"
                            
            self.clock.tick(self.fps)
            self.screen.fill((0, 0, 0)) 

            if self.menu.state == "game":
                self.run_game()
            
            if self.menu.state != "game":
                self.menu.update()

            self.draw_boss_hp()
            pygame.display.flip()