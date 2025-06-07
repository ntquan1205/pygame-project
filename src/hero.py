import pygame
from settings import *
from game import *
import math
from pytmx.util_pygame import load_pygame

screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()     
all_sprites_group = pygame.sprite.Group()     

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, lifetime, scale, bullet_image):
        super().__init__()
        self.image = pygame.image.load(bullet_image).convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, scale)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.x_vel = math.cos(math.radians(self.angle)) * self.speed
        self.y_vel = math.sin(math.radians(self.angle)) * self.speed
        self.bullet_lifetime = lifetime
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.x += self.x_vel
        self.y += self.y_vel
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()

class PistolBullet(Bullet):
    COOLDOWN = 15
    def __init__(self, x, y, angle):
        super().__init__(x, y, angle, speed=10, lifetime=1500, scale=1, bullet_image="assets/Weapons/bullet.png")

class ShotgunBullet(Bullet):
    COOLDOWN = 30
    def __init__(self, x, y, angle):
        super().__init__(x, y, angle, speed=8, lifetime=500, scale=1.5, bullet_image="assets/Weapons/bullet.png")

class AK47Bullet(Bullet):
    COOLDOWN = 10
    def __init__(self, x, y, angle):
        super().__init__(x, y, angle, speed=12, lifetime=1500, scale=1, bullet_image="assets/Weapons/bullet.png")

class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.max_health = HEALTH
        self.health = HEALTH
        self.damage = DAMAGE
        self.speed = PLAYER_SPEED
        self.base_player_image = pygame.transform.rotozoom(pygame.image.load("assets/Hero/Hero.png").convert_alpha(), 0, PLAYER_SIZE)
        self.image = pygame.transform.rotozoom(self.base_player_image, 0, PLAYER_SIZE)
        self.pos = pygame.math.Vector2(x, y)
        self.rect = self.image.get_rect()
        self.hitbox_rect = self.image.get_rect(center=self.pos)
        self.rect = self.hitbox_rect.copy()
        self.shoot = False
        self.shoot_cooldown = 0
        self.gun_offset_x = 30 
        self.gun_offset_y = 30  
        self.gun_barrel_offset = pygame.math.Vector2(self.gun_offset_x, self.gun_offset_y)
        self.screen = screen
        self.gun_images = {
            1: pygame.image.load("assets/Weapons/Pistol1.png").convert_alpha(),
            2: pygame.image.load("assets/Weapons/AK.png").convert_alpha(),
            3: pygame.image.load("assets/Weapons/Shotgun1.png").convert_alpha(),
        }
        self.current_gun = 1
        self.update_gun_image()
        self.angle = 0
        self.load_sounds()
        self.last_damage_time = 0
        self.damage_cooldown = 1000

    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time > self.damage_cooldown:
            self.health -= amount
            self.last_damage_time = current_time

            self.damage_sound.play()
            
            if self.health <= 0:
                self.health = 0
            
    def is_dead(self):
        return self.health <= 0

    def load_sounds(self):
        self.pistol_sound = pygame.mixer.Sound("assets/Weapons/Pistolbullet.mp3")
        self.shotgun_sound = pygame.mixer.Sound("assets/Weapons/Shotgunbullet.wav")
        self.ak47_sound = pygame.mixer.Sound("assets/Weapons/AKbullet.wav")

        self.damage_sound = pygame.mixer.Sound("assets/Hero/Dead.mp3")  #
        self.damage_sound.set_volume(0.7) 

    def update_gun_image(self):
        base_img = self.gun_images[self.current_gun]
        self.base_gun_image = pygame.transform.rotozoom(base_img, 0, PLAYER_SIZE)
        self.gun_image = self.base_gun_image
        self.gun_rect = self.gun_image.get_rect(center=self.rect.center)

    def change_player(self, weapon_index):
        self.current_gun = weapon_index
        self.update_gun_image()

    def player_rotation(self):
        mouse_coords = pygame.mouse.get_pos()
        screen_center_x = self.screen.get_width() // 2
        screen_center_y = self.screen.get_height() // 2
        x_change_mouse_player = (mouse_coords[0] - screen_center_x)
        y_change_mouse_player = (mouse_coords[1] - screen_center_y)
        self.angle = math.degrees(math.atan2(y_change_mouse_player, x_change_mouse_player))
        self.gun_image = pygame.transform.rotate(self.base_gun_image, -self.angle)
        self.gun_rect = self.gun_image.get_rect(center=self.rect.center)

    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if self.velocity_x != 0 and self.velocity_y != 0: 
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)

        if pygame.mouse.get_pressed()[0]:
            self.shoot = True
            self.is_shooting()
        else:
            self.shoot = False

        if keys[pygame.K_1]: self.change_player(1)
        if keys[pygame.K_2]: self.change_player(2)
        if keys[pygame.K_3]: self.change_player(3)

    def is_shooting(self):
        if self.shoot_cooldown == 0:
            barrel_offset = self.gun_barrel_offset.rotate(-self.angle)
            barrel_pos = self.pos + barrel_offset
            
            if self.current_gun == 1:
                bullet = PistolBullet(barrel_pos.x, barrel_pos.y, self.angle)
                self.pistol_sound.play()
                self.shoot_cooldown = PistolBullet.COOLDOWN
            elif self.current_gun == 2:
                bullet = AK47Bullet(barrel_pos.x, barrel_pos.y, self.angle)
                self.ak47_sound.play()
                self.shoot_cooldown = AK47Bullet.COOLDOWN
            elif self.current_gun == 3:
                bullet = ShotgunBullet(barrel_pos.x, barrel_pos.y, self.angle)
                self.shotgun_sound.play()
                self.shoot_cooldown = ShotgunBullet.COOLDOWN

            bullet_group.add(bullet)

    def move(self, map_width, map_height):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.rect.center = self.pos
        self.pos.x = max(0, min(self.pos.x, map_width - self.rect.width))
        self.pos.y = max(0, min(self.pos.y, map_height - self.rect.height))

    def update(self, map_width, map_height):
        self.user_input()
        self.move(map_width, map_height)
        self.player_rotation()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        bullet_group.update()

    def draw(self, screen, camera):
        char_pos = self.rect.topleft - pygame.Vector2(camera.x, camera.y)
        screen.blit(self.base_player_image, char_pos)
        
        gun_pos = (self.rect.centerx + self.gun_offset_x - camera.x, self.rect.centery + self.gun_offset_y - camera.y)
        gun_rect = self.gun_image.get_rect(center=gun_pos)
        screen.blit(self.gun_image, gun_rect)


class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height
        self.camera = pygame.Rect(0, 0, width, height)
        
    def apply(self, entity):
        return entity.rect.move(-self.camera.x, -self.camera.y)

    def update(self, target):
        x = target.rect.centerx - self.width // 2
        y = target.rect.centery - self.height // 2
        
        x = max(0, min(x, self.map_width - self.width))
        y = max(0, min(y, self.map_height - self.height))
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Map:
    def __init__(self):
        self.tmx_data = load_pygame("assets/Map/dungeon1.tmx")
        self.tile_size = self.tmx_data.tilewidth
        self.map_width = self.tmx_data.width * self.tile_size
        self.map_height = self.tmx_data.height * self.tile_size
        
    def Draw(self, screen, camera):
        start_x = max(0, int(camera.x // self.tile_size) - 1)
        start_y = max(0, int(camera.y // self.tile_size) - 1)
        end_x = min(self.tmx_data.width, int((camera.x + camera.width) // self.tile_size) + 2)
        end_y = min(self.tmx_data.height, int((camera.y + camera.height) // self.tile_size) + 2)
        
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'): 
                for y in range(start_y, end_y):
                    for x in range(start_x, end_x):
                        gid = layer.data[y][x]
                        tile = self.tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            screen.blit(tile, 
                                       (x * self.tile_size - camera.x, 
                                        y * self.tile_size - camera.y))
            else: 
                for x, y, gid in layer:
                    if start_x <= x < end_x and start_y <= y < end_y:
                        tile = self.tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            screen.blit(tile, 
                                      (x * self.tile_size - camera.x, 
                                       y * self.tile_size - camera.y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, target, speed=ENEMY_SPEED, animation_speed=0.035):
        super().__init__()
        self.target = target
        self.pos = pygame.math.Vector2(x, y)
        self.speed = speed
        self.animation_speed = animation_speed
        self.animation_counter = 0
        self.facing_right = True
        self.current_frame = 0
        self.setup_frames()
        self.image = self.right_frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.collision_radius = 50  
        self.is_colliding = False
        self.last_facing = True  
        self.damage = ENEMY_DAMAGE 

    def update(self, game_state):
        if game_state == "game":
            self.check_collision()
            
            if not self.is_colliding:
                self.animate()
                self.move_towards_target()
            else:
                self.image = self.right_frames[self.current_frame] if self.last_facing else self.left_frames[self.current_frame]

    def check_collision(self):
        distance = self.pos.distance_to(self.target.pos)
        self.is_colliding = distance < self.collision_radius
        if self.is_colliding:
            self.target.take_damage(self.damage)
        if not self.is_colliding:
            direction = self.target.pos - self.pos
            if direction.x != 0:  
                self.last_facing = direction.x > 0

    def setup_frames(self):
        pass

    def animate(self):
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.right_frames)
            self.image = self.right_frames[self.current_frame] if self.facing_right else self.left_frames[self.current_frame]

    def move_towards_target(self):
        if not self.is_colliding:  
            direction = self.target.pos - self.pos
            distance = direction.length()
            if distance != 0:
                direction.normalize_ip()
                
                if direction.x > 0 and not self.facing_right:
                    self.facing_right = True
                    self.image = self.right_frames[self.current_frame]
                elif direction.x < 0 and self.facing_right:
                    self.facing_right = False
                    self.image = self.left_frames[self.current_frame]
                
                self.pos += direction * self.speed
                self.rect.center = self.pos

class Boss1(Enemy):
    def __init__(self, x, y, target):
        super().__init__(x, y, target, speed=1.5, animation_speed=0.02)
        
    def setup_frames(self):
        original_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Enemy2.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Enemy3.png").convert_alpha(), 0, ENEMY_SIZE)
        ]
        self.right_frames = [pygame.transform.rotozoom(frame, 0, ENEMY_SIZE) for frame in original_frames]
        self.left_frames = [pygame.transform.flip(frame, True, False) for frame in self.right_frames]

class Boss2(Enemy):
    def __init__(self, x, y, target):
        super().__init__(x, y, target, speed=2.5, animation_speed=0.035)
        
    def setup_frames(self):
        original_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/1.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/2.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/3.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/4.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/5.png").convert_alpha(), 0, ENEMY_SIZE)
        ]
        self.right_frames = [pygame.transform.rotozoom(frame, 0, ENEMY_SIZE) for frame in original_frames]
        self.left_frames = [pygame.transform.flip(frame, True, False) for frame in self.right_frames]

class Boss3(Enemy):
    def __init__(self, x, y, target):
        super().__init__(x, y, target, speed=2.0, animation_speed=0.035)
        
    def setup_frames(self):
        original_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Walk_1.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Walk_2.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Walk_3.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Walk_4.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Walk_5.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Walk_6.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Walk_7.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Walk_8.png").convert_alpha(), 0, ENEMY_SIZE),
        ]
        self.left_frames = [pygame.transform.rotozoom(frame, 0, ENEMY_SIZE) for frame in original_frames]
        self.right_frames = [pygame.transform.flip(frame, True, False) for frame in self.left_frames]