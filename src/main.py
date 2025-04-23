import pygame
import random

pygame.init()

WIDTH = 1000
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))

snow = []
for i in range(50):
    x = random.randrange(0, WIDTH)
    y = random.randrange(0, HEIGHT)
    snow.append([x, y])

fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 18)
pygame.display.set_caption('Buttons!')

button1_enabled = True
new_press = True

class Button:
    def __init__(self, text, x_pos, y_pos, enabled):
        self.text = text
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.enabled = enabled

    def draw(self):
        button_text = font.render(self.text, True, 'black')
        button_rect = pygame.Rect((self.x_pos, self.y_pos), (150, 50))
        
        if self.enabled:
            if self.check_click():
                pygame.draw.rect(screen, 'dark gray', button_rect, 0, 5)
            else:
                pygame.draw.rect(screen, 'light gray', button_rect, 0, 5)
        else:
            pygame.draw.rect(screen, 'gray', button_rect, 0, 5)

        pygame.draw.rect(screen, 'black', button_rect, 2, 5)
        screen.blit(button_text, (self.x_pos + 25, self.y_pos + 18))

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        button_rect = pygame.Rect((self.x_pos, self.y_pos), (150, 50))
        
        if left_click and button_rect.collidepoint(mouse_pos) and self.enabled:
            return True
        return False

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    screen.fill('sky blue')
    
    for ice in range(len(snow)):
        pygame.draw.circle(screen, 'white', snow[ice], 2)
        snow[ice][1] += 1 
        if snow[ice][1] > HEIGHT: 
            snow[ice][1] = random.randrange(-50,-10)
            snow[ice][0] = random.randrange(0, WIDTH)

    my_button2 = Button('Начать игру', 100,300, True)
    my_button2.draw()
    
    my_button1 = Button('Об авторах', 100,400, button1_enabled)
    my_button1.draw()
    
    my_button3 = Button('Настройки', 100, 500, True)
    my_button3.draw()
    
    my_button4 = Button('Выход', 100, 600, True)
    my_button4.draw()

    if pygame.mouse.get_pressed()[0] and new_press:
        new_press = False
        
        if my_button4.check_click():
            run = False
            
    if not pygame.mouse.get_pressed()[0] and not new_press:
        new_press = True
    pygame.display.flip()
    timer.tick(fps)

pygame.quit()