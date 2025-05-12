import pygame
import sys
from src.constants import init_display
from src.game import Game

def main():
    # Initialize pygame
    pygame.init()
    
    # Create display
    screen = init_display()
    
    # Hide mouse cursor
    pygame.mouse.set_visible(False)
    
    # Enable mouse motion tracking for velocity calculations
    pygame.event.set_grab(True)
    
    # Create game instance
    game = Game()
    
    # Main game loop - keep running the game
    while True:
        game.run(screen)
        
        # Check if we need to exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()
