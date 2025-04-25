import pygame
import random

pygame.init()

pygame.mixer.music.load('assets/MenuTrack.ogg')
pygame.mixer.music.play(-1)

WIDTH = 1200
HEIGHT = 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Buttons!')

Menubackground = pygame.image.load('assets/Menu1.jpg')
Creditbackground = pygame.image.load('assets/auth1.jpg')

snow = [[random.randrange(0, WIDTH), random.randrange(0, HEIGHT)] for _ in range(50)]

fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 18)

class Button:
    def __init__(self, text, x_pos, y_pos, enabled=True):
        self.text = text
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.enabled = enabled
        self.rect = pygame.Rect((self.x_pos, self.y_pos), (150, 50))

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        is_hover = self.rect.collidepoint(mouse_pos)
        is_pressed = left_click and is_hover and self.enabled

        color = 'gray'
        if self.enabled:
            if is_pressed:
                color = 'dark gray'
            elif is_hover:
                color = 'light gray'

        pygame.draw.rect(screen, color, self.rect, 0, 5)
        pygame.draw.rect(screen, 'black', self.rect, 2, 5)

        button_text = font.render(self.text, True, 'black')
        screen.blit(button_text, (self.x_pos + 25, self.y_pos + 18))

    def check_click(self, new_press):
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        if left_click and self.rect.collidepoint(mouse_pos) and self.enabled and new_press:
            return True
        return False

current_screen = "main"
run = True
new_press = True

my_button1 = Button('Об авторах', 100, 400)
my_button2 = Button('Начать игру', 100, 300)
my_button3 = Button('Настройки', 100, 500)
my_button4 = Button('Выход', 100, 600)
back_button = Button('Назад', 65, 650)

while run:
    screen.fill((0, 0, 0))  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if current_screen == "main":
        screen.blit(Menubackground, (0, 0))

        for ice in range(len(snow)):
            pygame.draw.circle(screen, 'white', snow[ice], 2)
            snow[ice][1] += 1
            if snow[ice][1] > HEIGHT:
                snow[ice][1] = random.randrange(-50, -10)
                snow[ice][0] = random.randrange(0, WIDTH)

        my_button1.draw()
        my_button2.draw()
        my_button3.draw()
        my_button4.draw()

        if my_button1.check_click(new_press):
            current_screen = "about"
            new_press = False
        elif my_button4.check_click(new_press):
            run = False
            new_press = False

    elif current_screen == "about":
        screen.blit(Creditbackground, (0, 0))
        for ice in range(len(snow)):
            pygame.draw.circle(screen, 'white', snow[ice], 2)
            snow[ice][1] += 1
            if snow[ice][1] > HEIGHT:
                snow[ice][1] = random.randrange(-50, -10)
                snow[ice][0] = random.randrange(0, WIDTH)
        back_button.draw()
        if back_button.check_click(new_press):
            current_screen = "main"
            new_press = False

    if not pygame.mouse.get_pressed()[0]:
        new_press = True

    pygame.display.flip()
    timer.tick(fps)

pygame.quit()
