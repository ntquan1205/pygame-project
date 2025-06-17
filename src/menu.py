import pygame
import random
from characters import *
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
        self.rect = pygame.Rect((x_pos, y_pos), (250, 50))

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
        self.game.screen.blit(text, (self.x_pos + 75, self.y_pos + 18))

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

        self.bg_main = pygame.image.load('assets/Menu/test.png').convert()
        self.bg_main = pygame.transform.scale(self.bg_main, (WIDTH, HEIGHT))

        self.bg_credits = pygame.image.load('assets/Menu/authors.png').convert()
        self.bg_credits = pygame.transform.scale(self.bg_credits, (WIDTH, HEIGHT))

        self.btn_start = Button('Начать игру', WIDTH // 2.5, 325, game)
        self.btn_about = Button('Об авторах', WIDTH // 2.5, 425, game)
        self.btn_settings = Button(' Настройки', WIDTH // 2.5, 525, game)
        self.btn_exit = Button('   Выход', WIDTH // 2.5, 625, game)
        self.btn_back = Button('    Назад', 100, 650, game)
        self.btn_resume = Button('Продолжить', WIDTH // 2.5, 375, game)
        self.btn_main_menu = Button('Главное меню', WIDTH // 2.5, 475, game)

        self.screen_width = WIDTH
        self.screen_height = HEIGHT

        self.btn_retry = Button('Попробовать снова', WIDTH // 2.5, 425, game)

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
            if self.btn_back.check_click(events):
                self.state = "main"

        elif self.state == "settings":
            self.game.screen.blit(self.bg_main, (0, 0))
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

            self.btn_resume.draw()
            self.btn_main_menu.draw()

            if self.btn_resume.check_click(events):
                self.state = "game"
            elif self.btn_main_menu.check_click(events):
                bullet_group.empty()
                enemy_group.empty()
                all_sprites_group.empty()
                
                if self.game.boss_level:
                    self.game.boss_music.stop()
                    self.game.boss_level = False
                    self.game.boss_level_initialized = False
                
                pygame.mixer.music.play(-1)
                self.state = "main"

        elif self.state == "game_over":
            self.game.screen.fill((0, 0, 0))
            game_over_text = self.game.big_font.render("Игра Окончена!", True, 'red')
            continue_text = self.game.font.render("Нажмите Enter, чтобы вернуться в меню", True, 'white')
            
            self.game.screen.blit(game_over_text, (self.game.WIDTH // 2 - game_over_text.get_width() // 2, self.game.HEIGHT // 2 - 100))
            self.game.screen.blit(continue_text, (self.game.WIDTH // 2 - continue_text.get_width() // 2, self.game.HEIGHT // 2 + 100))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
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
        
        slider_x = int(400 + self.volume * 400)
        slider_rect = pygame.Rect(slider_x - 15, 340, 30, 30) 
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        if mouse_pressed:
            if slider_rect.collidepoint(mouse_pos) and not hasattr(self, 'dragging_volume'):
                self.dragging_volume = True
        else:
            if hasattr(self, 'dragging_volume'):
                del self.dragging_volume
        
        if hasattr(self, 'dragging_volume'):
            new_volume = (mouse_pos[0] - 400) / 400
            self.volume = max(0, min(1, new_volume))  

            pygame.mixer.music.set_volume(self.volume)
            self.game.boss_music.set_volume(self.volume)
        
        pygame.draw.circle(self.game.screen, 'black', (slider_x, 355), 15)
        
        vol_text = self.game.big_font.render(f'Громкость: {int(self.volume * 100)}%', True, 'black')
        pygame.draw.rect(self.game.screen, 'lightgrey', (140, 330, 250, 50))
        self.game.screen.blit(vol_text, (150, 345))