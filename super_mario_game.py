import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -13
PLAYER_SPEED = 5
PLATFORM_SPACING = 200
MAX_JUMP_HEIGHT = abs((JUMP_STRENGTH * JUMP_STRENGTH) / (2 * GRAVITY))
MIN_HEIGHT_INCREASE = 30  # 最小高度增加
MAX_HEIGHT_INCREASE = MAX_JUMP_HEIGHT - 20  # 最大高度增加，比最大跳跃高度小一点

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - 100)
        self.vel_y = 0
        self.on_ground = False
        self.jump_count = 0  # 追踪跳跃次数
        self.world_x = self.rect.x  # 添加世界坐标

    def update(self, platforms):
        # Horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.world_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.world_x += PLAYER_SPEED
        
        # 更新实际位置
        self.rect.x = self.world_x - camera_offset

        # Vertical movement (gravity)
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Collision detection
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True
                self.jump_count = 0  # 落地时重置跳跃次数

        # Jumping with double jump
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if self.on_ground or self.jump_count < 2:  # 允许最多跳两次（一段跳+二段跳）
                self.vel_y = JUMP_STRENGTH
                self.jump_count += 1
                self.on_ground = False

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.world_x = x  # 添加世界坐标

class PlatformGenerator:
    def __init__(self):
        self.last_platform_x = 600
        self.last_platform_y = SCREEN_HEIGHT - 200  # 初始平台高度
        self.create_initial_ground()
    
    def create_initial_ground(self):
        # 创建连续的地面
        for x in range(0, SCREEN_WIDTH * 2, SCREEN_WIDTH):
            ground = Platform(x, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)
            platforms.add(ground)
            all_sprites.add(ground)
            self.last_platform_x = max(self.last_platform_x, x + SCREEN_WIDTH)

    def generate_platforms(self, camera_offset):
        while self.last_platform_x - camera_offset < SCREEN_WIDTH + 400:
            # 生成新的地面段
            ground = Platform(self.last_platform_x, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)
            platforms.add(ground)
            all_sprites.add(ground)
            
            # 生成跳跃平台
            platform_width = 150
            platform_height = 20
            
            # 计算新平台的高度（比前一个平台更高）
            height_increase = random.randint(MIN_HEIGHT_INCREASE, int(MAX_HEIGHT_INCREASE))
            platform_y = self.last_platform_y - height_increase  # 减少y值使平台升高
            
            # 确保平台不会太高
            if platform_y < 100:  # 设置最高限制
                platform_y = SCREEN_HEIGHT - 200  # 重置到较低位置
            
            # 生成新平台
            platform_x = self.last_platform_x + random.randint(150, 200)  # 缩小水平间距范围
            new_platform = Platform(platform_x, platform_y, platform_width, platform_height)
            
            platforms.add(new_platform)
            all_sprites.add(new_platform)
            
            # 更新最后一个平台的信息
            self.last_platform_x = platform_x
            self.last_platform_y = platform_y

# Create groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# 创建平台生成器并初始化相机偏移量
platform_generator = PlatformGenerator()
camera_offset = 0

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 更新相机位置（修改为更平滑的跟随）
    target_offset = max(0, player.world_x - SCREEN_WIDTH // 3)
    camera_offset += (target_offset - camera_offset) * 0.1

    # 生成新平台
    platform_generator.generate_platforms(camera_offset)

    # 删除已经离开屏幕的平台（保留地面）
    for platform in platforms:
        if platform.rect.height != 20:  # 不是地面才删除
            if platform.rect.right - camera_offset < -100:
                platform.kill()

    # 更新所有sprite的位置
    for sprite in all_sprites:
        if sprite != player:
            sprite.rect.x = sprite.world_x - camera_offset

    # Update
    all_sprites.update(platforms)

    # Draw
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Refresh display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()