import pygame
from pygame import mixer
import os
import random
import csv
import math

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('ShootStrike')

#set framerate
clock = pygame.time.Clock()
FPS = 60


#define game variables
GRAVITY = 0.7
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES =21
MAX_LEVELS = 10
shake = 0
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
game_won = False
show_howto = False
menu_drift = 0
BANNER_FRAMES = 150
banner_timer = 0
end_anim  =0

#define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

#define font
font = pygame.font.Font('font/MotionControl-Bold.otf', 30)
title_font = pygame.font.Font('font/PixelPurl.ttf', 60)
menu_title_font = pygame.font.Font('font/PixelPurl.ttf', 80)
#load music and sounds
pygame.mixer.music.load('audio/game_musicc.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.5)


#load images
#button images
# start_img = pygame.image.load('img/start_btn.png').convert_alpha()
# exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
# restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

#background
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)




#bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
#grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
#pickup boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

#explosion
explosion_imgs = [pygame.image.load(f'img/explosion/exp{n}.png').convert_alpha() for n in range(1, 6)]

#define colours
BG = (144, 201, 120)
RED = (255,0,0)
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0 , 255, 0)
PINK = (235, 65, 54)
# draw text
def draw_text(text, font,text_col, x,y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

#define controls
CONTROLS = [('A / D', 'Move Left / right'), ('W', 'Jump'), ('SPACE', 'Shoot'), ('Q', 'Throw a grenade'), ('ESC', 'Quit')]

def draw_howto():
    panel_rect = pygame.Rect(60, 50, SCREEN_WIDTH - 120 , 470)
    panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (15, 25, 20, 215), panel.get_rect(), border_radius=16)
    screen.blit(panel, panel_rect)
    pygame.draw.rect(screen, WHITE, panel_rect, 3, border_radius=16)

    title = title_font.render('HOW TO PLAY', True,WHITE)
    screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH //2, y=70))

    y = 150
    for key, action in CONTROLS:
        chip = pygame.Rect(110, y, 120, 36)
        pygame.draw.rect(screen, (70, 110 , 75), chip , border_radius=8)
        label = font.render(key, True, WHITE)
        screen.blit(label, label.get_rect(center=chip.center))
        draw_text(action, font, WHITE, 255, y + 6)
        y += 42

    draw_text('PICKUPS', font, (255, 220, 90), 110, y + 10)
    x = 110
    for icon , text in ((health_box_img, 'Health + 25'), (ammo_box_img, 'Ammo + 15'), (grenade_box_img, 'Grenades +3')):
        screen.blit(icon, (x,y + 42))
        draw_text(text, font , WHITE, x + icon.get_width() + 8, y + 45)
        x += 210

    draw_text('Water or falling = instant death', font, (255, 120, 110), 110, y + 95)
    draw_text('Your own grenades hurt you aswell', font, (255, 120, 110), 110, y + 123)

#draw title
def draw_title():
    bob = math.sin(pygame.time.get_ticks() / 300) * 8
    shadow = menu_title_font.render('SHOOTSTRIKE', True, BLACK)
    main = menu_title_font.render('SHOOTSTRIKE', True, WHITE)
    cx = SCREEN_WIDTH // 2
    screen.blit(shadow, shadow.get_rect(center=(cx + 4, 140 + bob + 4)))
    screen.blit(main, main.get_rect(center=(cx, 140 + bob)))

def draw_bg(offset):
    screen.fill(BG)
    width = sky_img.get_width()
    layers = [
        (sky_img,      0.5, 0),
        (mountain_img, 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300),
        (pine1_img,    0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150),
        (pine2_img,    0.8, SCREEN_HEIGHT - pine2_img.get_height()),
    ]
    for img, speed, y in layers:
        x = -((offset * speed) % width)
        while x < SCREEN_WIDTH:
            screen.blit(img, (x, y))
            x += width


def draw_level_banner(timer):
    t = BANNER_FRAMES - timer
    if t < 30:
        s = 1 - ( 1 - t / 30) ** 3
    elif t > BANNER_FRAMES - 30:
        s = 1 - ((t - (BANNER_FRAMES - 30)) / 30 ** 2)
    else:
        s = 1
    w, h = 220, 70
    x = SCREEN_WIDTH - (w + 15) * s
    panel = pygame.Surface((w, h) , pygame.SRCALPHA)
    pygame.draw.rect(panel, (15, 25, 20, 215), panel.get_rect(), border_radius=12)
    pygame.draw.rect(panel , (255, 220, 90), panel.get_rect(), 3, border_radius=12)
    label = font.render(f'LEVEL {level}', True, WHITE)
    panel.blit(label , label.get_rect(centerx=w //2, y = 8))
    step = (w - 40) / MAX_LEVELS
    for i in range(MAX_LEVELS):
        col = (255, 220, 90) if i < level else (70, 90 , 75)
        pygame.draw.circle(panel , col, (int(20 + step * (i + 0.5)), 54), 5)
    screen.blit(panel, (x, 15))

#end screen
def draw_end_screen(title, subtitle, accent, progress):
    w, h = 560, 300
    rect = pygame.Rect(0,0, w,h)
    rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    rise = int((1 - progress) * 40)
    panel = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.rect(panel, ( 15,25,20,235), panel.get_rect(), border_radius=18)
    pygame.draw.rect(panel, accent, panel.get_rect(), 4, border_radius=18)
    pygame.draw.line(panel, accent, (60, 120), (w - 60, 120), 2)
    t = menu_title_font.render(title, True, accent)
    s = font.render(subtitle, True, accent)
    panel.blit(t, t.get_rect(centerx=w// 2, y = 40))
    panel.blit(s, s.get_rect(centerx=w //2, y = 140))
    panel.set_alpha(int(255 * progress))
    screen.blit(panel, rect.move(0, rise))

def ignore_held_click(*buttons):
    for b in buttons:
        b.clicked = True


#function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    water_group.empty()
    exit_group.empty()
    decoration_group.empty()
    particle_group.empty()

    #create empty tile list
    world_data = []
    for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)

    return world_data

def load_level(level_num):
    data = reset_level()
    with open (f'level{level_num}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y , tile in enumerate(row):
                data[x][y] = int(tile)
    new_world = World()
    new_player, new_health_bar = new_world.process_data(data)
    return data, new_world, new_player, new_health_bar

class TextButton:
    def __init__(self, x,y,w,h,text, font):
        self.rect = pygame.Rect(x,y,w,h)
        self.text, self.font = text, font
        self.hover = 0.0
        self.clicked = False

    def draw(self, surface):
        over = self.rect.collidepoint(pygame.mouse.get_pos())
        target = 1.0 if over else 0.0
        self.hover += (target - self.hover) * 0.2
        r = self.rect.inflate(int(self.hover * 12), int(self.hover * 6))
        base , lit = (40, 60, 45), (90, 160, 90)
        col = tuple(int(b + (l - b) * self.hover) for b, l in zip(base, lit))
        pygame.draw.rect(surface, col, r, border_radius=12)
        pygame.draw.rect(surface, WHITE, r, 3, border_radius = 12)
        label = self.font.render(self.text, True, WHITE)
        surface.blit(label, label.get_rect(center=r.center))

        action = False
        pressed = pygame.mouse.get_pressed()[0]
        if over and pressed and not self.clicked:
            action = True
            self.clicked = True
        if not pressed:
            self.clicked = False
        return action

    

class Soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,  x,y,scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.alive = True

        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0,0, 150, 20)  
        self.idling = False
        self.idling_counter = 0                                                           


        
        #load all images for players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        
        for animation in animation_types:
        
            temp_list = []
            #count num of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)  
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    def move(self, moving_left,moving_right):
        #reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        #assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -12
            self.jump = False
            self.in_air = True

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y >10:
            self.vel_y = 10
        dy += self.vel_y

        #check for collision
        for tile in  world.obstacle_list:
            #check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #if the ai has hit a wall then  it should turn around now
                if self.char_type =='enemy':
                    self.direction *= -1
                    self.move_counter = 0

            #check follision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy , self.width, self.height):
                #check if jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom


        #check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        #check for collision with exit 
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group , False):
            level_complete = True

        #check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        #check if going off the edge of screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        #update rect postn
        self.rect.x += dx
        self.rect.y += dy

        #update scroll based on player position
        if self.char_type  == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete


    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo >0:
            self.shoot_cooldown = 50
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, self)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

            if not self.idling and random.randint(1, 200) == 1:
                self.idling = True
                self.update_action(0)
                self.idling_counter = 50

            #check if ai is seeing player
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            else:
                if not self.idling:
                    ai_moving_right = (self.direction == 1)
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter = 0
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        self.rect.x += screen_scroll


    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index+= 1
        #if animation has run out , reset back to start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip ,False), self.rect)
        if self.char_type =='enemy' and self.alive and self.health < self.max_health:
            pygame.draw.rect(screen, (60, 20, 20), (self.rect.x, self.rect.y - 10, self.rect.width , 5))
            pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, self.rect.width * self.health / self.max_health, 5))


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        #iterate throughh each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15: #create player
                        player = Soldier('player',x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16: # create enemiy
                        enemy = Soldier('enemy',x * TILE_SIZE , y * TILE_SIZE, 1.65, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17: #create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)    
                    elif tile == 18: #create grenade box
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19: #create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:    # exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar


    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + (TILE_SIZE // 2), y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + (TILE_SIZE // 2), y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll




class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x+ TILE_SIZE //2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
        #scroll
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            spawn_particles(self.rect.centerx, self.rect.centery, (255, 255, 120), 14)
            #check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            #delete the item box
            self.kill()


class HealthBar():
    def __init__(self, x, y , health , max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        self.trail = health

    def draw(self, health):
        self.health = health
        self.trail += (self.health - self.trail) * 0.06
        ratio = self.health / self.max_health
        trail_ratio = self.trail / self.max_health
        color = GREEN if ratio > 0.5 else (255, 165, 0) if ratio > 0.25 else RED
        pygame.draw.rect(screen, BLACK, (self.x - 3, self.y - 3, 156, 26), border_radius=6)
        pygame.draw.rect(screen, (60, 20, 20), (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, (255, 220, 90), (self.x, self.y , 150 * trail_ratio , 20))
        pygame.draw.rect(screen, color, (self.x, self.y, 150 * ratio, 20))


#Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction, owner):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction 
        self.owner = owner


    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
            


        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                spawn_particles(self.rect.centerx, self.rect.centery, (255, 220, 90), 5)
                self.kill()
                return

        #check collision with characters

        if self.owner.char_type == 'enemy':
            if player.alive and pygame.sprite.collide_rect(self, player):
                spawn_particles(self.rect.centerx, self.rect.centery, RED)
                player.health -= 5
                self.kill()
        else:
            for enemy in enemy_group:
                if enemy.alive and pygame.sprite.collide_rect(self, enemy):
                    spawn_particles(self.rect.centerx, self.rect.centery, RED)
                    enemy.health -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        global shake
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dx = self.direction * self.speed
        dy = self.vel_y

        #check for collision with level
        for tile in world.obstacle_list:
            #check collision with walls
            if tile[1].colliderect(self.rect.x + dx , self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            #check for collisoin in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy , self.width , self.height):
                self.speed = 0
                #check if thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        #check collision with walls or sides of screen
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed


        #update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #countdown timer for explosion of grenade
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            shake = 12
            spawn_particles(self.rect.centerx, self.rect.centery, (255, 140, 40), 30)
            spawn_particles(self.rect.centerx, self.rect.centery , (255, 220, 90), 15)
            grenade_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 0.5)
            explosion_group.add(explosion)
            #do damage to anyone that is nearby
            if  player.alive and (abs(self.rect.centerx - player.rect.centerx)< TILE_SIZE * 2 and abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2):
                player.health -= 50
            for enemy in enemy_group:
                if enemy.alive and (abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2):
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.transform.scale(i, (int(i.get_width() * scale), int(i.get_height() * scale)))
                       for i in explosion_imgs]
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0



    def update(self):
        #scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        #update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #if animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0


    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter,0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH //2 + self.fade_counter, 0 , SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0- self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.direction == 2: #vertical screen fade down
            pygame.draw.rect(screen, self.color, (0,0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete

class Particle(pygame.sprite.Sprite):
    def __init__(self, x , y , color):
        super().__init__()
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-3,3), random.uniform(-4, -1))
        self.life = self.max_life = random.randint(15, 30)
        self.color = color
        self.image = pygame.Surface((4,4), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center = (x, y))
        
    def update(self):
        self.vel.y += 0.25
        self.pos += self.vel
        self.pos.x += screen_scroll
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return

        self.image.fill((*self.color, int(255 * self.life / self.max_life)))
        self.rect.center = self.pos

def spawn_particles(x,y, color , count=8):
    for _ in range(count):
        particle_group.add(Particle(x,y,color))



#create screen fade
intro_fade = ScreenFade(1, BLACK, 4)
death_fade= ScreenFade(2, PINK, 4)


#create buttons
# start_button = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150 , start_img, 1)
# exit_button = Button(SCREEN_WIDTH // 2 - 110 , SCREEN_HEIGHT //2  + 50 , exit_img , 1)
# restart_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50 , restart_img , 2)
cx = SCREEN_WIDTH // 2
start_button = TextButton(cx - 130, 250, 260, 60, 'START', font)
howto_button = TextButton(cx - 130, 330, 260, 60, 'HOW TO PLAY', font)
exit_button = TextButton(cx - 130, 410, 260, 60, 'EXIT', font)
back_button = TextButton(cx - 100, 545, 200, 55, 'BACK', font)
retry_button = TextButton(cx - 250, 385, 220, 56, 'RESTART', font)
menu_button = TextButton(cx + 30, 385, 220, 56, 'MENU', font)

#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()


#Create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

#load in level data and create world
with open (f'level{level}_data.csv', newline= '') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player , health_bar = world.process_data(world_data)


run = True

while run:
    clock.tick(FPS)
    if start_game == False:
        menu_drift += 0.8
        draw_bg(menu_drift)
        if show_howto:
            draw_howto()
            if back_button.draw(screen):
                show_howto= False
        else:
            draw_title()
            #draw menu
            #add buttons
            if start_button.draw(screen):
                start_game = True
                start_intro = True
            if howto_button.draw(screen):
                show_howto = True
            if exit_button.draw(screen):
                run = False
    elif game_won:
        menu_drift += 0.8
        draw_bg(menu_drift)
        end_anim = min(end_anim + 0.04 , 1)
        draw_end_screen('MISSION COMPLETE', 'All levels cleared!', (255, 220, 90), end_anim)
        if end_anim >= 1:
            if retry_button.draw(screen):
                end_anim = 0
                game_won = False
                level = 1
                bg_scroll = 0
                start_intro = True
                world_data, world, player, health_bar = load_level(level)
            if menu_button.draw(screen):
                end_anim = 0
                game_won = False
                start_game = False
                level = 1
                bg_scroll = 0
                world_data, world, player, health_bar = load_level(level)
                ignore_held_click(start_button, howto_button, exit_button)
    else:

        draw_bg(bg_scroll)
        #draw world map
        world.draw()

    # show player health
        health_bar.draw(player.health)

        # show ammo
        ammo_text = 'AMMO: '
        ammo_y = 38
        draw_text(ammo_text, font, WHITE, 10, ammo_y)
        ammo_w, ammo_h = font.size(ammo_text)
        bullet_y = ammo_y + (ammo_h - bullet_img.get_height()) // 2
        for x in range(min(player.ammo, 20)):
            screen.blit(bullet_img, (10 + ammo_w + (x * 10), bullet_y))
        if player.ammo > 20:
            draw_text(f'x{player.ammo}', font, WHITE , 10 + ammo_w + 210, ammo_y)

        # show grenades
        grenade_text = 'GRENADES: '
        grenade_y = 65
        draw_text(grenade_text, font, WHITE, 10, grenade_y)
        grenade_w, grenade_h = font.size(grenade_text)
        grenade_icon_y = grenade_y + (grenade_h - grenade_img.get_height()) // 2
        for x in range(player.grenades):
            screen.blit(grenade_img, (10 + grenade_w + (x * 15), grenade_icon_y))


        player.update()
        player.draw()


        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()



        #update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        particle_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        particle_group.draw(screen)

         #show intro
        if start_intro == True:
            if intro_fade.fade_counter == 0:
                banner_timer = BANNER_FRAMES
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0
        if banner_timer > 0:
            draw_level_banner(banner_timer)
            banner_timer -= 1
        #update player actions
        if player.alive:
            #shoot bullets
            if shoot:
                player.shoot()
            #throw grenades
            if grenade and grenade_thrown == False and player.grenades > 0:
                new_grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), player.rect.top, player.direction)
                grenade_group.add(new_grenade)
                #reduce grenades
                player.grenades -= 1
                grenade_thrown = True
                

            if player.in_air:
                player.update_action(2) #2 is jump

            elif moving_left or moving_right:
                player.update_action(1) #1 is for running
            else:
                player.update_action(0) #0 is idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll = max(0, bg_scroll - screen_scroll)            #check if player has completed thelevel
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    world_data, world, player, health_bar = load_level(level)
                else:
                    game_won = True

        else:
            screen_scroll = 0
            if death_fade.fade():
                end_anim = min(end_anim + 0.04, 1)
                draw_end_screen('YOU DIED', f'level {level} of {MAX_LEVELS}', (255, 110, 100), end_anim)
                if end_anim >= 1:
                    if retry_button.draw(screen):
                        end_anim = 0
                        death_fade.fade_counter = 0
                        start_intro = True
                        bg_scroll = 0
                        world_data, world, player, health_bar = load_level(level)
                    if menu_button.draw(screen):
                        end_anim = 0
                        death_fade.fade_counter = 0
                        start_game = False
                        bg_scroll = 0
                        world_data, world, player, health_bar = load_level(level)
                        ignore_held_click(start_button, howto_button, exit_button)





    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key ==pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_m:
                muted = not muted
                pygame.mixer.music.set_volume(0 if muted else 0.3)
            if event.key == pygame.K_q:
                grenade = True
            if event.key ==pygame.K_w and player.alive and not player.in_air:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                if not start_game and show_howto:
                    show_howto = False
                else:
                    run = False


        #keyboard button release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False
    if shake > 0:
        offset = (random.randint(-shake , shake), (random.randint(-shake, shake)))
        frame = screen.copy()
        screen.fill(BLACK)
        screen.blit(frame, offset)
        shake -= 1
    pygame.display.update()

pygame.quit()