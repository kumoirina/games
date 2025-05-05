import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -15
PLAYER_SPEED = 5
PLATFORM_SPACING = 200
MAX_JUMP_HEIGHT = abs((JUMP_STRENGTH * JUMP_STRENGTH) / (2 * GRAVITY))
MIN_HEIGHT_INCREASE = 30  # 最小高度增加
MAX_HEIGHT_INCREASE = MAX_JUMP_HEIGHT - 20  # 最大高度增加，比最大跳跃高度小一点

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 添加字体
pygame.font.init()
FONT = pygame.font.Font(None, 74)
SMALL_FONT = pygame.font.Font(None, 36)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.world_x = x

# 添加旗帜类
class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.world_x = x

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
        self.score = 0
        self.game_started = False
        self.game_over = False
        self.victory = False  # 添加胜利状态

    def update(self, platforms):
        if self.game_over:
            return

        # Horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.world_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.world_x += PLAYER_SPEED
        
        # 更新实际位置
        self.rect.x = self.world_x - camera_offset

        # 存储原始Y位置用于碰撞检测
        original_y = self.rect.y
        
        # Vertical movement (gravity)
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Collision detection
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # 从上方碰撞
                if original_y + self.rect.height <= platform.rect.top and self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                # 从下方碰撞
                elif original_y >= platform.rect.bottom and self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # Jumping with double jump
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if self.on_ground or self.jump_count < 2:
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
        self.coins_generated = 0  # 追踪已生成的金币数量
        self.flag_generated = False  # 追踪是否已生成旗帜
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
            
            # 在平台上方生成金币
            if platform_height == 20 and self.coins_generated < 100:  # 限制金币数量
                coin = Coin(platform_x + platform_width//2, platform_y - 40)
                coins.add(coin)
                all_sprites.add(coin)
                self.coins_generated += 1
                
                # 在第100个金币后生成旗帜
                if self.coins_generated == 100 and not self.flag_generated:
                    flag = Flag(platform_x + platform_width + 100, platform_y - 80)
                    flags.add(flag)
                    all_sprites.add(flag)
                    self.flag_generated = True
            
            # 更新最后一个平台的信息
            self.last_platform_x = platform_x
            self.last_platform_y = platform_y

def reset_game():
    global player, all_sprites, platforms, coins, flags, platform_generator, camera_offset
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    flags = pygame.sprite.Group()
    
    player = Player()
    all_sprites.add(player)
    
    platform_generator = PlatformGenerator()
    camera_offset = 0

def draw_game_over():
    game_over_text = FONT.render("Victory!" if player.victory else "Game Over", True, RED)
    score_text = SMALL_FONT.render(f"Score: {player.score}", True, BLACK)
    restart_text = SMALL_FONT.render("Restart", True, BLACK)
    
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70))
    
    screen.blit(game_over_text, text_rect)
    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)
    
    return restart_rect

# Create groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
coins = pygame.sprite.Group()
flags = pygame.sprite.Group()

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
        elif event.type == pygame.MOUSEBUTTONDOWN and player.game_over:
            mouse_pos = pygame.mouse.get_pos()
            if restart_button_rect.collidepoint(mouse_pos):
                reset_game()
    
    if not player.game_over:
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

        # 检测金币碰撞
        coin_collisions = pygame.sprite.spritecollide(player, coins, True)
        for coin in coin_collisions:
            player.score += 10
            if not player.game_started:
                player.game_started = True

        # 检测旗帜碰撞
        flag_collisions = pygame.sprite.spritecollide(player, flags, False)
        if flag_collisions:
            player.game_over = True
            player.victory = True

        # Update
        all_sprites.update(platforms)

    # Draw
    screen.fill(WHITE)
    all_sprites.draw(screen)
    
    # 显示分数和收集进度
    score_text = SMALL_FONT.render(f"Score: {player.score}", True, BLACK)
    progress_text = SMALL_FONT.render(f"Coins: {player.score//10}/100", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(progress_text, (10, 40))
    
    if player.game_over:
        restart_button_rect = draw_game_over()
    
    # Refresh display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()