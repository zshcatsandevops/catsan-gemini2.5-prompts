import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
RED = (210, 40, 40)      # Player
GREEN = (0, 150, 0)       # Ground
BROWN = (139, 69, 19)     # Enemy
YELLOW = (255, 220, 0)    # "Coin" Block

# Physics
GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 5
ENEMY_SPEED = 2

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Use a simple rectangle for the player sprite
        self.image = pygame.Surface((20, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Movement variables
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def update(self, keys, platforms):
        # Reset horizontal velocity
        self.vel_x = 0
        
        # --- Handle Input ---
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
        if keys[pygame.K_SPACE] and self.on_ground:
            # Player jumps
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            
        # --- Apply Physics ---
        # Apply gravity
        if not self.on_ground:
            self.vel_y += GRAVITY
            if self.vel_y > 10: # Terminal velocity
                self.vel_y = 10
                
        # --- Move and Check Collisions ---
        
        # Horizontal movement and collision
        self.rect.x += self.vel_x
        self.check_collisions_x(platforms)
        
        # Vertical movement and collision
        self.rect.y += self.vel_y
        self.on_ground = False # Assume not on ground until collision check
        self.check_collisions_y(platforms)

        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def check_collisions_x(self, platforms):
        """Check for horizontal collisions."""
        hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hit_list:
            if self.vel_x > 0: # Moving right
                self.rect.right = platform.rect.left
            elif self.vel_x < 0: # Moving left
                self.rect.left = platform.rect.right
                
    def check_collisions_y(self, platforms):
        """Check for vertical collisions."""
        hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hit_list:
            if self.vel_y > 0: # Moving down (falling)
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0: # Moving up (jumping)
                self.rect.top = platform.rect.bottom
                self.vel_y = 0 # Bonk!

    def reset(self, x, y):
        """Called when player falls or is hit."""
        self.rect.topleft = (x, y)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

# --- Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, move_range):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        self.start_x = x
        self.move_range = move_range
        self.direction = ENEMY_SPEED

    def update(self):
        # Move back and forth
        self.rect.x += self.direction
        if self.rect.x > self.start_x + self.move_range or self.rect.x < self.start_x:
            self.direction *= -1 # Turn around

# --- Platform Class ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=GREEN):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# --- Main Game Function ---
def main():
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("GBA-style Platformer Simulation")
    clock = pygame.time.Clock()

    # --- Create Game Objects ---
    
    # Sprite groups
    all_sprites = pygame.sprite.Group()
    platform_list = pygame.sprite.Group()
    enemy_list = pygame.sprite.Group()

    # Create player
    player_start_pos = (50, 300)
    player = Player(player_start_pos[0], player_start_pos[1])
    all_sprites.add(player)
    
    # Create platforms for a simple level
    # Ground
    ground = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
    platform_list.add(ground)
    
    # Floating platforms
    plat1 = Platform(200, 300, 100, 20)
    platform_list.add(plat1)
    
    plat2 = Platform(350, 240, 80, 20)
    platform_list.add(plat2)
    
    # "Coin" block
    coin_block = Platform(150, 250, 30, 30, YELLOW)
    platform_list.add(coin_block)

    # Add all platforms to all_sprites group for drawing
    all_sprites.add(platform_list)
    
    # Create enemy
    enemy = Enemy(200, 280, 80) # x, y, move_range
    enemy_list.add(enemy)
    all_sprites.add(enemy)

    # --- Game Loop ---
    running = True
    while running:
        # Keep loop running at the right speed
        clock.tick(FPS)
        
        # --- Process Input (Events) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # --- Update ---
        keys = pygame.key.get_pressed()
        player.update(keys, platform_list)
        enemy_list.update()
        
        # --- Check for Game Over Conditions ---
        # Player falls off screen
        if player.rect.top > SCREEN_HEIGHT:
            player.reset(player_start_pos[0], player_start_pos[1])

        # Check for collision with enemies
        enemy_hit_list = pygame.sprite.spritecollide(player, enemy_list, False)
        for hit_enemy in enemy_hit_list:
            # Check if player landed on top of enemy (a simple stomp)
            if player.vel_y > 0 and (player.rect.bottom < hit_enemy.rect.centery):
                hit_enemy.kill() # "Stomped" the enemy
                player.vel_y = -JUMP_STRENGTH / 2 # Small bounce
            else:
                # Player was hit from the side or bottom
                player.reset(player_start_pos[0], player_start_pos[1])
        
        # --- Draw / Render ---
        screen.fill(SKY_BLUE)
        all_sprites.draw(screen) # Draw all sprites in the group
        
        # --- Flip the display ---
        pygame.display.flip()

    # --- Quit ---
    pygame.quit()
    sys.exit()

# --- Run the Game ---
if __name__ == "__main__":
    main()
