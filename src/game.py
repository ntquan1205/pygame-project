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

        # Музыка меню
        pygame.mixer.music.load('assets/Menu/MenuTrack.ogg')
        pygame.mixer.music.set_volume(0.5)
        
        # Музыка босса
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

        self.game_over = False
        self.boss_level = False 
        self.boss_level_initialized = False 

        self.enemies_killed = 0
        self.total_enemies = 1

    def init_boss_level(self):
        self.boss_level = True
        self.boss_level_initialized = True
        bullet_group.empty()
        enemy_group.empty()
        
        pygame.mixer.music.stop()
        self.boss_music.play(-1)  
        
        self.game_map = Map("assets/Map/dungeon2BOSS.tmx")
        
        spawn_x, spawn_y = self.game_map.spawn_point
        
        self.player.pos = pygame.math.Vector2(spawn_x, spawn_y)
        self.player.rect.center = (spawn_x, spawn_y)
        self.player.hitbox_rect.center = (spawn_x, spawn_y)
        self.eye_boss = EYEBOSS(394, 184, self.player)
        enemy_group.add(self.eye_boss)
        all_sprites_group.add(self.eye_boss)
        
        self.camera = Camera(self.WIDTH, self.HEIGHT, self.game_map.map_width, self.game_map.map_height)

    def init_game(self):
        self.game_over = False
        self.boss_level = False  
        self.game_map = Map("assets/Map/dungeon1.tmx")
        spawn_x, spawn_y = self.game_map.spawn_point
        self.player = Hero(spawn_x, spawn_y, self.game_map)

        
        #self.enemy_boss = Witch(1000, 200, self.player)
        #self.enemy_boss.set_room_boundaries(530, 90, 1540, 380) #Large Room 4
        #enemy_group.add(self.enemy_boss)
        
        #self.enemy_boss_6 = Boss4(1300, 200, self.player)
        #self.enemy_boss_6.set_room_boundaries(530, 90, 1540, 380) #Large Room 4
        #enemy_group.add(self.enemy_boss_6)
    
        #self.enemy_boss_2 = Boss3(300, 1500, self.player)
        #self.enemy_boss_2.set_room_boundaries(20, 1350, 440, 1560) #Room 1
        #enemy_group.add(self.enemy_boss_2)
    
        self.enemy_boss_3 = Boss2(800, 1100, self.player)
        self.enemy_boss_3.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_boss_3)

        self.enemy_boss_7 = Skeleton1(1000, 1100, self.player)
        self.enemy_boss_7.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_boss_7)

        self.enemy_boss_8 = Skeleton2(1000, 1100, self.player)
        self.enemy_boss_8.set_room_boundaries(200, 1000, 1600, 1300) #Large Room 2
        enemy_group.add(self.enemy_boss_8)
        
    
        #self.enemy_boss_4 = Boss2(1250, 750, self.player)
        #self.enemy_boss_4.set_room_boundaries(900, 700, 1600, 900) #Room 6
        #enemy_group.add(self.enemy_boss_4)
    
        #self.enemy_boss_5 = Boss5(1400, 1500, self.player)
        #self.enemy_boss_5.set_room_boundaries(1160, 1350, 1600, 1560) #Room 3
        #enemy_group.add(self.enemy_boss_5)
    
        #self.enemy_boss_6 = Boss1(200, 750, self.player)
        #self.enemy_boss_6.set_room_boundaries(150, 700, 250, 800)
        #enemy_group.add(self.enemy_boss_6)

        self.camera = Camera(self.WIDTH, self.HEIGHT, self.game_map.map_width, self.game_map.map_height)

        self.enemies_killed = 0
        self.total_enemies = 6

    def run_game(self):
        if self.player.is_dead() and not self.game_over:
            self.game_over = True
            self.menu.state = "main"
            bullet_group.empty()
            enemy_group.empty()
            # При возврате в меню остановить музыку босса и включить музыку меню
            if self.boss_level:
                self.boss_music.stop()
                pygame.mixer.music.play(-1)
            return
            
        if not self.game_over:
            self.player.update(self.game_map)
            self.camera.update(self.player)
            bullet_group.update(self.game_map.collision_objects)
            
            # Проверка столкновений снарядов круговой атаки с игроком
            for enemy in enemy_group:
                if isinstance(enemy, EYEBOSS):
                    for shot in enemy.shots:
                        if shot.rect.colliderect(self.player.hitbox_rect):
                            self.player.take_damage(shot.damage)
                            shot.kill()
            
            # Проверка столкновений с лазером
            for enemy in enemy_group:
                if isinstance(enemy, EYEBOSS) and enemy.laser:
                    # Получаем глобальные координаты лазера с учетом камеры
                    laser_rect = pygame.Rect(
                        enemy.laser.rect.x - self.camera.camera.x,
                        enemy.laser.rect.y - self.camera.camera.y,
                        enemy.laser.rect.width,
                        enemy.laser.rect.height
                    )
                    
                    # Проверяем столкновение с игроком
                    if laser_rect.colliderect(self.player.hitbox_rect):
                        current_time = pygame.time.get_ticks()
                        if current_time - enemy.laser.last_damage_time > 1000:  # Урон раз в секунду
                            self.player.take_damage(enemy.laser.damage)
                            enemy.laser.last_damage_time = current_time
            
            # Отрисовка
            self.game_map.Draw(self.screen, self.camera.camera)
            
            # Отрисовка пуль игрока
            for bullet in bullet_group:
                bullet_pos = (bullet.rect.x - self.camera.camera.x, bullet.rect.y - self.camera.camera.y)
                self.screen.blit(bullet.image, bullet_pos)
            
            # Отрисовка игрока
            self.player.draw(self.screen, self.camera.camera)
            
            # Обновление и отрисовка врагов
            enemy_group.update("game")
            
            for enemy in enemy_group:
                # Отрисовка врага
                self.screen.blit(enemy.image, (enemy.rect.x - self.camera.camera.x, enemy.rect.y - self.camera.camera.y))
                
                # Отрисовка снарядов врага и лазера
                if isinstance(enemy, EYEBOSS):
                    # Круговые снаряды
                    for shot in enemy.shots:
                        shot_pos = (shot.rect.x - self.camera.camera.x, shot.rect.y - self.camera.camera.y)
                        self.screen.blit(shot.image, shot_pos)
                    
                    # Лазер
                    if enemy.laser:
                        laser_pos = (enemy.laser.rect.x - self.camera.camera.x, enemy.laser.rect.y - self.camera.camera.y)
                        self.screen.blit(enemy.laser.image, laser_pos)
            
            # Отрисовка HUD
            self.draw_health_bar()
            
            # Проверка завершения уровня
            if len(enemy_group) == 0 and self.menu.state == "game" and not self.boss_level_initialized:
                self.menu.state = "waiting_for_boss"
                self.enemies_killed = 0
                # При завершении уровня босса вернуть музыку меню
                if self.boss_level:
                    self.boss_music.stop()
                    pygame.mixer.music.play(-1)

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