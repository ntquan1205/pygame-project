import pygame
import random
from hero import *
from settings import *
import sys

screen = pygame.display.set_mode((WIDTH, HEIGHT))
bg_game = pygame.image.load("assets/InGame/ground.png").convert()
all_sprites_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

class Button:
    def __init__(self, text, x_pos, y_pos, game):
        self.text = text
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.game = game
        self.rect = pygame.Rect((x_pos, y_pos), (150, 50))

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        is_hover = self.rect.collidepoint(mouse_pos)
        color = 'gray'
        if is_hover and left_click:
            color = 'darkgray'
        elif is_hover:
            color = 'lightgray'
        pygame.draw.rect(self.game.screen, color, self.rect, 0, 5)
        pygame.draw.rect(self.game.screen, 'black', self.rect, 2, 5)
        text = self.game.font.render(self.text, True, 'black')
        self.game.screen.blit(text, (self.x_pos + 25, self.y_pos + 18))

    def check_click(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    return True
        return False
    
class MenuManager:
    def __init__(self, game):
        self.game = game
        self.state = "main"
        self.volume = 0.5

        self.bg_main = pygame.image.load('assets/Menu/Menu1.jpg')
        self.bg_credits = pygame.image.load('assets/Menu/auth1.jpg').convert()
        self.title_img = pygame.image.load('assets/Menu/Name.png')

        self.btn_about = Button('Об авторах', 100, 400, game)
        self.btn_start = Button('Начать игру', 100, 300, game)
        self.btn_settings = Button(' Настройки', 100, 500, game)
        self.btn_exit = Button('   Выход', 100, 600, game)
        self.btn_back = Button('    Назад', 65, 650, game)
        self.btn_resume = Button('Продолжить', 100, 300, game)
        self.btn_main_menu = Button('Главное меню', 100, 400, game)

        self.screen_width = WIDTH
        self.screen_height = HEIGHT

    def update_snow(self):
        for snowflake in self.game.snow:
            pygame.draw.circle(self.game.screen, 'white', snowflake, 2)
            snowflake[1] += 1
            if snowflake[1] > self.game.HEIGHT:
                snowflake[1] = random.randrange(-50, -10)  
                snowflake[0] = random.randrange(0, self.game.WIDTH)

    def fade_menu(self):
        fade_surface = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
        fade_surface.fill((0, 0, 0))
        for alpha in range(0, 255, 5):
            fade_surface.set_alpha(alpha)
            self.game.screen.blit(self.bg_main, (0, 0))  
            self.game.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.game.clock.tick(self.game.fps)

    def fade_waitingforstart(self):
        fade_surface = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
        fade_surface.fill((0, 0, 0))
        for alpha in range(255, 0, -5):
            fade_surface.set_alpha(alpha)
            self.game.screen.fill((0, 0, 255)) 
            start_text = self.game.font.render("Нажмите Enter, чтобы начать игру", True, 'white')
            self.game.screen.blit(start_text, (self.game.WIDTH // 2 - start_text.get_width() // 2, self.game.HEIGHT // 2 - start_text.get_height() // 2)) 
            self.game.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.game.clock.tick(self.game.fps)

    def update(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.game.screen.fill((0, 0, 0))

        if self.state == "main":
            self.game.screen.blit(self.bg_main, (0, 0))
            self.game.screen.blit(self.title_img, (190, -10))
            self.update_snow()
            self.btn_about.draw()
            self.btn_start.draw()
            self.btn_settings.draw()
            self.btn_exit.draw()

            if self.btn_about.check_click(events):
                self.state = "about"
            elif self.btn_settings.check_click(events):
                self.state = "settings"
            elif self.btn_exit.check_click(events):
                pygame.quit()
                sys.exit()
            elif self.btn_start.check_click(events):
                self.fade_menu()
                self.fade_waitingforstart()
                self.state = "waiting_for_start"
        elif self.state == "about":
            self.game.screen.blit(self.bg_credits, (0, 0))
            self.btn_back.draw()
            self.update_snow()
            if self.btn_back.check_click(events):
                self.state = "main"

        elif self.state == "settings":
            self.game.screen.blit(self.bg_main, (0, 0))
            self.game.screen.blit(self.title_img, (190, -10))
            self.update_snow()
            self.draw_volume_slider()
            self.btn_back.draw()

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if 400 <= mx <= 800 and 340 <= my <= 360:
                        self.volume = (mx - 400) / 400
                        pygame.mixer.music.set_volume(self.volume)

            if self.btn_back.check_click(events):
                self.state = "main"

        elif self.state == "waiting_for_start":
            self.game.screen.fill((0, 0, 255)) 
            start_text = self.game.font.render("Нажмите Enter, чтобы начать игру", True, 'white')
            self.game.screen.blit(start_text, (self.game.WIDTH // 2 - start_text.get_width() // 2, self.game.HEIGHT // 2 - start_text.get_height() // 2))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]: 
                self.state = "game"
                self.game.init_game()  

        elif self.state == "waiting_for_boss":
            self.game.screen.fill((0, 0, 255))  
            boss_text = self.game.big_font.render("Все враги побеждены! Готовьтесь к боссу!", True, 'white')
            continue_text = self.game.font.render("Нажмите Enter, чтобы продолжить", True, 'white')
            
            self.game.screen.blit(boss_text, (self.game.WIDTH // 2 - boss_text.get_width() // 2, self.game.HEIGHT // 2 - 50))
            self.game.screen.blit(continue_text, (self.game.WIDTH // 2 - continue_text.get_width() // 2, self.game.HEIGHT // 2 + 50))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                self.game.init_boss_level()  
                self.state = "game"  

        elif self.state == "pause":
            self.game.screen.blit(self.bg_main, (0, 0))
            self.game.screen.blit(self.title_img, (190, -10))
            self.update_snow()
            self.btn_resume.draw()
            self.btn_main_menu.draw()
            self.btn_back.draw()

            if self.btn_resume.check_click(events):
                self.state = "game"
            elif self.btn_main_menu.check_click(events) or self.btn_back.check_click(events):
                bullet_group.empty()
                enemy_group.empty()
                all_sprites_group.empty()
                
                if self.game.boss_level:
                    self.game.boss_music.stop()
                    self.game.boss_level = False
                    self.game.boss_level_initialized = False
                
                pygame.mixer.music.play(-1)
                self.state = "main"
        
    def draw_volume_slider(self):
        pygame.draw.rect(self.game.screen, 'lightgrey', (400, 350, 400, 10))
        pygame.draw.circle(self.game.screen, 'black', (int(400 + self.volume * 400), 355), 15)
        vol_text = self.game.big_font.render(f'Громкость: {int(self.volume * 100)}%', True, 'black')
        pygame.draw.rect(self.game.screen, 'lightgrey', (140, 330, 250, 50))
        self.game.screen.blit(vol_text, (150, 345))
        
