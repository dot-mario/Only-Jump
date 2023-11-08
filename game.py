import pygame
import random

BASE_IMG_PATH = 'data/images/player/'
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 1000
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_HEIGHT = -10
DASH_SPEED = 15

GAME_SPEED = 1
GAME_SCORE = 0

SOUND_VOLUME = 0.3

def load_sprites(path, size=(48, 48)):
    sprite_sheet = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    frame_len = sprite_sheet.get_width() // size[0]
    frames = [sprite_sheet.subsurface(pygame.Rect(i * size[0], 0, size[0], size[1])) for i in range(frame_len)]
    return frames

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img
def load_image_dark(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    return img

def play_sound(sound):
    hop = pygame.mixer.Sound(sound)
    pygame.mixer.Sound.play(hop).set_volume(SOUND_VOLUME)

def play_rand_sound(sounds):
    filename = random.choice(sounds)
    hop = pygame.mixer.Sound(filename)
    pygame.mixer.Sound.play(hop).set_volume(SOUND_VOLUME)
    
# Game setup
pygame.init()
pygame.display.set_caption('Only Jump!')
pygame.display.set_icon(pygame.image.load('data/images/player/Question_Block_NSMB.png'))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
game_over = False
game_restart = False

death_sounds =[
    pygame.mixer.Sound('data/sounds/owowowow.wav'),
    pygame.mixer.Sound('data/sounds/owowowow2.wav'),
]
block_images = [
    load_image("Brick_Block.png"),
    load_image("Brick_Block.png"),
    load_image("Brick_Block.png"),
    load_image("Brick_Block.png"),
    load_image("Question_Block_NSMB.png")
]
cloud_images = [
    load_image("cloud_1.png"),
    load_image("cloud_2.png")
]
game_over_image = load_image_dark("game_over.png")

pygame.mixer.Sound.play(pygame.mixer.Sound('data/sounds/Walking the Plains.mp3'), loops=-1).set_volume(SOUND_VOLUME)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animations = {
            'idle': load_sprites('idle.png'),
            'run': load_sprites('run.png'),
            'jump': load_sprites('jump.png'),
            'wall_slide': load_sprites('wall_slide.png'),
            'air_spin': load_sprites('air_spin.png'),
            'dash': load_sprites('air_spin.png'),
        }
        self.jump_sound = [
            pygame.mixer.Sound('data/sounds/ya.wav'),
            pygame.mixer.Sound('data/sounds/yo.wav'),
            pygame.mixer.Sound('data/sounds/hoo.wav'),
            pygame.mixer.Sound('data/sounds/hoo2.wav'),
        ]
        self.dash_sound = pygame.mixer.Sound('data/sounds/whoohoo2.wav')
        
        self.action = 'idle'
        self.frame_index = 0
        self.image = self.animations[self.action][self.frame_index]
        
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.collideRect = pygame.rect.Rect((0, 0), (30, 41))
        
        self.velocity = pygame.Vector2(0, 0)
        self.direction = 1  # 1 right, -1 left
        self.on_ground = False
        self.double_jump = False
        
        self.on_wall = False
        self.is_jumping = False
        self.is_running = False
        self.is_dashing = False
        self.dash_speed = DASH_SPEED
        self.dash_duration = 200 
        self.last_dash = pygame.time.get_ticks()
        self.dash_cooldown = 1000
        
        self.now_interact_platform = None
        self.is_riding_platform = False
        
        self.is_dead = False

    def apply_gravity(self):
        if not self.on_ground:
            self.velocity.y += GRAVITY
    
    def dash(self):
        now = pygame.time.get_ticks()
        if now - self.last_dash > self.dash_cooldown and not self.is_dashing:
            self.is_dashing = True
            self.last_dash = now
            self.velocity.x = self.dash_speed * self.direction
            self.frame_index = 0
            self.action = 'dash'
            play_sound(self.dash_sound)

    def jump(self):
        if self.is_dashing:
            return
        if self.on_ground:
            self.velocity.y = JUMP_HEIGHT
            self.on_ground = False
            self.action = 'jump'
            self.frame_index = 0
            self.is_riding_platform = False
            play_rand_sound(self.jump_sound)
        elif not self.double_jump:
            self.velocity.y = JUMP_HEIGHT
            self.double_jump = True
            self.action = 'air_spin'
            self.frame_index = 0
            play_rand_sound(self.jump_sound)

    def move(self, dx):
        if self.is_dashing:
            return
        self.is_running = True
        self.rect.x += dx * PLAYER_SPEED
        self.direction = 1 if dx > 0 else -1

    def update(self):
        if game_over:
            if not self.is_dead:
                self.velocity.x = 2
                self.velocity.y = -18
                self.is_dead = True
            self.action = 'air_spin'
            self.velocity.y += GRAVITY
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y
            self.frame_index += 0.25
            if self.frame_index >= len(self.animations[self.action]):
                self.frame_index = 0
            
            if self.direction < 0:
                self.image = pygame.transform.flip(self.animations[self.action][int(self.frame_index)], True, False)
            else:
                self.image = self.animations[self.action][int(self.frame_index)]
            
            if self.rect.top > SCREEN_HEIGHT + 500:
                global game_restart
                game_restart = True
            return
            
        
        self.collideRect.midbottom = (self.rect.midbottom[0], self.rect.midbottom[1] - 5)
        
        now = pygame.time.get_ticks()
        if self.is_dashing:
            self.action = 'dash'
            if now - self.last_dash > self.dash_duration:
                self.is_dashing = False
                self.velocity.x = 0
        elif self.double_jump:
            self.action = 'air_spin'
        elif self.is_jumping:
            self.action = 'jump'
        elif self.on_wall:
            self.action = 'wall_slide'
        elif self.is_running:
            self.action = 'run'
        else:
            self.action = 'idle'

        self.apply_gravity()
        
        if self.is_riding_platform:
            self.rect.y += 2 * GAME_SPEED
        
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        
        # 화면 오른쪽 끝을 넘어가면 왼쪽 끝에서 나타남
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        # 화면 왼쪽 끝을 넘어가면 오른쪽 끝에서 나타남
        elif self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH

        self.frame_index += 0.15
        if self.frame_index >= len(self.animations[self.action]):
            self.frame_index = 0
        
        if self.direction < 0:
            self.image = pygame.transform.flip(self.animations[self.action][int(self.frame_index)], True, False)
        else:
            self.image = self.animations[self.action][int(self.frame_index)]

        self.is_jumping = not self.on_ground
        self.is_running = self.velocity.x != 0 and self.on_ground

    def handle_collision_with_platforms(self, platforms):
        for platform in platforms:
            if self.collideRect.colliderect(platform.rect):
                collision_type = None
                if self.velocity.y >= 0 and self.collideRect.bottom >= platform.rect.top and self.collideRect.bottom<= platform.rect.bottom:
                    self.collideRect.bottom = platform.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                    self.double_jump = False
                    collision_type = 'top'
                    self.now_interact_platform = platform

                elif self.velocity.y < 0 and self.collideRect.top <= platform.rect.bottom and self.collideRect.top >= platform.rect.top:
                    self.collideRect.top = platform.rect.bottom
                    self.velocity.y = 0
                    collision_type = 'bottom'
                
                elif self.velocity.x >= 0 and self.collideRect.right >= platform.rect.left and self.collideRect.right <= platform.rect.right and (self.collideRect.top <= platform.rect.bottom and self.collideRect.bottom >= platform.rect.top):
                    self.collideRect.right = platform.rect.left
                    collision_type = 'Lside'
                elif self.velocity.x <= 0 and self.collideRect.left <= platform.rect.right and self.collideRect.left >= platform.rect.left and (self.collideRect.top <= platform.rect.bottom and self.collideRect.bottom >= platform.rect.top):
                    self.collideRect.left = platform.rect.right
                    collision_type = 'Rside'
                        
                self.rect.midbottom = self.collideRect.midbottom[0], self.collideRect.midbottom[1] + 5

                if collision_type == 'Lside' or collision_type == 'Rside':
                    self.velocity.x = 0

                if collision_type == 'top':
                    self.is_riding_platform = True
                    break
            
            if self.now_interact_platform is not None and not self.is_jumping:
                if self.now_interact_platform.rect.right < self.rect.left or self.now_interact_platform.rect.left > self.rect.right:
                    self.on_ground = False
                    self.now_interact_platform = None
                    self.is_riding_platform = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, isStartPlatform = False, image_count = 5):
        super().__init__()
        self.isStartPlatform = isStartPlatform

        image_width, image_height = 20, 20

        total_width = image_width * image_count  # 전체 너비는 이미지 너비 * 개수
        total_height = image_height
        combined_surface = pygame.Surface((total_width, total_height))

        for i in range(image_count):
            _image = random.choice(block_images)
            _image = pygame.transform.scale(_image, (image_width, image_height))  # 이미지 크기 조정
            combined_surface.blit(_image, (i * image_width, 0))

        self.image = combined_surface
        self.rect = combined_surface.get_rect()
        
        if isStartPlatform:
            self.rect = self.image.get_rect(midbottom=(player.rect.midbottom[0], player.rect.midbottom[1] + 5))
        else:
            width = image_count * image_width
            height = image_height
            x = random.randint(0, SCREEN_WIDTH - width)
            y = -height  # 화면 위에서 시작
            self.rect = self.image.get_rect(topleft=(x, y))
            self.ableToScoreUP = True
    
    def update(self):
        if not self.isStartPlatform:
            self.rect.y += 2 * GAME_SPEED  # 내려오는 속도 조절
        
    def handle_collision_with_player(self, player):
        if not self.isStartPlatform:
            if self.ableToScoreUP and self.rect.colliderect(player.rect):
                self.ableToScoreUP = False
                return 1
        return 0

class BackGround(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.image = random.choice(cloud_images)
        width = self.image.get_width()
        height = self.image.get_height()
        x = random.randint(0, SCREEN_WIDTH - width)
        y = -height  # 화면 위에서 시작
        self.rect = self.image.get_rect(topleft=(x, y))
    
    def update(self):
        self.rect.y += 1.5 * GAME_SPEED


players = pygame.sprite.Group()
platforms = pygame.sprite.Group()
backgrounds = pygame.sprite.Group()

player = Player()
players.add(player)

start_platform = Platform(True)
platforms.add(start_platform)

PLATFORM_CREATION_INTERVAL = 3000

last_platform_creation_time = 0
last_cloud_creation_time = 0

last_death_time = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_restart:
                game_over = False
                game_restart = False
                player = Player()
                players.empty()
                players.add(player)
                platforms.empty()
                start_platform = Platform(True)
                platforms.add(start_platform)
                last_platform_creation_time = 0
                GAME_SPEED = 1
                GAME_SCORE = 0
                last_death_time = pygame.time.get_ticks()
            else:
                if event.key == pygame.K_z or event.key == pygame.K_UP:
                    if start_platform is not None:
                        platforms.remove(start_platform)
                    player.jump()
                if event.key == pygame.K_x:
                    player.dash()
    
    if not game_restart:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-1)
        if keys[pygame.K_RIGHT]:
            player.move(1)
        
        current_time = pygame.time.get_ticks() - last_death_time

        if current_time - last_platform_creation_time > round(random.uniform(PLATFORM_CREATION_INTERVAL * 0.5- current_time / 10000, PLATFORM_CREATION_INTERVAL - current_time / 10000),3):
            new_platform = Platform(image_count=random.randint(1, 10))
            platforms.add(new_platform)
            
            new_background = BackGround()
            backgrounds.add(new_background)
            
            last_platform_creation_time = current_time
        
        if current_time - last_cloud_creation_time > round(random.uniform(4000, 15000),3):
            new_background = BackGround()
            backgrounds.add(new_background)
            
            last_cloud_creation_time = current_time
            
        GAME_SPEED = round(current_time / 100000,3) + 1

        player.handle_collision_with_platforms(platforms)
        for platform in platforms:
            GAME_SCORE += platform.handle_collision_with_player(player)

        backgrounds.update()
        platforms.update()
        players.update()
        
        for platform in platforms:
            if platform.rect.top > SCREEN_HEIGHT + 100  :
                platforms.remove(platform)
        
        for background in backgrounds:
            if background.rect.top > SCREEN_HEIGHT:
                backgrounds.remove(background)
        
        if not game_over and player.rect.top > SCREEN_HEIGHT + 100:
            game_over = True
            play_rand_sound(death_sounds)

    screen.fill((69, 193, 255))
    
    font = pygame.font.SysFont(None, 55)
    text = font.render('Score \n    ' + str(GAME_SCORE), True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, text.get_height() // 2 + 50))
    screen.blit(text, text_rect)
    
    if not game_restart:
        backgrounds.draw(screen)
        platforms.draw(screen)
        players.draw(screen)
    else:
        font = pygame.font.SysFont(None, 55)
        text = font.render('Press any key to restart', True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
        _game_over_image = game_over_image.copy()
        _game_over_image = pygame.transform.scale(_game_over_image, (_game_over_image.get_width() * 2, _game_over_image.get_height() * 2))
        screen.blit(_game_over_image, _game_over_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4+100)))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
