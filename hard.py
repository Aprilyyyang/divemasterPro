import pygame
import sys
import pygame.transform
import random
import time
import RPi.GPIO as GPIO
import os

import main

#player1_pin = 26
player1_pin = 23
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

# 初始化
pygame.init ()

width = 320  # 1000
height = 240  # 700

screen = pygame.display.set_mode ((width, height))

score_sound1 = r'score.mp3'

#the score that the game ends!!!!! 
end_score = 10

# 记录一下像素，方便以后修改
ring_width_pixel = ring_height_pixel = 80

diver_1_width_pixel = diver_1_height_pixel = diver_2_width_pixel = diver_2_height_pixel = diver_3_width_pixel = diver_3_height_pixel = 50

pool_width_pixel = 320
pool_height_pixel = 240

# 加载资源
bg_img = pygame.image.load ('pool.png')
ring_img = pygame.image.load ('ring.png')
diver_1_img = pygame.image.load ('diver_1.png')
diver_2_img = pygame.image.load ('diver_2.png')
diver_3_img = pygame.image.load ('diver_3.png')
bomb_img = pygame.image.load ('bomb.png')
crocodile_img = pygame.image.load ('crocodile.png')
font = pygame.font.Font (None, 15)


bombs = []  # 存储所有炸弹的列表
last_velocity_threshold = 2.08  # 用于记录上一个速度阈值

warning_msg = ""  # 存储警告信息的变量
warning_duration = 120  # 警告信息显示持续的帧数
warning_counter = 0  # 警告信息计时器

warning_msg_crocodile = ""  # 存储警告信息的变量
warning_duration_crocodile = 120  # 警告信息显示持续的帧数
warning_counter_crocodile = 0  # 警告信息计时器

crocodiles = []  # 存储所有小鳄鱼
last_velocity_threshold_cro = 2.20  # 用于记录上一个速度阈值

ring_x = 0
ring_y = (height - ring_height_pixel) // 2 - 20  # 居中

ring_speed = 2
ring_direction = 1  # 控制不一样的方向的

# 新加的功能
ring_velocity_x = 2  # Horizontal velocity
ring_velocity_y = 1  # Vertical velocity

diver_1_x = 60
diver_1_y = 170
# diver_2_x = 450
diver_2_x = 135
diver_2_y = 170
diver_3_x = 210
diver_3_y = 170
score_1 = 0
score_2 = 0
score_3 = 0
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

# 添加两个按钮
player2_btn = pygame.Rect (135, 222, 50, 15)  # 用于控制 diver_2 的按钮 diver1是中间的那个
# player1_btn = pygame.Rect(210, 650, 80, 50)  # 用于控制 diver_1 的按钮
player1_btn = pygame.Rect (60, 222, 50, 15)  # 手动算出

player3_btn = pygame.Rect (210, 222, 50, 15)  # 用于控制 diver_3 的按钮
pygame.draw.rect (screen, (0, 0, 255), player1_btn)  # 设置颜色为蓝色 (0, 0, 255)
pygame.draw.rect (screen, (0, 255, 0), player2_btn)  # 设置颜色为绿色 (0, 255, 0)
pygame.draw.rect (screen, (255, 255, 255), player3_btn)  # 设置颜色为白色
player1_font = pygame.font.Font (None, 24)
player2_font = pygame.font.Font (None, 24)
player3_font = pygame.font.Font (None, 24)
player1_text = player1_font.render ("Player 1 Go", True, (255, 255, 255))
player2_text = player2_font.render ("Player 2 Go", True, (255, 255, 255))
player3_text = player2_font.render ("Player 3 Go", True, (255, 255, 255))
player1_text_rect = player1_text.get_rect (center=player1_btn.center)
player2_text_rect = player2_text.get_rect (center=player2_btn.center)
player3_text_rect = player3_text.get_rect (center=player3_btn.center)

# 主循环
clock = pygame.time.Clock ()

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
def play_score_sound(sound):
    #sound_player1 = pygame.mixer.Sound('jump.wav')
    pygame.mixer.music.load(sound)
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
        if player1_btn.collidepoint (event.pos):
            player1_pressed ()
        if player2_btn.collidepoint (event.pos):
            player2_pressed ()
        if player3_btn.collidepoint (event.pos):
            player3_pressed ()


def handle_keyboard_events(event):
    # ...（之前的处理逻辑）
    global jumping_1, jumping_2, jumping_3, move_diver_1_ring, move_diver_2_ring, move_diver_3_ring
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_w:
            player1_pressed ()
        if event.key == pygame.K_SPACE:
            player2_pressed ()
        if event.key == pygame.K_p:
            player3_pressed ()


""" # def handle_buttons_events(event):
def handle_buttons_events():
    global jumping_1, jumping_2, jumping_3, move_diver_1_ring, move_diver_2_ring, move_diver_3_ring, player1_pin, player2_pin, player3_pin
    if (not GPIO.input(player1_pin)):
        print(f"button {player1_pin} pressed.. player 1 jump")
        player1_pressed()
    if (not GPIO.input(player2_pin)):
        print(f"button {player2_pin} pressed.. player 2 jump")
        player2_pressed()   
    if (not GPIO.input(player3_pin)):
        print(f"button {player3_pin} pressed.. player 3 jump")
        player3_pressed() """

# 处理开始屏幕中的事件
def handle_start_screen_events(event):
    try:
        global game_started
        global game_start_btn
        if event.type == pygame.MOUSEBUTTONUP:
            if game_start_btn.collidepoint (event.pos):
                game_started = True
    except:
        pass


def draw_3_buttons():  # 在游戏中画按钮
    player2_btn = pygame.Rect (135, 222, 50, 15)  # 用于控制 diver_2 的按钮 diver1是中间的那个
    # player1_btn = pygame.Rect(210, 650, 80, 50)  # 用于控制 diver_1 的按钮
    player1_btn = pygame.Rect (60, 222, 50, 15)  # 手动算出
    player3_btn = pygame.Rect (210, 222, 50, 15)  # 用于控制 diver_3 的按钮
    pygame.draw.rect (screen, (0, 0, 255), player1_btn)  # 设置颜色为蓝色 (0, 0, 255)
    pygame.draw.rect (screen, (0, 255, 0), player2_btn)  # 设置颜色为绿色 (0, 255, 0)
    pygame.draw.rect (screen, (255, 255, 255), player3_btn)  # 设置颜色为白色


def draw_divers_bg():
    screen.blit (diver_1_img, (diver_1_x, diver_1_y))
    screen.blit (diver_2_img, (diver_2_x, diver_2_y))
    screen.blit (diver_3_img, (diver_3_x, diver_3_y))
    screen.blit (bg_img, (0, 0))


def ring_control():
    global jump_ready, move_count_1, move_count_2, ring_x, ring_speed, ring_direction, ring_velocity_x, ring_velocity_y, ring_y
    ring_x += ring_velocity_x
    ring_y += ring_velocity_y

    if ring_x <= 0 or ring_x + ring_width_pixel >= width:
        # ring_x = 0
        # ring_direction *= -1
        ring_velocity_x *= -1
        # ring_speed += 1 #为了增加游戏难度！每一轮都加速
        # ring_speed = ring_speed * ring_direction
        # 有效解决了问题！
        # ring_speed = (abs(ring_speed) + 0.1) * ring_direction
        if ring_velocity_x >= 0:
            ring_velocity_x = ring_velocity_x + 0.005
        elif ring_velocity_x < 0:
            ring_velocity_x = ring_velocity_x - 0.005

        jump_ready = True

    if ring_y <= 0 or ring_y + ring_height_pixel >= 170:
        ring_velocity_y *= -1  # Reverse vertical
        if ring_velocity_y >= 0:
            ring_velocity_y = ring_velocity_y + 0.01
        elif ring_velocity_x < 0:
            ring_velocity_y = ring_velocity_y - 0.01

        jump_ready = True
        move_count_1 = 0
        move_count_2 = 0

    screen.blit (ring_img, (ring_x, ring_y))


def manage_bombs():
    global bombs, last_velocity_threshold
    threshold_increase = 0.3  # 每增加0.3速度增加一个炸弹

    # 当速度达到新的阈值时添加炸弹
    if ring_velocity_x > last_velocity_threshold:
        last_velocity_threshold += threshold_increase
        add_new_bomb()

    # 更新和绘制所有活跃的炸弹
    for bomb in bombs:
        if bomb['active']:
            update_bomb(bomb)
            draw_bomb(bomb)

def add_new_bomb():
    global warning_msg, warning_counter, warning_duration
    # 添加一个新的炸弹
    warning_msg = "Caution! Here comes the bomb!"
    warning_counter = warning_duration

    new_bomb = {
        'x': random.randint(0, width),
        'y': random.randint(0, 145),
        'velocity_x': random.choice([-1, 1]),
        'velocity_y': random.choice([-1, 1]),
        'active': True
    }
    bombs.append(new_bomb)

def update_bomb(bomb):
    global bomb_x, bomb_y, bomb_velocity_x, bomb_velocity_y, bomb_active
    global score_1, score_2, score_3

    # 更新炸弹的位置
    bomb['x'] += bomb['velocity_x']
    bomb['y'] += bomb['velocity_y']

    # 边界回弹
    if bomb['x'] <= 0 or bomb['x'] + bomb_img.get_width() >= width:
        #bomb['velocity_x'] *= -1
        bomb['velocity_x'] = -bomb['velocity_x'] + random.uniform(-1, 1)
    if bomb['y'] <= 0 or bomb['y'] + bomb_img.get_height() >= 150:
        #bomb['velocity_y'] *= -1
        bomb['velocity_y'] = -bomb['velocity_y'] + random.uniform(-1, 1)

    # 检测与玩家的碰撞
    if bomb['x'] < diver_1_x + diver_1_width_pixel and bomb['x'] + bomb_img.get_width() > diver_1_x and bomb['y'] < diver_1_y + diver_1_height_pixel and bomb['y']  + bomb_img.get_height() > diver_1_y:
            score_1 -= 1  # 玩家 1 分数减一
            bomb['active'] = False
            print(" 1 you hit the bomb!")
    elif bomb['x'] < diver_2_x + diver_2_width_pixel and bomb['x'] + bomb_img.get_width() > diver_2_x and bomb['y'] < diver_2_y + diver_2_height_pixel and bomb['y']  + bomb_img.get_height() > diver_2_y:
            score_2 -= 1  # 玩家 2 分数减一
            print(" 2 you hit the bomb!")
            bomb['active'] = False
    elif bomb['x'] < diver_3_x + diver_3_width_pixel and bomb['x'] + bomb_img.get_width() > diver_3_x and bomb['y']  < diver_3_y + diver_3_height_pixel and bomb['y'] + bomb_img.get_height() > diver_3_y:
            score_3 -= 1  # 玩家 3 分数减一
            bomb_active = False
            print(" 3 you hit the bomb!")
            bomb['active'] = False  # 炸弹被碰到，消失

            
    # 更新炸弹的位置和检查边界回弹
    # ...（更新逻辑）

    # 碰撞检测
    # ...（碰撞检测逻辑）

def draw_bomb(bomb):
    if bomb['active']:
        screen.blit(bomb_img, (bomb['x'], bomb['y']))

#鳄鱼
def manage_crocodile():
    global crocodile, last_velocity_threshold_cro
    threshold_increase_cro = 0.3  # 每增加0.3速度增加一个小鳄鱼

    # 当速度达到新的阈值时添加炸弹
    if ring_velocity_x > last_velocity_threshold_cro:
        last_velocity_threshold_cro += threshold_increase_cro
        add_new_crocodile()

    # 更新和绘制所有活跃的炸弹
    for crocodile in crocodiles:
        if crocodile['active']:
            update_crocodile(crocodile)
            draw_crocodile(crocodile)

def add_new_crocodile():
    global warning_msg_crocodile, warning_counter_crocodile, warning_duration_crocodile
   
    warning_msg_crocodile = "Caution! Here comes the crocodile!"
    warning_counter_crocodile = warning_duration_crocodile
     # 添加一个新的炸弹
    new_crocodile = {
        'x': random.randint(0, width),
        'y': random.randint(0, 150),
        'velocity_x': random.choice([-1, 1]),
        'velocity_y': random.choice([-1, 1]),
        'active': True
    }
    crocodiles.append(new_crocodile)

def update_crocodile(crocodile):
    global bomb_x, bomb_y, bomb_velocity_x, bomb_velocity_y, bomb_active
    global score_1, score_2, score_3

    # 更新炸弹的位置
    crocodile['x'] += crocodile['velocity_x']
    crocodile['y'] += crocodile['velocity_y']

    # 边界回弹
    if crocodile['x'] <= 0 or crocodile['x'] + bomb_img.get_width() >= width:
        #bomb['velocity_x'] *= -1
        crocodile['velocity_x'] = -crocodile['velocity_x'] + random.uniform(-0.1, 0.1)
    if crocodile['y'] <= 0 or crocodile['y'] + crocodile_img.get_height() >= 150:
        #bomb['velocity_y'] *= -1
        crocodile['velocity_y'] = -crocodile['velocity_y'] + random.uniform(-0.1, 0.1)

    # 检测与玩家的碰撞
    if crocodile['x'] < diver_1_x + diver_1_width_pixel and crocodile['x'] + crocodile_img.get_width() > diver_1_x and crocodile['y'] < diver_1_y + diver_1_height_pixel and crocodile['y']  + crocodile_img.get_height() > diver_1_y:
            score_1 -= 1  # 玩家 1 分数减一
            crocodile['active'] = False
            print(" 1 you hit the crocodile!")
    elif crocodile['x'] < diver_2_x + diver_2_width_pixel and crocodile['x'] + crocodile_img.get_width() > diver_2_x and crocodile['y'] < diver_2_y + diver_2_height_pixel and crocodile['y']  + crocodile_img.get_height() > diver_2_y:
            score_2 -= 1  # 玩家 2 分数减一
            print(" 2 you hit the crocodile!")
            crocodile['active'] = False
    elif crocodile['x'] < diver_3_x + diver_3_width_pixel and crocodile['x'] + crocodile_img.get_width() > diver_3_x and crocodile['y'] < diver_3_y + diver_3_height_pixel and crocodile['y'] + crocodile_img.get_height() > diver_3_y:
            score_3 -= 1  # 玩家 3 分数减一
            print(" 3 you hit the crocodile!")
            crocodile['active'] = False  

            
    # 更新炸弹的位置和检查边界回弹
    # ...（更新逻辑）

    # 碰撞检测
    # ...（碰撞检测逻辑）

def draw_crocodile(crocodile):
    if crocodile['active']:
        screen.blit(crocodile_img, (crocodile['x'], crocodile['y']))




def is_jumping():  # diver jumps的过程
    global jumping_1, diver_1_y, jumping_2, diver_2_y, jumping_3, diver_3_y, height, diver_1_height_pixel, diver_2_height_pixel, diver_3_height_pixel
    if jumping_1:
        # diver_1_y -= 8
        diver_1_y -= 3
        # if diver_1_y < ((height - diver_1_height_pixel) // 2 - 20):
        if diver_1_y < ring_y + 40:
            jumping_1 = False

    if jumping_2:
        diver_2_y -= 3
        if diver_2_y < ring_y + 40:
            jumping_2 = False

    if jumping_3:
        diver_3_y -= 3
        if diver_3_y < ring_y + 40:
            jumping_3 = False


def is_jump_successful():
    # Declare global variables
    global diver_1_x, diver_1_y, diver_2_x, diver_2_y, diver_3_x, diver_3_y
    global ring_x, ring_y, ring_width_pixel
    global score_1, score_2, score_3
    global jump_ready, move_diver_1_ring, move_diver_2_ring, move_diver_3_ring
    if jump_game:
        # Check if diver 1 successfully jumped through the ring
        if abs (diver_1_x - ring_x) <= 40 and abs (diver_1_y - ring_y) <= 40:
            score_1 += 1
            jump_ready = True
            move_diver_1_ring = True
            print ("diver1", diver_1_x, "and", diver_1_y)
            print ("ring", ring_x, "and", ring_y)
            play_score_sound(score_sound1)

        # Check if diver 2 successfully jumped through the ring
        if abs (diver_2_x - ring_x) <= 40 and abs (diver_2_y - ring_y) <= 40:
            score_2 += 1
            jump_ready = True
            move_diver_2_ring = True
            # Verification
            print ("diver2", diver_2_x, "and", diver_2_y)
            print ("ring", ring_x, "and", ring_y)
            play_score_sound(score_sound1)

        # Check if diver 3 successfully jumped through the ring
        if abs (diver_3_x - ring_x) <= 40 and abs (diver_3_y - ring_y) <= 40:
            score_3 += 1
            jump_ready = True
            move_diver_3_ring = True
            print ("diver1", diver_3_x, "and", diver_3_y)
            print ("ring", ring_x, "and", ring_y)
            play_score_sound(score_sound1)


def move_together_1():
    # Declare global variables
    global move_diver_1_ring, move_count_1, ring_direction, unchanged_diver_1_x
    global diver_1_x, diver_1_y, width, ring_speed, height, diver_1_height_pixel
    global scaled_diver_1_img, screen, jump_ready

    if move_diver_1_ring:
        move_count_1 += 1

        # 计算出来的
        # distance_together_1 = (width - unchanged_diver_1_x) / ring_speed
        distance_together_1 = 12
        if move_count_1 <= distance_together_1:
            # diver_1_x_new = unchanged_diver_1_x + move_count_1 * ring_speed
            diver_1_x_new = unchanged_diver_1_x + move_count_1 * ring_velocity_x
            # diver_1_x_new = ring_x + 40 - scaled_diver_1_img.get_width() // 2
            # diver_1_y = ((height - diver_1_height_pixel) // 2)
            diver_1_y = ring_y + 40
            screen.blit (scaled_diver_1_img, (diver_1_x_new, diver_1_y))
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

        if move_count_2 <= 12:
            # diver_2_x_new = ring_x + 40 - scaled_diver_2_img.get_width() // 2
            diver_2_x_new = unchanged_diver_2_x + move_count_2 * ring_velocity_x

            diver_2_y = ring_y + 40
            screen.blit (scaled_diver_2_img, (diver_2_x_new, diver_2_y))
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

        # 计算出来的
        # distance_together_1 = (width - unchanged_diver_1_x) / ring_speed
        if move_count_3 <= 10:
            diver_3_x_new = unchanged_diver_3_x + move_count_3 * ring_velocity_x
            diver_3_y = ring_y + 40
            screen.blit (scaled_diver_3_img, (diver_3_x_new, diver_3_y))
        else:
            move_diver_3_ring = False
            jump_ready = True


def reset_diver_position(diver_x, diver_y, initial_x, jumping):
    if not jumping and jump_ready and diver_y < 170:
        diver_x = initial_x
        diver_y = 170
    return diver_x, diver_y


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

    for event in pygame.event.get ():
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
    
    # time.sleep(0.01)
    if game_started:
        jump_game = True
        #handle_buttons_events()
        if (not GPIO.input(player1_pin)):
            print(f"button {player1_pin} pressed.. player 1 jump")
            player1_pressed()
        if (not GPIO.input(player2_pin)):
            print(f"button {player2_pin} pressed.. player 2 jump")
            player2_pressed()   
        if (not GPIO.input(player3_pin)):
            print(f"button {player3_pin} pressed.. player 3 jump")
            player3_pressed() 

    for event in pygame.event.get ():
        if event.type == pygame.QUIT:
            pygame.quit ()
            sys.exit ()

        if game_started:
            jump_game = True
            handle_mouse_events (event)
            handle_keyboard_events (event)

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
        show_end ()
        continue

    draw_3_buttons ()
    # 在游戏界面中绘制按钮
    draw_divers_bg ()

    ring_control ()

    is_jumping ()

    if jump_game:
        if not move_diver_1_ring:
            # 为了平滑跳动
            diver_1_center_x = diver_1_x + diver_1_width_pixel // 2

            # if ((height - diver_1_height_pixel) // 2) <= diver_1_y <= 580:
            if (ring_y + 40) <= diver_1_y <= 170:
                # 计算缩放比例，范围从1.0到0.25
                # scale_factor = 1.0 - (diver_1_y - 580) / (((height - diver_2_height_pixel) // 2) - 580) * 0.75
                scale_factor = 1.0 - (diver_1_y - 170) / (ring_y + 40 - 170) * 0.75

                # 缩小图像以实现平滑跳动
                scaled_diver_1_img = pygame.transform.scale (diver_1_img, (
                int (diver_1_width_pixel * scale_factor), int (diver_1_height_pixel * scale_factor)))
                # 为了中心不变！！！！！这很困难的 还好我算出来了
                unchanged_diver_1_x = diver_1_center_x - scaled_diver_1_img.get_width () // 2

                # screen.blit(scaled_diver_1_img, (diver_1_x, diver_1_y))
                screen.blit (scaled_diver_1_img, (unchanged_diver_1_x, diver_1_y))
            # elif diver_1_y == ((height - diver_2_height_pixel) // 2 ):
            # 缩小为四分之一
            # scaled_diver_1_img = pygame.transform.scale(diver_1_img, (diver_1_width_pixel // 4, diver_2_height_pixel // 4))
            # screen.blit(scaled_diver_1_img, (diver_1_x, diver_1_y))
            # else:
            # screen.blit(diver_1_img, (diver_1_x, diver_1_y))

        if not move_diver_2_ring:
            # screen.blit(diver_2_img, (diver_2_x, diver_2_y))

            diver_2_center_x = diver_2_x + diver_2_width_pixel // 2

            if (ring_y + 40) <= diver_2_y <= 170:
                # 计算缩放比例，范围从1.0到0.25
                scale_factor = 1.0 - (diver_2_y - 170) / (ring_y + 40 - 170) * 0.75

                # 缩小图像以实现平滑跳动
                scaled_diver_2_img = pygame.transform.scale (diver_2_img, (
                int (diver_2_width_pixel * scale_factor), int (diver_2_height_pixel * scale_factor)))
                # 为了中心不变！！！！！
                unchanged_diver_2_x = diver_2_center_x - scaled_diver_2_img.get_width () // 2

                screen.blit (scaled_diver_2_img, (unchanged_diver_2_x, diver_2_y))
        if not move_diver_3_ring:
            # screen.blit(diver_3_img, (diver_3_x, diver_3_y))
            diver_3_center_x = diver_3_x + diver_3_width_pixel // 2

            if (ring_y + 40) <= diver_3_y <= 170:
                # 计算缩放比例，范围从1.0到0.25
                scale_factor = 1.0 - (diver_3_y - 170) / (ring_y + 40 - 170) * 0.75

                # 缩小图像以实现平滑跳动
                scaled_diver_3_img = pygame.transform.scale (diver_3_img, (
                int (diver_3_width_pixel * scale_factor), int (diver_3_height_pixel * scale_factor)))
                # 为了中心不变！！！！！
                unchanged_diver_3_x = diver_3_center_x - scaled_diver_3_img.get_width () // 2

                screen.blit (scaled_diver_3_img, (unchanged_diver_3_x, diver_3_y))

        # transform()

        is_jump_successful ()  # 判断

    move_together_1 ()
    move_together_2 ()
    move_together_3 ()

    #bomb_control()
     # 检查是否需要显示警告信息
    if warning_counter > 0:
        warning_counter -= 1  # 更新警告计时器
        warning_font = pygame.font.Font(None, 20)
        warning_text = warning_font.render(warning_msg, True, (255, 0, 0))  # 创建警告文本
        screen.blit(warning_text, (width // 2 - warning_text.get_width() // 2 + 10, 70))  # 显示警告信息

    manage_bombs()

    if warning_counter_crocodile > 0:
        warning_counter_crocodile -= 1  # 更新警告计时器
        warning_font = pygame.font.Font(None, 20)
        warning_text_crocodile = warning_font.render(warning_msg_crocodile, True, (255, 0, 0))  # 创建警告文本
        screen.blit(warning_text_crocodile, (width // 2 - warning_text_crocodile.get_width() // 2 + 10, 80))  # 显示警告信息

    manage_crocodile()

    # 复位
    diver_1_x, diver_1_y = reset_diver_position (diver_1_x, diver_1_y, 60, jumping_1)
    diver_2_x, diver_2_y = reset_diver_position (diver_2_x, diver_2_y, 135, jumping_2)
    diver_3_x, diver_3_y = reset_diver_position (diver_3_x, diver_3_y, 210, jumping_3)

    font = pygame.font.Font (None, 15)
    score_text_1 = font.render ("Player 1 Score: " + str (score_1), True, (0, 0, 0))
    score_text_2 = font.render ("Player 2 Score: " + str (score_2), True, (0, 0, 0))
    score_text_3 = font.render ("Player 3 Score: " + str (score_3), True, (0, 0, 0))
    screen.blit (score_text_1, (10, 10))
    screen.blit (score_text_2, (10, 30))
    screen.blit (score_text_3, (10, 50))

    speed_text = font.render ("Ring Speed: {:.2f}".format (abs (ring_velocity_x)), True, (200, 150, 200))
    screen.blit (speed_text, (width - speed_text.get_width () - 10, 10))

    
    create_return_button(screen)

    # 更新按钮状态
    if player1_btn_pressed:
        pygame.draw.rect (screen, (0, 0, 255), player1_btn)
    else:
        pygame.draw.rect (screen, (0, 0, 0), player1_btn)

    if player2_btn_pressed:
        pygame.draw.rect (screen, (0, 255, 0), player2_btn)
    else:
        pygame.draw.rect (screen, (0, 0, 0), player2_btn)

    if player3_btn_pressed:
        pygame.draw.rect (screen, (255, 255, 255), player3_btn)
    else:
        pygame.draw.rect (screen, (0, 0, 0), player3_btn)

    pygame.display.update ()
    clock.tick (60)
