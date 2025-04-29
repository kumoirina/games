import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -10
PLAYER_SPEED = 5

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

    def update(self, platforms):
        # Horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

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

        # Jumping
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_STRENGTH

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# Create groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create platforms
ground = Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)
platform1 = Platform(200, 400, 150, 20)
platform2 = Platform(450, 300, 150, 20)

platforms.add(ground, platform1, platform2)
all_sprites.add(ground, platform1, platform2)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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