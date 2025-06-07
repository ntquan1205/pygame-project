import pygame
import sys
from pytmx.util_pygame import load_pygame

# --- Настройки ---
WIDTH, HEIGHT = 1280, 720
FPS = 60
PLAYER_SPEED = 4

# --- Игрок ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.center)
        self.vel = pygame.Vector2(0, 0)

    def update(self, keys, collision_rects):
        self.vel.x = keys[pygame.K_d] - keys[pygame.K_a]
        self.vel.y = keys[pygame.K_s] - keys[pygame.K_w]
        if self.vel.length_squared() > 0:
            self.vel = self.vel.normalize() * PLAYER_SPEED

        next_pos = self.pos + self.vel
        next_rect = self.rect.copy()
        next_rect.center = next_pos

        if not any(next_rect.colliderect(rect) for rect in collision_rects):
            self.pos = next_pos
            self.rect.center = self.pos

# --- Загрузка карты ---
class TiledMap:
    def __init__(self, filename):
        self.tmx_data = load_pygame(filename)
        self.tile_size = self.tmx_data.tilewidth
        self.width = self.tmx_data.width * self.tile_size
        self.height = self.tmx_data.height * self.tile_size

    def draw(self, surface):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(tile, (x * self.tile_size, y * self.tile_size))

    def get_collision_rects(self):
        rects = []
        for layer in self.tmx_data.layers:
            if layer.name.lower() == "collision":
                for y in range(layer.height):
                    for x in range(layer.width):
                        tile = layer.data[y][x]
                        if tile:
                            rects.append(pygame.Rect(
                                x * self.tile_size, y * self.tile_size,
                                self.tile_size, self.tile_size
                            ))
        return rects

# --- Главный цикл ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    game_map = TiledMap("assets/map/dungeon1.tmx")
    collision_rects = game_map.get_collision_rects()

    player = Player(100, 100)

    while True:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        player.update(keys, collision_rects)

        screen.fill((0, 0, 0))
        game_map.draw(screen)
        screen.blit(player.image, player.rect)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
