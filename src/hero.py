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

class CircularShot(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (10, 10), 10)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.direction = direction
        self.speed = speed
        self.damage = 1  # Damage dealt to player
        self.lifetime = 3000  # 3 seconds
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # Remove the shot if its lifetime has expired
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
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
        self.hit_mask = pygame.mask.from_surface(self.base_player_image)
        
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
        
        # Добавлено: направление взгляда персонажа
        self.facing_right = True

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
            self.facing_right = True  # Персонаж смотрит вправо
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.facing_right = False  # Персонаж смотрит влево

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
        # Отражаем спрайт персонажа если нужно
        player_image = self.base_player_image if self.facing_right else pygame.transform.flip(self.base_player_image, True, False)
        screen.blit(player_image, self.rect.topleft - pygame.Vector2(camera.x, camera.y))
        
        # Оружие рисуется как было (оно поворачивается отдельно)
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
    def __init__(self, map_path="assets/Map/dungeon1.tmx"):
        self.tmx_data = load_pygame(map_path)
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
        if "dungeon1.tmx" in self.tmx_data.filename:
            return (800, 1552) 
        else:  
            return (400, 720) 

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

        self.is_dead = False
        self.death_animation_frames = []
        self.death_animation_counter = 0
        self.death_animation_speed = 0.1
        self.current_death_frame = 0
        self.death_animation_done = False
        
        self.room_boundaries = None 
        self.is_active = False 

        self.damage_sound = None 
    
    def set_room_boundaries(self, left, top, right, bottom):
        self.room_boundaries = (left, top, right, bottom)

    def is_hero_in_room(self):
        if not self.room_boundaries:
            return True  
        left, top, right, bottom = self.room_boundaries
        hero_x, hero_y = self.target.pos.x, self.target.pos.y
        return (left <= hero_x <= right and 
                top <= hero_y <= bottom)

    def is_within_room(self, new_pos):
        if not self.room_boundaries:
            return True  
        left, top, right, bottom = self.room_boundaries
        return (left <= new_pos.x <= right and top <= new_pos.y <= bottom)

    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time > self.hit_cooldown:
            self.health -= amount
            self.last_hit_time = current_time
            if self.damage_sound:
                self.damage_sound.play()
            if self.health <= 0:
                self.health = 0
                self.is_dead = True
                self.setup_death_frames()
                return True  
        return False

    def setup_death_frames(self):
        pass

    def update(self, game_state):
        if game_state == "game":
            self.is_active = self.is_hero_in_room()
            
            if not self.is_dead:
                if self.is_active:  
                    self.check_collision()
                    
                    if not self.is_colliding:
                        self.animate()
                        self.move_towards_target()
                    else:
                        self.image = self.right_frames[self.current_frame] if self.last_facing else self.left_frames[self.current_frame]

                    # Only check bullet collisions when active
                    for bullet in bullet_group:
                        if self.rect.colliderect(bullet.rect):
                            self.take_damage(bullet.damage)
                            bullet.kill()
                else:
                    # When not active, show idle frame
                    self.image = self.right_frames[0] if self.facing_right else self.left_frames[0]
            else:
                self.death_animation_counter += self.death_animation_speed
                if self.death_animation_counter >= 1 and not self.death_animation_done:
                    self.death_animation_counter = 0
                    self.current_death_frame += 1
                    if self.current_death_frame >= len(self.death_animation_frames):
                        self.death_animation_done = True
                        self.kill()
                    else:
                        self.image = self.death_animation_frames[self.current_death_frame]

    def check_collision(self):
        if not self.is_active:
            return
        
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
   
        if not self.is_colliding and self.is_active:  # Only move if active
            direction = self.target.pos - self.pos
            distance = direction.length()
            if distance != 0:
                direction.normalize_ip()
            
                new_pos = self.pos + direction * self.speed
            
                if self.is_within_room(new_pos):
                    if direction.x > 0 and not self.facing_right:
                        self.facing_right = True
                        self.image = self.right_frames[self.current_frame]
                    elif direction.x < 0 and self.facing_right:
                        self.facing_right = False
                        self.image = self.left_frames[self.current_frame]
                
                    self.pos = new_pos
                    self.rect.center = self.pos
    

class Witch(Enemy):
    def __init__(self, x, y, target):
        super().__init__(x, y, target, speed=1.5, animation_speed=0.02 , max_health=BOSS1_HP)
        
    def setup_frames(self):
        original_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Witch/Enemy2.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Witch/Enemy3.png").convert_alpha(), 0, ENEMY_SIZE)
        ]
        self.right_frames = [pygame.transform.rotozoom(frame, 0, ENEMY_SIZE) for frame in original_frames]
        self.left_frames = [pygame.transform.flip(frame, True, False) for frame in self.right_frames]
    def setup_death_frames(self):
        self.death_animation_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Witch/D0.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Witch/D1.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Witch/D2.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Witch/D3.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Witch/D4.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Witch/D5.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Witch/D6.png").convert_alpha(), 0, ENEMY_SIZE_2)
        ]
        self.image = self.death_animation_frames[0]

class Skeleton1(Enemy):
    def __init__(self, x, y, target):
        super().__init__(x, y, target, speed=1.5, animation_speed=0.04 , max_health=BOSS1_HP)
        self.damage_sound = pygame.mixer.Sound("assets/Enemies/death-15.mp3")
        
    def setup_frames(self):
        original_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/W1.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/W2.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/W3.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/W4.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/W5.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/W6.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/W7.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/W8.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/W9.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/W10.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/W11.png").convert_alpha(), 0, ENEMY_SIZE)
        ]
        self.right_frames = [pygame.transform.rotozoom(frame, 0, ENEMY_SIZE) for frame in original_frames]
        self.left_frames = [pygame.transform.flip(frame, True, False) for frame in self.right_frames]
    def setup_death_frames(self):
        self.death_animation_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/dead-1.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/dead-2.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/dead-3.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/dead-4.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/dead-5.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton1/dead-6.png").convert_alpha(), 0, ENEMY_SIZE_2),
        ]
        self.image = self.death_animation_frames[0]

class Skeleton2(Enemy):
    def __init__(self, x, y, target):
        super().__init__(x, y, target, speed=1.5, animation_speed=0.04 , max_health=BOSS1_HP)
        self.damage_sound = pygame.mixer.Sound("assets/Enemies/death-15.mp3")
        
    def setup_frames(self):
        original_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton2/walk-1.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton2/walk-2.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton2/walk-3.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton2/walk-4.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton2/walk-5.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton2/walk-6.png").convert_alpha(), 0, ENEMY_SIZE)
        ]
        self.right_frames = [pygame.transform.rotozoom(frame, 0, ENEMY_SIZE) for frame in original_frames]
        self.left_frames = [pygame.transform.flip(frame, True, False) for frame in self.right_frames]
    def setup_death_frames(self):
        self.death_animation_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton2/dead-1.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton2/dead-2.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton2/dead-3.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton2/dead-4.png").convert_alpha(), 0, ENEMY_SIZE_2)

        ]
        self.image = self.death_animation_frames[0]

class Boss(Enemy):
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

    def setup_death_frames(self):
        self.death_animation_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Death_1.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Death_2.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Death_3.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Death_4.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Death_5.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Death_6.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Death_7.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Death_8.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Death_9.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Boss/Bringer-of-Death_Death_10.png").convert_alpha(), 0, ENEMY_SIZE_2)
        ]
        self.image = self.death_animation_frames[0]
        
class Skeleton3(Enemy):
    def __init__(self, x, y, target):
        super().__init__(x, y, target, speed=1.5, animation_speed=0.035 , max_health=BOSS1_HP)
        self.damage_sound = pygame.mixer.Sound("assets/Enemies/death-15.mp3")
        
    def setup_frames(self):
        original_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton3/walk-1.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton3/walk-2.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton3/walk-3.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton3/walk-4.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton3/walk-5.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton3/walk-6.png").convert_alpha(), 0, ENEMY_SIZE),
        ]
        self.right_frames = [pygame.transform.rotozoom(frame, 0, ENEMY_SIZE) for frame in original_frames]
        self.left_frames = [pygame.transform.flip(frame, True, False) for frame in self.right_frames]
    def setup_death_frames(self):
        self.death_animation_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton3/dead-1.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton3/dead-2.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton3/dead-3.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton3/dead-4.png").convert_alpha(), 0, ENEMY_SIZE_2),
        ]
        self.image = self.death_animation_frames[0]
        
class Skeleton4(Enemy):
    def __init__(self, x, y, target):
        super().__init__(x, y, target, speed=1.5, animation_speed=0.02 , max_health=BOSS1_HP)
        self.damage_sound = pygame.mixer.Sound("assets/Enemies/death-15.mp3")
        
    def setup_frames(self):
        original_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton4/walk-1.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton4/walk-2.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton4/walk-3.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton4/walk-4.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton4/walk-5.png").convert_alpha(), 0, ENEMY_SIZE),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton4/walk-6.png").convert_alpha(), 0, ENEMY_SIZE),
        ]
        self.right_frames = [pygame.transform.rotozoom(frame, 0, ENEMY_SIZE) for frame in original_frames]
        self.left_frames = [pygame.transform.flip(frame, True, False) for frame in self.right_frames]
    def setup_death_frames(self):
        self.death_animation_frames = [
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton4/dead-1.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton4/dead-2.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton4/dead-3.png").convert_alpha(), 0, ENEMY_SIZE_2),
            pygame.transform.rotozoom(pygame.image.load("assets/Enemies/Skeleton4/dead-4.png").convert_alpha(), 0, ENEMY_SIZE_2),
        ]
        self.image = self.death_animation_frames[0]

class Laser(pygame.sprite.Sprite):
    def __init__(self, owner, target, length=250, duration=2.5):
        super().__init__()
        self.owner = owner
        self.target = target
        self.length = length
        self.duration = duration
        self.spawn_time = pygame.time.get_ticks()
        self.last_damage_time = 0
        self.damage = 0.5
        self.damage_cooldown = 300
        self.width = 8
        
        # Анимационные параметры
        self.current_length = 0
        self.growing_speed = 20
        self.angle = 0
        self.image = None
        self.rect = None
        self.mask = None
        self.update_direction()

    def update_direction(self):
        # Рассчитываем направление к цели
        dx = self.target.pos.x - self.owner.rect.centerx
        dy = self.target.pos.y - self.owner.rect.centery
        self.angle = math.degrees(math.atan2(-dy, dx))
        
        # Плавное увеличение длины
        if self.current_length < self.length:
            self.current_length = min(self.current_length + self.growing_speed, self.length)
        
        # Создаем изображение луча
        self.original_image = pygame.Surface((self.current_length, self.width), pygame.SRCALPHA)
        
        # Рисуем градиент (от яркого у глаза к тусклому на конце)
        for i in range(int(self.current_length)):
            alpha = int(255 * (1 - i/self.current_length)**0.5)
            color = (255, 50, 50, alpha)
            pygame.draw.line(self.original_image, color, (i, 0), (i, self.width), 1)
        
        # Яркое основание
        pygame.draw.rect(self.original_image, (255, 100, 100, 255), (0, 0, 15, self.width))
        
        # Поворачиваем изображение
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        
        # Ключевое изменение: позиционируем луч так, чтобы он начинался из центра глаза
        direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
        start_pos = pygame.math.Vector2(self.owner.rect.centerx, self.owner.rect.centery)
        
        # Устанавливаем позицию лазера (начало + половина длины в направлении луча)
        self.rect.center = start_pos + direction * self.current_length / 2
        
        # Обновляем маску
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.update_direction()
        if pygame.time.get_ticks() - self.spawn_time > self.duration * 1000:
            self.kill()
            return False
        return True
            
    def check_hit(self, player):
        if hasattr(player, 'hit_mask') and self.current_length == self.length:
            offset = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
            if self.mask.overlap(player.hit_mask, offset):
                current_time = pygame.time.get_ticks()
                if current_time - self.last_damage_time > self.damage_cooldown:
                    self.last_damage_time = current_time
                    return True
        return False
    
class EYEBOSS(Enemy):
    def __init__(self, x, y, target):
        super().__init__(x, y, target, speed=0, animation_speed=0.1, max_health=1000)
        
        self.setup_frames()
        self.image = self.right_frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.setup_death_frames()
        
        self.float_offset = 0
        self.float_speed = 0.05
        self.float_height = 3
        
        self.last_teleport_time = pygame.time.get_ticks()
        self.teleport_cooldown = 5000
        self.teleport_spots = [
            (157, 150), (642, 150),
            (651, 450), (155, 450)
        ]
        
        self.shots = pygame.sprite.Group()
        self.circular_attack_cooldown = 2000
        self.last_circular_attack = 0
        self.shot_speed = 2
        self.shot_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.shot_image, (255, 0, 0), (10, 10), 10)
        
        self.laser = None
        self.laser_cooldown = 10000 
        self.last_laser_time = 0
        self.laser_duration = 3000  
        self.laser_sound = pygame.mixer.Sound("assets/Music/surovyiy-lazernyiy-gul.mp3")

    def setup_frames(self):
        try:
            original_frames = [
                pygame.transform.scale(
                    pygame.image.load(f"assets/Enemies/EYEBOSS/Idle/Eye Beast Idle{i+1}.png").convert_alpha(),
                    (150, 150))
                for i in range(20)
            ]
            self.left_frames = original_frames
            self.right_frames = [pygame.transform.flip(frame, True, False) for frame in original_frames]
        except:
            fallback_surface = pygame.Surface((150, 150), pygame.SRCALPHA)
            pygame.draw.circle(fallback_surface, (255, 0, 0), (75, 75), 75)
            self.left_frames = [fallback_surface]
            self.right_frames = [fallback_surface]

    def setup_death_frames(self):
        try:
            self.death_animation_frames = [
                pygame.transform.scale(
                    pygame.image.load(f"assets/Enemies/EYEBOSS/Death/Eye Beast Death{i+1}.png").convert_alpha(),
                    (150, 150))
                for i in range(10) 
            ]
        except:
            self.death_animation_frames = []
            for i in range(10):
                surface = pygame.Surface((150, 150), pygame.SRCALPHA)
                color = (255, 0, 0, 255 - i*25)  
                pygame.draw.circle(surface, color, (75, 75), 75 - i*7) 
                self.death_animation_frames.append(surface)
        
        self.image = self.death_animation_frames[0] if self.death_animation_frames else self.image

    def circular_attack(self):
        now = pygame.time.get_ticks()
        if now - self.last_circular_attack > self.circular_attack_cooldown:
            self.last_circular_attack = now
            
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
                
                shot = CircularShot(
                    self.rect.centerx,
                    self.rect.centery,
                    direction,
                    self.shot_speed
                )
                self.shots.add(shot)

    def laser_attack(self):
        now = pygame.time.get_ticks()
        
        if now - self.last_laser_time > self.laser_cooldown and not self.laser:
            self.laser = Laser(self, self.target)
            self.laser_sound.play()
            self.last_laser_time = now
        
        if self.laser:
            if not self.laser.update():
                self.laser = None
            elif self.laser.check_hit(self.target):
                self.target.take_damage(self.laser.damage)

    def teleport(self):
        available_spots = [spot for spot in self.teleport_spots 
                         if spot != (self.pos.x, self.pos.y)]
        if available_spots:
            new_x, new_y = random.choice(available_spots)
            self.pos = pygame.math.Vector2(new_x, new_y)
            self.rect.center = (new_x, new_y)

    def update(self, game_state="game"):
        if self.is_dead:
            self.death_animation_counter += self.death_animation_speed
            if self.death_animation_counter >= 1 and not self.death_animation_done:
                self.death_animation_counter = 0
                self.current_death_frame += 1
                if self.current_death_frame >= len(self.death_animation_frames):
                    self.death_animation_done = True
                    self.kill()
                else:
                    self.image = self.death_animation_frames[self.current_death_frame]
            return
        
        now = pygame.time.get_ticks()
        
        if now - self.last_teleport_time > self.teleport_cooldown:
            self.teleport()
            self.last_teleport_time = now
        
        if self.target:
            self.facing_right = self.target.pos.x > self.pos.x
            frames = self.right_frames if self.facing_right else self.left_frames
            self.image = frames[int(self.current_frame) % len(frames)]
        
        self.circular_attack()
        self.shots.update()
        self.laser_attack()
        
        self.float_offset += self.float_speed
        self.rect.y = self.pos.y + math.sin(self.float_offset) * self.float_height
        
        super().update(game_state)

    def draw_shots(self, surface, camera):
        for shot in self.shots:
            surface.blit(shot.image, (shot.rect.x - camera.x, shot.rect.y - camera.y))
        
        if self.laser:
            surface.blit(self.laser.image, 
                    (self.laser.rect.x - camera.x, 
                        self.laser.rect.y - camera.y))
            
class Cat(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        super().__init__()
        self.game = game
        self.world_pos = pygame.math.Vector2(x, y)  # World position
        self.screen_pos = pygame.math.Vector2(x, y)  # Screen position (will be updated)
        self.load_frames()
        self.current_frame = 0
        self.animation_speed = 0.1
        self.animation_counter = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=self.screen_pos)
        
    def load_frames(self):
        self.frames = []
        for i in range(1, 5):  # cat1.png to cat4.png
            try:
                frame = pygame.image.load(f"assets/Cat/Box{i}.png").convert_alpha()
                frame = pygame.transform.scale(frame, (50, 50))  # Adjust size as needed
                self.frames.append(frame)
            except:
                fallback = pygame.Surface((50, 50), pygame.SRCALPHA)
                pygame.draw.circle(fallback, (255, 165, 0), (25, 25), 25)
                self.frames.append(fallback)
    
    def update(self, camera):
        # Update animation
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
        
        # Update screen position based on camera
        self.screen_pos.x = self.world_pos.x - camera.x
        self.screen_pos.y = self.world_pos.y - camera.y
        self.rect.center = self.screen_pos
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
        # Draw enemy counter
        if hasattr(self.game, 'enemies_killed') and hasattr(self.game, 'total_enemies'):
            enemies_left = max(0, self.game.total_enemies - self.game.enemies_killed)
            counter_text = self.game.font.render(f"Enemies left: {enemies_left}", True, (255, 255, 255))
            text_rect = counter_text.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
            
            # Draw background for text
            pygame.draw.rect(screen, (0, 0, 0), 
                           (text_rect.x - 5, text_rect.y - 5, 
                            text_rect.width + 10, text_rect.height + 10))
            pygame.draw.rect(screen, (255, 255, 255), 
                           (text_rect.x - 5, text_rect.y - 5, 
                            text_rect.width + 10, text_rect.height + 10), 2)
            
            screen.blit(counter_text, text_rect)