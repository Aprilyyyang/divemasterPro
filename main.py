import sys
import time
import pygame
from random import *
from pygame.locals import *
import RPi.GPIO as GPIO
import os



# Initialize pygame and set up the display
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')

os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

pygame.init()
width = 320
height = 240
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

class Position(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

pygame.mixer.init()
#background1 = r'/home/pi/final_demo/background.mp3'
background1 = r'/home/pi/final_demo/background3.wav'
#background2 = r'/home/pi/final_demo/background4.mp3'
background2 = r'/home/pi/final_demo/background3.wav'
background3 = r'/home/pi/final_demo/background3.wav'
current_music = None

def play_background_music(background):
    pygame.init()
    pygame.mixer.init()
    global current_music
    if current_music is not None:
        current_music.stop()
    current_music = pygame.mixer.Sound(background)
    current_music.play(-1)

def exit_end():
    pygame.quit()
    quit()


def draw_text(surface, text, font, color, rect, max_width):
    words = text.split(' ')
    space_width, word_height = font.size(' ')
    current_line = []
    current_line_width = 0
    lines = []

    for word in words:
        word_width, _ = font.size(word)

        if current_line and current_line_width + space_width + word_width <= max_width:
            current_line.append(' ')
            current_line_width += space_width

        if current_line_width + word_width <= max_width:
            current_line.append(word)
            current_line_width += word_width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_line_width = word_width

    lines.append(' '.join(current_line))

    y = rect.y

    for line in lines:
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect(topleft=(rect.x, y))
        surface.blit(text_surface, text_rect)
        y += word_height

    return y - rect.y  # Return the total height used



def handle_start_screen_events(event, game_start_btn=None, game_mode_btn1=None, game_mode_btn2=None, music_btn=None):
    if event.type == pygame.MOUSEBUTTONUP:
        if game_start_btn and game_start_btn.collidepoint(event.pos):
            return True
        elif game_mode_btn1 and game_mode_btn1.collidepoint(event.pos):
            return 1
        elif game_mode_btn2 and game_mode_btn2.collidepoint(event.pos):
            return 2
        elif music_btn and music_btn.collidepoint(event.pos):
            return "music"
        elif return_btn and return_btn.collidepoint(event.pos):
            return 3  # Change this line to return the correct mode for "Return" button


def into_game():
    start_flag = False
    global return_btn
    mode = 0
    music_mode = 0 
    

    # Load  background image and scale it to 320x240
    original_background = pygame.image.load("OIP.jpg")
    background_image = pygame.transform.scale(original_background, (320, 240))

    # Load the additional image and scale it 
    additional_image = pygame.image.load("title3.png")
    additional_image = additional_image.convert()  # 转换为支持透明度的格式
    additional_image.set_colorkey((255, 255, 255))  # 将白色（255, 255, 255）设置为透明色
    additional_image = pygame.transform.scale(additional_image, (320, 90))

    while mode == 0:
        # Blit the background image
        screen.blit(background_image, (0, 0))

        # Blit the additional image in the of the screen
        screen.blit(additional_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_end()

            if not start_flag:
                game_start_btn = pygame.Rect(144, 110, 48, 40)
                pygame.draw.rect(screen, (255, 0, 0), game_start_btn)
                game_start_font = pygame.font.Font(None, 12)
                game_start_text = game_start_font.render("Start Game", True, (255, 255, 255))
                game_start_text_rect = game_start_text.get_rect(center=game_start_btn.center)
                screen.blit(game_start_text, game_start_text_rect)
                pygame.display.update()

                if event.type == pygame.MOUSEBUTTONUP:
                    if game_start_btn.collidepoint(event.pos):
                        start_flag = True
            else:
                # Define button positions
                btn_width = 68
                btn_height = 25
                btn_margin = 20
                btn1_x = int(width / 3) - btn_width - btn_margin + 30
                btn2_x = int(2 * width / 3) + btn_margin - 30
                btn_y = int(height / 3 + 15)
                
                 # Button 1

                game_mode_btn1 = pygame.Rect(btn1_x, btn_y, btn_width, btn_height * 2)
                pygame.draw.rect(screen, (255, 0, 0), game_mode_btn1)
                game_start_font = pygame.font.Font(None, 12)
                game_start_text = game_start_font.render("EASY", True, (255, 255, 255))
                game_start_text_rect = game_start_text.get_rect(center=game_mode_btn1.center)
                screen.blit(game_start_text, game_start_text_rect)
                 
                 # Button 2

                game_mode_btn2 = pygame.Rect(btn2_x, btn_y, btn_width, btn_height * 2)
                pygame.draw.rect(screen, (255, 0, 0), game_mode_btn2)
                game_start_text = game_start_font.render("HARD", True, (255, 255, 255))
                game_start_text_rect = game_start_text.get_rect(center=game_mode_btn2.center)
                screen.blit(game_start_text, game_start_text_rect)

                 # Button music

                music_btn = pygame.Rect(245, 210, btn_width, btn_height)
                pygame.draw.rect(screen, (0, 0, 255), music_btn)
                music_text = game_start_font.render("Music", True, (255, 255, 255))
                music_text_rect = music_text.get_rect(center=music_btn.center)
                screen.blit(music_text, music_text_rect)

                 # Button return

                return_btn = pygame.Rect(5, 210, btn_width, btn_height)
                pygame.draw.rect(screen, (0, 255, 0), return_btn)
                game_start_text = game_start_font.render("return", True,( 255, 255, 255))
                game_start_text_rect = game_start_text.get_rect(center=return_btn.center)
                screen.blit(game_start_text, game_start_text_rect)


                # Explain the game text box for Button 1
                
                text1 = "moving left and right"
                lines1 = text1.split('\n')
                text_rect1 = pygame.Rect(0, 0, btn_width, btn_height * len(lines1))
                text_surface1 = pygame.Surface((btn_width, btn_height * len(lines1)))
                text_surface1.set_colorkey((0, 0, 0))  # Make black transparent
                #text_surface1.fill((0,0,0))  # Set the background color, adjust as needed
                game_start_font = pygame.font.Font(None, 14) 
                # Adjust max_height here based on your preference
                #max_height1 = 200  # can change this value
                #draw_text(text_surface1, text1, game_start_font, (255, 255, 255), text_rect1, btn_width, max_height1)

               # text_rect1.topleft = (game_mode_btn1.centerx - btn_width / 2, game_mode_btn1.bottom + 10)
               # Example usage
                text_rect1 = pygame.Rect(0, 0, btn_width, 100)
                text_height1 = draw_text(text_surface1, text1, game_start_font, (0, 0, 255), text_rect1, btn_width)
                text_rect1.topleft = (game_mode_btn1.centerx - btn_width / 2, game_mode_btn1.bottom + 10)


                # Explain the game text box for Button 2
                text2 = "Bounce! Bomb! Crocodile!"
                lines2 = text2.split('\n')
                text_rect2 = pygame.Rect(0, 0, btn_width, btn_height * len(lines2))
                text_surface2 = pygame.Surface((btn_width, btn_height * len(lines2)))
                text_surface2.set_colorkey((0, 0, 0))  # Make black transparent
                text_rect2 = pygame.Rect(0, 0, btn_width, 100)
                text_height2 = draw_text(text_surface2, text2, game_start_font, (0,0,255), text_rect2, btn_width)
                text_rect2.topleft = (game_mode_btn2.centerx - btn_width / 2, game_mode_btn2.bottom + 10)


                screen.blit(text_surface1, text_rect1)
                screen.blit(text_surface2, text_rect2)

                pygame.display.update()

                event_result = handle_start_screen_events(event, game_start_btn, game_mode_btn1, game_mode_btn2, music_btn)
                if event.type == pygame.MOUSEBUTTONUP:
                    if game_mode_btn1.collidepoint(event.pos):
                        mode = 1
                    elif game_mode_btn2.collidepoint(event.pos):
                        mode = 2
                    elif return_btn.collidepoint(event.pos):
                        mode = 3

                if event_result == "music":
                    # Toggle through different music modes
                    music_mode = (music_mode + 1) % 4
                    if music_mode == 1:
                        # Play background music 1
                        play_background_music(background1)
                        print("Playing Background Music 1")
                    elif music_mode == 2:
                        # Play background music 2
                        play_background_music(background2)
                        print("Playing Background Music 2")
                    elif music_mode == 3:
                        # Play background music 3
                        play_background_music(background3)
                        print("Playing Background Music 3")
                    elif music_mode == 0:
                        # 不要背景音
                        current_music.stop()
                        print("no Background Music")
                        
                    
                

        clock.tick(15)

    if mode == 1:
        import easy
    elif mode == 2:
        import hard
    elif mode == 3:
        into_game()

if __name__ == '__main__':
    pygame.init()
    width = 320
    height = 240
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    into_game()
