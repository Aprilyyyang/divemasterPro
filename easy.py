import pygame
import sys
import time
import pygame.transform
import RPi.GPIO as GPIO
from pygame.locals import *
import os
import main


pygame.mixer.init()
#score_sound_channel = pygame.mixer.Channel(1)
#background_channel = pygame.mixer.Channel(2)

player1_pin = 26
player2_pin = 13
player3_pin = 19

GPIO.setmode(GPIO.BCM)
GPIO.setup(player1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(player2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(player3_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize pygame and set up the display
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')

os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')



# Initialize pygame and set up the display

# 初始化
pygame.init()

width = 320  #1000
height = 240  #700

screen = pygame.display.set_mode((width, height))

# 记录一下像素，方便以后修改
ring_width_pixel = ring_height_pixel = 80

diver_1_width_pixel = diver_1_height_pixel = diver_2_width_pixel = diver_2_height_pixel = diver_3_width_pixel = diver_3_height_pixel = 50

pool_width_pixel = 320
pool_height_pixel = 240

# 加载资源
bg_img = pygame.image.load('pool.png')
ring_img = pygame.image.load('ring.png')
diver_1_img = pygame.image.load('diver_1.png')
diver_2_img = pygame.image.load('diver_2.png')
diver_3_img = pygame.image.load('diver_3.png')
font = pygame.font.Font(None, 15)

#sound_player1 = pygame.mixer.Sound('jump.wav')
#background = pygame.mixer.Sound('background.wav')
score_sound1 = r'score.mp3'
score_sound2 = r'no_score.mp3'





ring_x = 0
ring_y = (height - ring_height_pixel) // 2 - 20  # 居中

ring_speed = 2
ring_direction = 1  #控制不一样的方向的

diver_1_x = 60
diver_1_y = 170
diver_2_x = 135
diver_2_y = 170
diver_3_x = 210
diver_3_y = 170
score_1 = score_2 = score_3 = 0
jumping_1 = False
jumping_2 = False
jumping_3 = False
jump_ready = False

game_started = True
jump_game = False

# 新增平移标志和计数器
move_diver_1_ring = False
move_diver_2_ring = False
move_diver_3_ring = False
move_count_1 = move_count_2 = move_count_3 = 0

unchanged_diver_1_x = unchanged_diver_2_x = unchanged_diver_3_x = 0

#the score that the game ends!!!!! 
end_score = 10



# 添加两个按钮
player2_btn = pygame.Rect(135, 222, 50, 15)  # 用于控制 diver_2 的按钮 diver1是中间的那个
#player1_btn = pygame.Rect(210, 650, 80, 50)  # 用于控制 diver_1 的按钮
player1_btn = pygame.Rect(60, 222, 50, 15) #手动算出

player3_btn = pygame.Rect(210, 222, 50, 15)  # 用于控制 diver_3 的按钮
pygame.draw.rect(screen, (0, 0, 255), player1_btn)  # 设置颜色为蓝色 (0, 0, 255)
pygame.draw.rect(screen, (0, 255, 0), player2_btn)  # 设置颜色为绿色 (0, 255, 0)
pygame.draw.rect(screen, (255, 255, 255), player3_btn)  # 设置颜色为白色



# 主循环
clock = pygame.time.Clock()

player1_btn_pressed = False
player2_btn_pressed = False
player3_btn_pressed = False


def create_return_button(screen):
    return_btn = pygame.Rect(10, 216, 40, 20)  # 10, 10 是按钮的坐标，位于左上角
    pygame.draw.rect(screen, (0, 255, 0), return_btn)  # 使用绿色绘制按钮
    font = pygame.font.Font(None, 18)
    text = font.render("Return", True, (255, 255, 255))  # 白色文字
    text_rect = text.get_rect(center=return_btn.center)
    screen.blit(text, text_rect)
    return return_btn

# Function to play the score sound effect
def play_score_sound(score_sound):
    #sound_player1 = pygame.mixer.Sound('jump.wav')
    pygame.mixer.music.load(score_sound)
    pygame.mixer.music.play()

def player1_pressed():
    global jumping_1, move_diver_1_ring
    global player1_btn, player2_btn, player3_btn
    global player1_btn_pressed, player2_btn_pressed, player3_btn_pressed, jump_game, diver_1_y, move_count_1, diver_2_y, move_count_2, diver_3_y, move_count_3 
    player1_btn_pressed = True
    player2_btn_pressed = False
    player3_btn_pressed = False
    jump_game = True
    jumping_1 = True
    diver_1_y = 170
    move_diver_1_ring = False
    move_count_1 = 0

def player2_pressed():
    global jumping_2, move_diver_2_ring
    global player1_btn, player2_btn, player3_btn
    global player1_btn_pressed, player2_btn_pressed, player3_btn_pressed, jump_game, diver_1_y, move_count_1, diver_2_y, move_count_2, diver_3_y, move_count_3 
    player1_btn_pressed = False
    player2_btn_pressed = True
    player3_btn_pressed = False
    jump_game = True
    jumping_2 = True
    diver_2_y = 170
    move_diver_2_ring = False
    move_count_2 = 0

def player3_pressed():
    global jumping_3, move_diver_3_ring
    global player1_btn, player2_btn, player3_btn
    global player1_btn_pressed, player2_btn_pressed, player3_btn_pressed, jump_game, diver_1_y, move_count_1, diver_2_y, move_count_2, diver_3_y, move_count_3 
    player1_btn_pressed = False
    player2_btn_pressed = False
    player3_btn_pressed = True
    jump_game = True
    jumping_3 = True
    diver_3_y = 170
    move_diver_3_ring = False
    move_count_3 = 0   

    # 处理游戏中的事件
def handle_mouse_events(event):
    # ...（之前的处理逻辑）
    global player1_btn, player2_btn, player3_btn
    if event.type == pygame.MOUSEBUTTONUP:
        if player1_btn.collidepoint(event.pos):
            player1_pressed()
        if player2_btn.collidepoint(event.pos):
            player2_pressed()
        if player3_btn.collidepoint(event.pos):
            player3_pressed()

def handle_keyboard_events(event):
    # ...（之前的处理逻辑）
    global jumping_1, jumping_2, jumping_3, move_diver_1_ring, move_diver_2_ring, move_diver_3_ring
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_w:
            player1_pressed()
        if event.key == pygame.K_SPACE:
            player2_pressed()        
        if event.key == pygame.K_p:
            player3_pressed()




# 处理开始屏幕中的事件
def handle_start_screen_events(event):
    try:
        global game_started
        global game_start_btn
        if event.type == pygame.MOUSEBUTTONUP:
            if game_start_btn.collidepoint(event.pos):
                game_started = True
    except:
        pass


def draw_3_buttons():  #在游戏中画按钮
    player2_btn = pygame.Rect(135, 222, 50, 15)  # 用于控制 diver_2 的按钮 diver1是中间的那个
    #player1_btn = pygame.Rect(210, 650, 80, 50)  # 用于控制 diver_1 的按钮
    player1_btn = pygame.Rect(60, 222, 50, 15) #手动算出
    player3_btn = pygame.Rect(210, 222, 50, 15)  # 用于控制 diver_3 的按钮
    pygame.draw.rect(screen, (0, 0, 255), player1_btn)  # 设置颜色为蓝色 (0, 0, 255)
    pygame.draw.rect(screen, (0, 255, 0), player2_btn)  # 设置颜色为绿色 (0, 255, 0)
    pygame.draw.rect(screen, (255, 255, 255), player3_btn)  # 设置颜色为白色

def draw_divers_bg():
        screen.blit(diver_1_img, (diver_1_x, diver_1_y))
        screen.blit(diver_2_img, (diver_2_x, diver_2_y))
        screen.blit(diver_3_img, (diver_3_x, diver_3_y))
        screen.blit(bg_img, (0, 0))

def ring_control():
    global jump_ready, move_count_1, move_count_2, ring_x, ring_speed, ring_direction
    ring_x += ring_speed
    if ring_x > width or ring_x < -ring_width_pixel+10:
            #ring_x = 0
        ring_direction *= -1
        
        #ring_speed += 1 #为了增加游戏难度！每一轮都加速
        #ring_speed = ring_speed * ring_direction
        #有效解决了问题！
        ring_speed = (abs(ring_speed) + 0.05) * ring_direction

        jump_ready = True
        move_count_1 = 0
        move_count_2 =0
    screen.blit(ring_img, (ring_x, ring_y))

def jumping(): #diver jumps的过程
    global jumping_1, diver_1_y, jumping_2, diver_2_y, jumping_3, diver_3_y, height, diver_1_height_pixel, diver_2_height_pixel, diver_3_height_pixel
    if jumping_1:
        #diver_1_y -= 8
        diver_1_y -= 3
        #if diver_1_y < ((height - diver_1_height_pixel) // 2 - 20):
        if diver_1_y < ((height - diver_1_height_pixel) // 2):
            jumping_1 = False

    if jumping_2:
        diver_2_y -= 3
        if diver_2_y < ((height - diver_2_height_pixel) // 2):
            jumping_2 = False

    if jumping_3:
        diver_3_y -= 3
        if diver_3_y < ((height - diver_3_height_pixel) // 2):
            jumping_3 = False

def tranform_diver1():
    global move_diver_1_ring, diver_1_x, diver_1_y, diver_1_width_pixel, diver_1_height_pixel
    global height, diver_2_height_pixel, diver_1_img, screen, unchanged_diver_1_x, scaled_diver_1_img

    if not move_diver_1_ring:
                #为了平滑跳动
        diver_1_center_x = diver_1_x + diver_1_width_pixel // 2

        #if ((height - diver_1_height_pixel) // 2) <= diver_1_y <= 580:
        if ((height - diver_1_height_pixel) // 2) <= diver_1_y <= 170:
                # 计算缩放比例，范围从1.0到0.25
                    #scale_factor = 1.0 - (diver_1_y - 580) / (((height - diver_2_height_pixel) // 2) - 580) * 0.75
                    scale_factor = 1.0 - (diver_1_y - 170) / (((height - diver_1_height_pixel) // 2) - 170) * 0.75


                    # 缩小图像以实现平滑跳动
                    scaled_diver_1_img = pygame.transform.scale(diver_1_img, (int(diver_1_width_pixel * scale_factor), int(diver_1_height_pixel * scale_factor)))
                    #为了中心不变！！！！！这很困难的 还好我算出来了
                    unchanged_diver_1_x = diver_1_center_x - scaled_diver_1_img.get_width() // 2

                    #screen.blit(scaled_diver_1_img, (diver_1_x, diver_1_y))
                    screen.blit(scaled_diver_1_img, (unchanged_diver_1_x, diver_1_y))
                #elif diver_1_y == ((height - diver_2_height_pixel) // 2 ):
                    # 缩小为四分之一
                    #scaled_diver_1_img = pygame.transform.scale(diver_1_img, (diver_1_width_pixel // 4, diver_2_height_pixel // 4))
                    #screen.blit(scaled_diver_1_img, (diver_1_x, diver_1_y))
                #else:
                    #screen.blit(diver_1_img, (diver_1_x, diver_1_y))

def transform_diver2():
    global move_diver_2_ring, diver_2_x, diver_2_y, diver_2_width_pixel, diver_2_height_pixel
    global height, diver_2_height_pixel, diver_2_img, screen, unchanged_diver_2_x, scaled_diver_2_img
    if not move_diver_2_ring:
            #screen.blit(diver_2_img, (diver_2_x, diver_2_y))

                diver_2_center_x = diver_2_x + diver_2_width_pixel // 2

                if ((height - diver_2_height_pixel) // 2) <= diver_2_y <= 170:
                # 计算缩放比例，范围从1.0到0.25
                    scale_factor = 1.0 - (diver_2_y - 170) / (((height - diver_2_height_pixel) // 2) - 170) * 0.75

                    # 缩小图像以实现平滑跳动
                    scaled_diver_2_img = pygame.transform.scale(diver_2_img, (int(diver_2_width_pixel * scale_factor), int(diver_2_height_pixel * scale_factor)))
                    #为了中心不变！！！！！
                    unchanged_diver_2_x = diver_2_center_x - scaled_diver_2_img.get_width() // 2

                    screen.blit(scaled_diver_2_img, (unchanged_diver_2_x, diver_2_y))

def transform_diver3():
    global move_diver_3_ring, diver_3_x, diver_3_y, diver_3_width_pixel, diver_3_height_pixel
    global height, diver_3_height_pixel, diver_3_img, screen, unchanged_diver_3_x, scaled_diver_3_img
    if not move_diver_3_ring:
            #screen.blit(diver_3_img, (diver_3_x, diver_3_y))
            diver_3_center_x = diver_3_x + diver_3_width_pixel // 2

            if ((height - diver_3_height_pixel) // 2) <= diver_3_y <= 170:
                # 计算缩放比例，范围从1.0到0.25
                    scale_factor = 1.0 - (diver_3_y - 170) / (((height - diver_3_height_pixel) // 2) - 170) * 0.75

                    # 缩小图像以实现平滑跳动
                    scaled_diver_3_img = pygame.transform.scale(diver_3_img, (int(diver_3_width_pixel * scale_factor), int(diver_3_height_pixel * scale_factor)))
                    #为了中心不变！！！！！
                    unchanged_diver_3_x = diver_3_center_x - scaled_diver_3_img.get_width() // 2

                    screen.blit(scaled_diver_3_img, (unchanged_diver_3_x, diver_3_y))



def is_jump_successful():
    # Declare global variables
    global diver_1_x, diver_1_y, diver_2_x, diver_2_y, diver_3_x, diver_3_y
    global ring_x, ring_y, ring_width_pixel
    global score_1, score_2, score_3
    global jump_ready, move_diver_1_ring, move_diver_2_ring, move_diver_3_ring
    if jump_game:
        # Check if diver 1 successfully jumped through the ring
        if abs(diver_1_x - ring_x) <= 40 and abs(diver_1_y - ring_y) <= 40:
            score_1 += 1
            jump_ready = True
            move_diver_1_ring = True
            print("diver1", diver_1_x, "and", diver_1_y)
            print("ring", ring_x, "and", ring_y)
            print("Diver 1 scored!")
            #score_sound_channel.play(sound_player1) 
            play_score_sound(score_sound1)
     
        


        # Check if diver 2 successfully jumped through the ring
        if abs(diver_2_x - ring_x) <= 40 and abs(diver_2_y - ring_y) <= 40:
            score_2 += 1
            jump_ready = True
            move_diver_2_ring = True
            # Verification
            print("diver2", diver_2_x, "and", diver_2_y)
            print("ring", ring_x, "and", ring_y)
            play_score_sound(score_sound1)

        # Check if diver 3 successfully jumped through the ring
        if abs(diver_3_x - ring_x) <= 40 and abs(diver_3_y - ring_y) <= 40:
            score_3 += 1
            jump_ready = True
            move_diver_3_ring = True
            print("diver1", diver_3_x, "and", diver_3_y)
            print("ring", ring_x, "and", ring_y)
            play_score_sound(score_sound1)

def move_together_1():
    # Declare global variables
    global move_diver_1_ring, move_count_1, ring_direction, unchanged_diver_1_x
    global diver_1_x, diver_1_y, width, ring_speed, height, diver_1_height_pixel
    global scaled_diver_1_img, screen, jump_ready

    if move_diver_1_ring:
        move_count_1 += 1
        if ring_direction == 1:
            # 计算出来的
            distance_together_1 = (width - unchanged_diver_1_x) / ring_speed
            if move_count_1 <= distance_together_1:
                diver_1_x_new = unchanged_diver_1_x + move_count_1 * ring_speed
                diver_1_y = ((height - diver_1_height_pixel) // 2)
                screen.blit(scaled_diver_1_img, (diver_1_x_new, diver_1_y))
            else:
                move_diver_1_ring = False
                jump_ready = True
        elif ring_direction == -1:
            distance_together_1 = unchanged_diver_1_x / abs(ring_speed)
            if move_count_1 <= distance_together_1:
                diver_1_x_new = unchanged_diver_1_x + move_count_1 * ring_speed
                diver_1_y = ((height - diver_1_height_pixel) // 2)
                screen.blit(scaled_diver_1_img, (diver_1_x_new, diver_1_y))
            else:
                move_diver_1_ring = False
                jump_ready = True
    
def move_together_2():
    # Declare global variables
    global move_diver_2_ring, move_count_2, ring_direction, unchanged_diver_2_x
    global diver_2_x, diver_2_y, width, ring_speed, height, diver_2_height_pixel
    global scaled_diver_2_img, screen, jump_ready

    if move_diver_2_ring:
        move_count_2 += 1
        if ring_direction == 1:
            # 计算出来的
            distance_together_2 = (width - unchanged_diver_2_x) / ring_speed
            if move_count_2 <= distance_together_2:
                diver_2_x_new = unchanged_diver_2_x + move_count_2 * ring_speed
                diver_2_y = ((height - diver_2_height_pixel) // 2)
                screen.blit(scaled_diver_2_img, (diver_2_x_new, diver_2_y))
            else:
                move_diver_2_ring = False
                jump_ready = True
        elif ring_direction == -1:
            distance_together_2 = unchanged_diver_2_x / abs(ring_speed)
            if move_count_2 <= distance_together_2:
                diver_2_x_new = unchanged_diver_2_x + move_count_2 * ring_speed
                diver_2_y = ((height - diver_2_height_pixel) // 2)
                screen.blit(scaled_diver_2_img, (diver_2_x_new, diver_2_y))
            else:
                move_diver_2_ring = False
                jump_ready = True

def move_together_3():
    # Declare global variables
    global move_diver_3_ring, move_count_3, ring_direction, unchanged_diver_3_x
    global diver_3_x, diver_3_y, width, ring_speed, height, diver_3_height_pixel
    global scaled_diver_3_img, screen, jump_ready

    if move_diver_3_ring:
        move_count_3 += 1
        if ring_direction == 1:
            # 计算出来的
            distance_together_3 = (width - unchanged_diver_3_x) / ring_speed
            if move_count_3 <= distance_together_3:
                diver_3_x_new = unchanged_diver_3_x + move_count_3 * ring_speed
                diver_3_y = ((height - diver_3_height_pixel) // 2)
                screen.blit(scaled_diver_3_img, (diver_3_x_new, diver_3_y))
            else:
                move_diver_3_ring = False
                jump_ready = True
        elif ring_direction == -1:
            distance_together_3 = unchanged_diver_3_x / abs(ring_speed)
            if move_count_3 <= distance_together_3:
                diver_3_x_new = unchanged_diver_3_x + move_count_3 * ring_speed
                diver_3_y = ((height - diver_3_height_pixel) // 2)
                screen.blit(scaled_diver_3_img, (diver_3_x_new, diver_3_y))
            else:
                move_diver_3_ring = False
                jump_ready = True

def reset_diver_position(diver_x, diver_y, initial_x, jumping):
    if not jumping and jump_ready and diver_y < 170:
        diver_x = initial_x
        diver_y = 170
    return diver_x, diver_y

def render_scores():
    global score_1, score_2, score_3 
    font = pygame.font.Font(None, 15)
    score_text_1 = font.render("Player 1 Score: " + str(score_1), True, (0, 0, 0))
    score_text_2 = font.render("Player 2 Score: " + str(score_2), True, (0, 0, 0))
    score_text_3 = font.render("Player 3 Score: " + str(score_3), True, (0, 0, 0))
    screen.blit(score_text_1, (10, 10))
    screen.blit(score_text_2, (10, 30))
    screen.blit(score_text_3, (10, 50))

def render_buttons():
    global player1_btn, player2_btn, player3_btn
    global player1_btn_pressed, player2_btn_pressed, player3_btn_pressed
    # 更新按钮状态
    if player1_btn_pressed:
        pygame.draw.rect(screen, (0, 0, 255), player1_btn)
    else:
        pygame.draw.rect(screen, (0, 0, 0), player1_btn)

    if player2_btn_pressed:
        pygame.draw.rect(screen, (0, 255, 0), player2_btn)
    else:
        pygame.draw.rect(screen, (0, 0, 0), player2_btn)

    if player3_btn_pressed:
        pygame.draw.rect(screen, (255, 255, 255), player3_btn)
    else:
        pygame.draw.rect(screen, (0, 0, 0), player3_btn)


def show_end():
    # screen.blit(bg_img, (0,0))
    crown_img_path = "crown.png"
    crown_img = pygame.image.load(crown_img_path)
    crown_img = pygame.transform.scale(crown_img, (40, 40))
   
    black_img = pygame.Surface((20, 20))
    black_img.fill((0, 0, 0))

    screen.fill((0, 0, 0))
    font = pygame.font.SysFont("simHei", 20)
    font_color = (255, 255, 255)
    score_data = {'Player 1': score_1, 'Player 2': score_2, 'Player 3': score_3}
    scores = sorted(score_data.items(), key=lambda x: x[1], reverse=True)

    # Render and display text
    fontsurf = font.render(f'{"Name":<10}{"Score":<5}Top', False, font_color)
    screen.blit(fontsurf, (60, 60))
    fontsurf = font.render(f'{scores[0][0]:<10}{scores[0][1]:<5}winner', False, font_color)
    screen.blit(fontsurf, (60, 95))
    fontsurf = font.render(f'{scores[1][0]:<10}{scores[1][1]:<5}{2}', False, font_color)
    screen.blit(fontsurf, (60, 120))
    fontsurf = font.render(f'{scores[2][0]:<10}{scores[2][1]:<5}{3}', False, font_color)
    screen.blit(fontsurf, (60, 145))

    return_btn = create_return_button(screen)
    create_return_button(screen)

    if event.type == pygame.MOUSEBUTTONUP:
                if return_btn.collidepoint(event.pos):
                    #jump_game = False
                    main.into_game()

    # Get the current time in seconds
    current_time = time.time()

    # Blink the crown every second
    if int(current_time) % 2 == 0:
        crown_rect = crown_img.get_rect()
        crown_rect.topright = (screen.get_width() - 270, 85)
        screen.blit(crown_img, crown_rect)
    else:
        # Display the black image during the other second
        crown_rect = black_img.get_rect()
        crown_rect.topright = (screen.get_width() - 270, 85)
        screen.blit(black_img, crown_rect)

    pygame.display.update()



while True:
    return_btn = create_return_button(screen)
    #time.sleep(0.01)
    for event in pygame.event.get ():
        if event.type == pygame.QUIT:
            pygame.quit ()
            sys.exit ()

        if game_started:
            jump_game = True
            handle_mouse_events (event)
            handle_keyboard_events (event)

            # to do
            # handle_button_events(event)
            if event.type == pygame.MOUSEBUTTONUP:
                if return_btn.collidepoint(event.pos):
                    jump_game = False
                    main.into_game()

        if not game_started:
            handle_start_screen_events (event)
    # 判断分数
    if score_1 >= end_score or score_2 >= end_score or score_3 >= end_score:
        game_started = False
        # 显示结束画面
        show_end()
        continue
    if game_started:
        jump_game = True

    draw_3_buttons()
    # 在游戏界面中绘制按钮
    draw_divers_bg()
    ring_control()
    jumping()

    if jump_game:
        tranform_diver1()
        transform_diver2()
        transform_diver3()
        
        is_jump_successful() #判断
    # Continue playing background music
    #if not background_channel.get_busy():
        #play_background_music()
        
    move_together_1()
    move_together_2()
    move_together_3()

    #复位
    diver_1_x, diver_1_y = reset_diver_position(diver_1_x, diver_1_y, 60, jumping_1)
    diver_2_x, diver_2_y = reset_diver_position(diver_2_x, diver_2_y, 135, jumping_2)
    diver_3_x, diver_3_y = reset_diver_position(diver_3_x, diver_3_y, 210, jumping_3)

    render_scores()

    # 更新按钮状态
    render_buttons()

    create_return_button(screen)

    pygame.display.update()

    clock.tick(60)
