import pygame

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors - Psychedelic palette
COLORS = [
    (255, 0, 128),  # Hot pink
    (128, 0, 255),  # Purple
    (0, 255, 255),  # Cyan
    (255, 255, 0),  # Yellow
    (0, 255, 128),  # Turquoise
    (255, 128, 0),  # Orange
]

# Initialize pygame display
def init_display():
    """Initialize pygame display with the appropriate width and height."""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Psychedelic Footbag")
    return screen
