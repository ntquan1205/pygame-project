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
    def __init__(self, x, y, angle, speed, lifetime, scale, bullet_image, damage):
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
        self.damage = damage 

    def update(self, collision_objects=None):
        self.x += self.x_vel
        self.y += self.y_vel
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if collision_objects:
            bullet_rect = pygame.Rect(self.x - self.rect.width/2, 
                                    self.y - self.rect.height/2, 
                                    self.rect.width, self.rect.height)
            for obj in collision_objects:
                if bullet_rect.colliderect(obj):
                    self.kill()
                    break

        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()

class PistolBullet(Bullet):
    COOLDOWN = 15
    def __init__(self, x, y, angle):
        super().__init__(x, y, angle, speed=10, lifetime=1500, scale=1, bullet_image="assets/Weapons/bullet.png", damage= PISTOL_DAMAGE)

class ShotgunBullet(Bullet):
    COOLDOWN = 30
    def __init__(self, x, y, angle):
        super().__init__(x, y, angle, speed=8, lifetime=500, scale=1.5, bullet_image="assets/Weapons/bullet.png", damage= SHOTGUN_DAMAGE)

class AK47Bullet(Bullet):
    COOLDOWN = 10
    def __init__(self, x, y, angle):
        super().__init__(x, y, angle, speed=12, lifetime=1500, scale=1, bullet_image="assets/Weapons/bullet.png", damage= AK47_DAMAGE)

class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y, game_map):
        super().__init__()
        self.max_health = HEALTH
        self.health = HEALTH
        self.damage = DAMAGE
        self.speed = PLAYER_SPEED
        self.base_player_image = pygame.transform.rotozoom(pygame.image.load("assets/Hero/Hero.png").convert_alpha(), 0, PLAYER_SIZE)
        self.image = self.base_player_image
        self.pos = pygame.math.Vector2(x, y)
        self.rect = self.image.get_rect(center=self.pos)
        self.hitbox_rect = self.rect.copy()
        self.shoot = False
        self.shoot_cooldown = 0
        self.gun_barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, 0)
        self.game_map = game_map
        
        self.gun_images = {
            1: pygame.image.load("assets/Weapons/Pistol1.png").convert_alpha(),
            2: pygame.image.load("assets/Weapons/AK.png").convert_alpha(),
            3: pygame.image.load("assets/Weapons/Shotgun1.png").convert_alpha(),
        }
        self.current_gun = 1
        self.angle = 0
        self.update_gun_image()
        self.load_sounds()
        self.last_damage_time = 0
        self.damage_cooldown = 1000

    def load_sounds(self):
        self.pistol_sound = pygame.mixer.Sound("assets/Weapons/Pistolbullet.mp3")
        self.shotgun_sound = pygame.mixer.Sound("assets/Weapons/Shotgunbullet.wav")
        self.ak47_sound = pygame.mixer.Sound("assets/Weapons/AKbullet.wav")
        self.damage_sound = pygame.mixer.Sound("assets/Hero/Dead.mp3")
        self.damage_sound.set_volume(0.7)

    def update_gun_image(self):
        base_img = self.gun_images[self.current_gun]
        self.base_gun_image = pygame.transform.rotozoom(base_img, 0, PLAYER_SIZE)
        self.gun_image = pygame.transform.rotate(self.base_gun_image, -self.angle)
        self.gun_rect = self.gun_image.get_rect(center=self.hitbox_rect.center)
        self.barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, 0).rotate(-self.angle)

    def change_player(self, weapon_index):
        self.current_gun = weapon_index
        self.update_gun_image()

    def player_rotation(self):
        mouse_coords = pygame.mouse.get_pos()
        x_change_mouse_player = (mouse_coords[0] - WIDTH // 2)
        y_change_mouse_player = (mouse_coords[1] - HEIGHT // 2)
        self.angle = math.degrees(math.atan2(y_change_mouse_player, x_change_mouse_player))
        self.gun_image = pygame.transform.rotate(self.base_gun_image, -self.angle)
        self.gun_rect = self.gun_image.get_rect(center=self.hitbox_rect.center)
        self.barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, 0).rotate(-self.angle)

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
            spawn_pos = self.pos + self.barrel_offset
            
            if self.current_gun == 1:
                bullet = PistolBullet(spawn_pos.x, spawn_pos.y, self.angle)
                self.pistol_sound.play()
                self.shoot_cooldown = PistolBullet.COOLDOWN
            elif self.current_gun == 2:
                bullet = AK47Bullet(spawn_pos.x, spawn_pos.y, self.angle)
                self.ak47_sound.play()
                self.shoot_cooldown = AK47Bullet.COOLDOWN
            elif self.current_gun == 3:
                bullet = ShotgunBullet(spawn_pos.x, spawn_pos.y, self.angle)
                self.shotgun_sound.play()
                self.shoot_cooldown = ShotgunBullet.COOLDOWN

            bullet_group.add(bullet)

    def move(self, game_map):
        old_pos = self.pos.copy()
        
        self.pos.x += self.velocity_x
        self.hitbox_rect.centerx = self.pos.x
        self.rect.centerx = self.pos.x
        
        for obj in game_map.collision_objects:
            if self.hitbox_rect.colliderect(obj):
                self.pos.x = old_pos.x
                self.hitbox_rect.centerx = self.pos.x
                self.rect.centerx = self.pos.x
                break
        
        self.pos.y += self.velocity_y
        self.hitbox_rect.centery = self.pos.y
        self.rect.centery = self.pos.y
        
        for obj in game_map.collision_objects:
            if self.hitbox_rect.colliderect(obj):
                self.pos.y = old_pos.y
                self.hitbox_rect.centery = self.pos.y
                self.rect.centery = self.pos.y
                break
        
        self.pos.x = max(0, min(self.pos.x, game_map.map_width - self.rect.width))
        self.pos.y = max(0, min(self.pos.y, game_map.map_height - self.rect.height))
        self.hitbox_rect.center = self.pos
        self.rect.center = self.pos

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

    def update(self, game_map):
        self.user_input()
        self.move(game_map)
        self.player_rotation()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        bullet_group.update(game_map.collision_objects)

    def draw(self, screen, camera):
        screen.blit(self.base_player_image, self.rect.topleft - pygame.Vector2(camera.x, camera.y))
        gun_pos = self.gun_rect.topleft - pygame.Vector2(camera.x, camera.y)
        screen.blit(self.gun_image, gun_pos)

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
        self.collision_objects = self.get_collision_objects()
        self.spawn_point = self.get_spawn_point()

    def get_spawn_point(self):
        for layer in self.tmx_data.layers:
            if layer.name.lower() == "spawn" and hasattr(layer, 'objects'):
                for obj in layer.objects:
                    return (obj.x, obj.y)
        return (800, 1552)  # Fallback spawn point

    def get_collision_objects(self):
        collision_objects = []
        for layer in self.tmx_data.layers:
            if hasattr(layer, 'name') and layer.name.lower() == "collision":
                if hasattr(layer, 'objects'):
                    for obj in layer.objects:
                        collision_objects.append(pygame.Rect(
                            obj.x, obj.y, obj.width, obj.height
                        ))
                elif hasattr(layer, 'data'):
                    for x in range(self.tmx_data.width):
                        for y in range(self.tmx_data.height):
                            gid = layer.data[y][x]
                            if gid != 0:
                                collision_objects.append(pygame.Rect(
                                    x * self.tile_size, y * self.tile_size,
                                    self.tile_size, self.tile_size
                                ))
        return collision_objects
        
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
                        if gid != 0:
                            tile = self.tmx_data.get_tile_image_by_gid(gid)
                            if tile:
                                screen.blit(tile, 
                                          (x * self.tile_size - camera.x, 
                                           y * self.tile_size - camera.y))
            elif hasattr(layer, 'objects'): 
                for obj in layer.objects:
                    if hasattr(obj, 'gid') and obj.gid:
                        tile = self.tmx_data.get_tile_image_by_gid(obj.gid)
                        if tile:
                            screen.blit(tile, 
                                      (obj.x - camera.x, 
                                       obj.y - camera.y))
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, target, speed=ENEMY_SPEED, animation_speed=0.035, max_health=100):
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
        self.max_health = max_health
        self.health = max_health
        self.last_hit_time = 0
        self.hit_cooldown = 500  

    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time > self.hit_cooldown:
            self.health -= amount
            self.last_hit_time = current_time
            if self.health <= 0:
                self.kill()

    def update(self, game_state):
        if game_state == "game":
            self.check_collision()
            
            if not self.is_colliding:
                self.animate()
                self.move_towards_target()
            else:
                self.image = self.right_frames[self.current_frame] if self.last_facing else self.left_frames[self.current_frame]

            for bullet in bullet_group:
                if self.rect.colliderect(bullet.rect):
                    self.take_damage(bullet.damage)
                    bullet.kill()

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
        super().__init__(x, y, target, speed=1.5, animation_speed=0.02 , max_health=BOSS1_HP)
        
    def setup_frames(self):
        original_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Mob/Enemy2.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Mob/Enemy3.png").convert_alpha(), 0, ENEMY_SIZE)
        ]
        self.right_frames = [pygame.transform.rotozoom(frame, 0, ENEMY_SIZE) for frame in original_frames]
        self.left_frames = [pygame.transform.flip(frame, True, False) for frame in self.right_frames]

class Boss2(Enemy):
    def __init__(self, x, y, target):
        super().__init__(x, y, target, speed=2.5, animation_speed=1, max_health=BOSS2_HP)
        
    def setup_frames(self):
        original_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss_2/Spell.png").convert_alpha(), 0, ENEMY_SIZE),
        ]
        self.right_frames = [pygame.transform.rotozoom(frame, 0, ENEMY_SIZE) for frame in original_frames]
        self.left_frames = [pygame.transform.flip(frame, True, False) for frame in self.right_frames]

class Boss3(Enemy):
    def __init__(self, x, y, target):
        super().__init__(x, y, target, speed=2.0, animation_speed=0.035, max_health=BOSS3_HP)
        
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