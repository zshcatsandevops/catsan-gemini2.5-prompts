import pygame
import textwrap
import math  # Import the math module for the sine function

# --- Configuration ---
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
BACKGROUND_COLOR = (20, 20, 40)  # Dark blue, Melee-like
TEXT_COLOR = (230, 230, 255)
TITLE_COLOR = (255, 255, 100)
FEATHER_BASE_WIDTH = 100  # Base width for the feather drawing
FEATHER_BASE_HEIGHT = 200 # Base height for the feather drawing

# --- Trophy Details (Custom-written in Melee style) ---
TROPHY_TITLE = "Cape Feather"
TROPHY_DESCRIPTION = (
    "This mystical feather first appeared in Super Mario World. Grabbing it "
    "would transform Mario into Cape Mario, allowing him to fly for sustained "
    "periods and perform a spinning cape attack. While this feather doesn't "
    "appear as an item in Super Smash Bros. Melee, its power is channeled by "
    "Mario for his side special move, the Cape. A well-timed flick of the Cape "
    "can reflect projectiles and spin opponents right around!"
)
TROPHY_GAME = "Appears in: Super Mario World"
ROTATION_INSTRUCTION = "(Use Left/Right Arrows to Rotate)"


# --- Helper Function to Wrap Text ---
def draw_text(surface, text, pos, font, color, max_width):
    """Draws text on a surface, wrapping it to a max width."""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    
    lines.append(current_line)

    x, y = pos
    for line in lines:
        line_surface = font.render(line, True, color)
        surface.blit(line_surface, (x, y))
        y += font.get_linesize()

# --- Helper Function to Create the Feather Surface ---
def create_feather_surface(width, height):
    """Draws the feather onto a new, transparent surface."""
    # Create a surface with a per-pixel alpha channel
    feather_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    
    center_x = width // 2
    center_y = height // 2
    
    # Colors
    WHITE = (255, 255, 255)
    RED = (220, 0, 0)
    YELLOW = (255, 220, 0)
    GRAY = (180, 180, 180)
    
    # Adjust drawing coordinates to be relative to the new surface
    # Center y-offset to make it fit well
    y_offset = 10 

    # Feather Body (White Polygon)
    white_points = [
        (center_x - 5, center_y - 80 + y_offset),  # top tip
        (center_x + 40, center_y - 20 + y_offset), # top-right
        (center_x + 30, center_y + 50 + y_offset), # bottom-right
        (center_x - 10, center_y + 80 + y_offset), # bottom-tip
        (center_x - 30, center_y + 50 + y_offset), # bottom-left
        (center_x - 40, center_y - 20 + y_offset)  # top-left
    ]
    pygame.draw.polygon(feather_surf, WHITE, white_points)

    # Quill Line (Gray Line)
    pygame.draw.line(feather_surf, GRAY, (center_x - 8, center_y - 75 + y_offset), (center_x - 2, center_y + 78 + y_offset), 3)

    # Red Sash (Red Polygon)
    red_points = [
        (center_x - 30, center_y + 45 + y_offset),
        (center_x + 30, center_y + 45 + y_offset),
        (center_x + 25, center_y + 70 + y_offset),
        (center_x - 25, center_y + 70 + y_offset)
    ]
    pygame.draw.polygon(feather_surf, RED, red_points)

    # Quill Tip (Yellow Polygon)
    yellow_points = [
        (center_x - 10, center_y + 78 + y_offset),
        (center_x + 10, center_y + 78 + y_offset),
        (center_x, center_y + 95 + y_offset)
    ]
    pygame.draw.polygon(feather_surf, YELLOW, yellow_points)
    
    return feather_surf


# --- Main Function ---
def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Melee Trophy Viewer: Cape Feather")
    clock = pygame.time.Clock()

    # Load fonts
    try:
        title_font = pygame.font.SysFont("Arial", 28, bold=True)
        body_font = pygame.font.SysFont("Arial", 18)
        instruction_font = pygame.font.SysFont("Arial", 16, bold=True)
    except:
        print("Arial font not found, using default font.")
        title_font = pygame.font.Font(None, 34)
        body_font = pygame.font.Font(None, 24)
        instruction_font = pygame.font.Font(None, 22)

    # --- Create the base feather surface ---
    original_feather_surface = create_feather_surface(FEATHER_BASE_WIDTH, FEATHER_BASE_HEIGHT)

    # --- Animation Variables ---
    float_angle = 0  # Angle for the sine wave to create floating effect
    float_speed = 0.05  # How fast the trophy bobs
    float_amplitude = 10  # How high and low the trophy bobs
    
    rotate_angle = 0 # Angle for 3D rotation
    rotate_speed = 0.05 # How fast it rotates when key is held

    # --- Main Loop ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Handle rotation input (holding keys)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            rotate_angle -= rotate_speed
        if keys[pygame.K_RIGHT]:
            rotate_angle += rotate_speed

        # --- Draw ---
        screen.fill(BACKGROUND_COLOR)

        # Update float animation
        float_angle = (float_angle + float_speed) % (2 * math.pi)
        y_offset = int(math.sin(float_angle) * float_amplitude)

        # --- 3D Rotation Simulation ---
        # Calculate horizontal scaling based on cosine of the angle
        scale_x_factor = math.cos(rotate_angle)
        scaled_width = int(FEATHER_BASE_WIDTH * abs(scale_x_factor))
        
        if scaled_width > 0: # Avoid scaling to 0 width
            # Scale the original feather surface
            scaled_surface = pygame.transform.smoothscale(
                original_feather_surface, (scaled_width, FEATHER_BASE_HEIGHT)
            )
            
            # If scale is negative, flip the image horizontally
            if scale_x_factor < 0:
                scaled_surface = pygame.transform.flip(scaled_surface, True, False)
        
            # Get rect and position
            base_cx = SCREEN_WIDTH * 0.25
            base_cy = SCREEN_HEIGHT / 2
            draw_rect = scaled_surface.get_rect(center=(base_cx, base_cy + y_offset))
            screen.blit(scaled_surface, draw_rect)


        # Draw Text
        text_x_start = SCREEN_WIDTH * 0.5
        text_max_width = SCREEN_WIDTH * 0.45

        # Title
        title_surface = title_font.render(TROPHY_TITLE, True, TITLE_COLOR)
        screen.blit(title_surface, (text_x_start, SCREEN_HEIGHT * 0.1))

        # Description
        draw_text(screen, TROPHY_DESCRIPTION, (text_x_start, SCREEN_HEIGHT * 0.25), body_font, TEXT_COLOR, text_max_width)

        # Game of Origin
        game_surface = body_font.render(TROPHY_GAME, True, TITLE_COLOR)
        screen.blit(game_surface, (text_x_start, SCREEN_HEIGHT * 0.82))
        
        # Rotation Instructions
        instruction_surface = instruction_font.render(ROTATION_INSTRUCTION, True, TITLE_COLOR)
        screen.blit(instruction_surface, (text_x_start, SCREEN_HEIGHT * 0.90))


        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

