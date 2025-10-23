import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
LEVEL_WIDTH = 1800 # Level is now 3x wider than screen
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
RED = (210, 40, 40)      # Player (Small)
ORANGE = (255, 140, 0)    # Player (Super)
GREEN = (0, 150, 0)       # Ground
BROWN = (139, 69, 19)     # Enemy
YELLOW = (255, 220, 0)    # "Coin" Block
GRAY = (150, 150, 150)    # "Used" Block

# Physics
GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 5
ENEMY_SPEED = 2

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # State variables
        self.is_super = False
        self.is_invincible = False # To prevent rapid hits
        self.invincible_timer = 0
        
        # Create small image
        self.image_small = pygame.Surface((20, 30))
        self.image_small.fill(RED)
        
        # Create super image
        self.image_super = pygame.Surface((20, 40))
        self.image_super.fill(ORANGE)
        
        # Set initial image and rect
        self.image = self.image_small
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Movement variables
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def update(self, keys, platforms, camera_x):
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

        # Keep player within level bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH
            
        # Update invincibility timer
        if self.is_invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.is_invincible = False
                # Simple flash effect off
                if self.is_super:
                    self.image.fill(ORANGE)
                else:
                    self.image.fill(RED)

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
                
                # Check if we bonked a special block
                if platform.type == 'coin_block':
                    self.hit_coin_block(platform)

    def hit_coin_block(self, block):
        """Called when player hits a coin block from below."""
        if not self.is_super:
            self.grow()
        block.color = GRAY # Change color to "used"
        block.image.fill(block.color)
        block.type = 'used' # Can't be used again

    def grow(self):
        """Make the player 'super'."""
        if not self.is_super:
            self.is_super = True
            # Move rect up so it doesn't fall through floor
            bottom = self.rect.bottom
            self.image = self.image_super
            self.rect = self.image.get_rect(bottom=bottom, centerx=self.rect.centerx)

    def shrink(self):
        """Make the player 'small' after getting hit."""
        self.is_super = False
        self.is_invincible = True
        self.invincible_timer = FPS * 2 # 2 seconds of invincibility
        
        # Move rect up so it doesn't fall through floor
        bottom = self.rect.bottom
        self.image = self.image_small
        self.rect = self.image.get_rect(bottom=bottom, centerx=self.rect.centerx)
        self.image.fill(RED) # Ensure it's the right color

    def take_damage(self):
        """Handle player taking damage from an enemy."""
        if not self.is_invincible:
            if self.is_super:
                self.shrink()
            else:
                return True # Return True to signal game reset
        return False # No reset needed

    def reset(self, x, y):
        """Called when player falls or is hit."""
        self.rect.topleft = (x, y)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        # Reset to small
        if self.is_super:
            self.shrink()
            self.is_invincible = False
            self.image.fill(RED)


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
    def __init__(self, x, y, w, h, color=GREEN, type='platform'):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.color = color
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.type = type

# --- Main Game Function ---
def main():
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("GBA-style Platformer Simulation")
    clock = pygame.time.Clock()
    
    # Camera offset
    camera_x = 0

    # --- Create Game Objects ---
    
    # Sprite groups
    all_sprites = pygame.sprite.Group()
    platform_list = pygame.sprite.Group()
    enemy_list = pygame.sprite.Group()

    # Create player
    player_start_pos = (50, 300)
    player = Player(player_start_pos[0], player_start_pos[1])
    all_sprites.add(player)
    
    # --- Create platforms for a simple level ---
    # Ground
    ground = Platform(0, SCREEN_HEIGHT - 40, LEVEL_WIDTH, 40)
    platform_list.add(ground)
    
    # Floating platforms
    plat1 = Platform(200, 300, 100, 20)
    platform_list.add(plat1)
    
    plat2 = Platform(350, 240, 80, 20)
    platform_list.add(plat2)
    
    # "Coin" block
    coin_block = Platform(150, 250, 30, 30, YELLOW, 'coin_block')
    platform_list.add(coin_block)
    
    # More level content
    plat3 = Platform(550, 200, 100, 20)
    platform_list.add(plat3)
    
    plat4 = Platform(700, 300, 150, 20)
    platform_list.add(plat4)
    
    plat5 = Platform(900, 250, 50, 20)
    platform_list.add(plat5)
    
    plat6 = Platform(1100, 200, 100, 20)
    platform_list.add(plat6)

    # Add all platforms to all_sprites group for drawing
    all_sprites.add(platform_list)
    
    # --- Create enemies ---
    enemy1 = Enemy(200, 280, 80) # On plat1
    enemy_list.add(enemy1)
    
    enemy2 = Enemy(700, 280, 130) # On plat4
    enemy_list.add(enemy2)
    
    all_sprites.add(enemy_list)

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
        player.update(keys, platform_list, camera_x)
        enemy_list.update()
        
        # --- Update Camera ---
        # Tries to center player, but stops at level edges
        target_camera_x = player.rect.x - SCREEN_WIDTH // 2
        # Clamp camera to level bounds
        if target_camera_x < 0:
            camera_x = 0
        elif target_camera_x > LEVEL_WIDTH - SCREEN_WIDTH:
            camera_x = LEVEL_WIDTH - SCREEN_WIDTH
        else:
            camera_x = target_camera_x

        # --- Check for Game Over Conditions ---
        # Player falls off screen
        if player.rect.top > SCREEN_HEIGHT:
            player.reset(player_start_pos[0], player_start_pos[1])

        # Check for collision with enemies
        enemy_hit_list = pygame.sprite.spritecollide(player, enemy_list, False)
        for hit_enemy in enemy_hit_list:
            # Check if player landed on top of enemy (a simple stomp)
            if player.vel_y > 0 and (player.rect.bottom < hit_enemy.rect.centery + 10):
                hit_enemy.kill() # "Stomped" the enemy
                player.vel_y = -JUMP_STRENGTH / 2 # Small bounce
            else:
                # Player was hit from the side or bottom
                if player.take_damage(): # take_damage returns True if reset is needed
                    player.reset(player_start_pos[0], player_start_pos[1])
        
        # --- Draw / Render ---
        screen.fill(SKY_BLUE)
        
        # Draw all sprites offset by the camera
        for sprite in all_sprites:
            # Simple flash effect for invincibility
            if player.is_invincible and sprite == player:
                if (pygame.time.get_ticks() // 100) % 2 == 0:
                    # Draw nothing (skip)
                    continue
            
            screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))
        
        # --- Flip the display ---
        pygame.display.flip()

    # --- Quit ---
    pygame.quit()
    sys.exit()

# --- Run the Game ---
if __name__ == "__main__":
    main()
