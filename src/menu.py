import pygame
import random

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

        self.bg_main = pygame.image.load('assets/Menu1.jpg')
        self.bg_credits = pygame.image.load('assets/auth1.jpg')
        self.title_img = pygame.image.load('assets/Name.png')

        self.btn_about = Button('Об авторах', 100, 400, game)
        self.btn_start = Button('Начать игру', 100, 300, game)
        self.btn_settings = Button(' Настройки', 100, 500, game)
        self.btn_exit = Button('   Выход', 100, 600, game)
        self.btn_back = Button('    Назад', 65, 650, game)

    def update_snow(self):
        for snowflake in self.game.snow:
            pygame.draw.circle(self.game.screen, 'white', snowflake, 2)
            snowflake[1] += 1
            if snowflake[1] > self.game.HEIGHT:
                snowflake[1] = random.randrange(-50, -10)  
                snowflake[0] = random.randrange(0, self.game.WIDTH)


    def update(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False

        self.game.screen.fill((0, 0, 0))
        self.update_snow()

        if self.state == "main":
            self.game.screen.blit(self.bg_main, (0, 0))
            self.game.screen.blit(self.title_img, (190, -10))
            self.btn_about.draw()
            self.btn_start.draw()
            self.btn_settings.draw()
            self.btn_exit.draw()

            if self.btn_about.check_click(events):
                self.state = "about"
            elif self.btn_settings.check_click(events):
                self.state = "settings"
            elif self.btn_exit.check_click(events):
                self.game.running = False

        elif self.state == "about":
            self.game.screen.blit(self.bg_credits, (0, 0))
            self.btn_back.draw()
            if self.btn_back.check_click(events):
                self.state = "main"

        elif self.state == "settings":
            self.game.screen.blit(self.bg_main, (0, 0))
            self.game.screen.blit(self.title_img, (190, -10))
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

    def draw_volume_slider(self):
        pygame.draw.rect(self.game.screen, 'lightgrey', (400, 350, 400, 10))
        pygame.draw.circle(self.game.screen, 'black', (int(400 + self.volume * 400), 355), 15)
        vol_text = self.game.big_font.render(f'Громкость: {int(self.volume * 100)}%', True, 'black')
        pygame.draw.rect(self.game.screen, 'lightgrey', (140, 330, 250, 50))
        self.game.screen.blit(vol_text, (150, 345))
