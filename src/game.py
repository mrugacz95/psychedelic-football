import pygame
import sys
import math
from src.constants import WIDTH, HEIGHT, COLORS
from src.leg import Leg
from src.footbag import Footbag

# Background color cycling
bg_color_index = 0
bg_color_timer = 0
bg_color_change_speed = 0.5

class Game:
    def __init__(self):
        self.leg = Leg()
        self.footbag = Footbag()
        self.running = True
        self.score = 0
        self.font = pygame.font.Font(None, 48)
        
        # Title animation properties
        self.title_font = pygame.font.Font(None, 64)  # Slightly smaller font size for better visibility
        self.title_text = "Psychedelic Footbag"
        self.title_color_index = 0
        self.title_color_timer = 0
        self.title_y_offset = 0
        self.title_wave_amplitude = 10  # Reduced amplitude for better legibility
        self.title_wave_frequency = 0.1
        self.title_wave_speed = 0.05
        self.title_wave_time = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
    def update(self):
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Update leg position
        self.leg.update(mouse_pos)
        
        # Check for collision between footbag and leg
        if self.leg.check_footbag_collision(self.footbag):
            self.score += 1
            
        # Update footbag
        self.footbag.update()
        
        # Check if footbag hit ground
        if self.footbag.check_ground_collision():
            self.running = False
            
        # Update background color
        global bg_color_timer, bg_color_index
        bg_color_timer += bg_color_change_speed
        if bg_color_timer >= 100:
            bg_color_timer = 0
            bg_color_index = (bg_color_index + 1) % len(COLORS)
            
        # Update title animation
        self.title_wave_time += self.title_wave_speed
        self.title_color_timer += 1
        if self.title_color_timer > 15:  # Cycle colors more quickly than background
            self.title_color_timer = 0
            self.title_color_index = (self.title_color_index + 1) % len(COLORS)
        
    def draw(self, screen):
        # Fill background with psychedelic color gradient
        bg_color = COLORS[bg_color_index]
        bg_color2 = COLORS[(bg_color_index + 1) % len(COLORS)]
        for y in range(0, HEIGHT, 4):
            # Interpolate between colors
            t = y / HEIGHT
            color = (
                int(bg_color[0] * (1 - t) + bg_color2[0] * t),
                int(bg_color[1] * (1 - t) + bg_color2[1] * t),
                int(bg_color[2] * (1 - t) + bg_color2[2] * t)
            )
            pygame.draw.rect(screen, color, (0, y, WIDTH, 4))
            
        # Draw animated title
        self.draw_animated_title(screen)
            
        # Draw objects
        self.leg.draw(screen)
        self.footbag.draw(screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
        
    def draw_animated_title(self, screen):
        """Draw the animated title at the top of the screen."""
        # Get base color for the title
        title_color = COLORS[self.title_color_index]
        
        # Set up position variables
        title_width = self.title_font.size(self.title_text)[0]
        title_start_x = (WIDTH - title_width) // 2
        
        # Fixed vertical position near the top of the screen (not too high)
        base_y = 60
        
        # Create a background for better visibility
        bg_rect = pygame.Rect(0, 20, WIDTH, 100)
        bg_color = (0, 0, 0, 70)  # Semi-transparent black
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill(bg_color)
        screen.blit(bg_surf, bg_rect)
        
        # Draw the glow effect first
        glow_color = (title_color[0], title_color[1], title_color[2], 60)
        x_pos = title_start_x
        
        for i, char in enumerate(self.title_text):
            # Skip spaces for glow effect
            if char == " ":
                x_pos += self.title_font.size(" ")[0]
                continue
                
            # Calculate wave offset for this character
            wave_offset = math.sin(self.title_wave_time + i * self.title_wave_frequency) * self.title_wave_amplitude
            
            # Draw glow (multiple offsets for bloom effect)
            char_surf = self.title_font.render(char, True, glow_color)
            for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                screen.blit(char_surf, (x_pos + offset[0], base_y + wave_offset + offset[1]))
                
            x_pos += self.title_font.size(char)[0]
        
        # Now draw the main text over the glow
        x_pos = title_start_x
        for i, char in enumerate(self.title_text):
            # Calculate wave offset
            wave_offset = math.sin(self.title_wave_time + i * self.title_wave_frequency) * self.title_wave_amplitude
            
            # Create bright color for this character
            bright_color = (min(255, title_color[0] + 50), 
                           min(255, title_color[1] + 50), 
                           min(255, title_color[2] + 50))
            
            # Alternate between normal and bright colors
            color = bright_color if i % 2 == 0 else title_color
            
            # Render and position the character
            char_surf = self.title_font.render(char, True, color)
            screen.blit(char_surf, (x_pos, base_y + wave_offset))
            
            # Move to next character position
            x_pos += self.title_font.size(char)[0]
        
    def game_over_screen(self, screen):
        # Display game over message
        game_over_text = self.font.render("GAME OVER", True, (255, 255, 255))
        final_score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        restart_text = self.font.render("Press SPACE to restart", True, (255, 255, 255))
        
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
        screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))
        
        pygame.display.flip()
        
        # Wait for restart or quit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Restart game
                        self.__init__()
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
        
    def run(self, screen):
        clock = pygame.time.Clock()
        
        # Main game loop
        while self.running:
            self.handle_events()
            self.update()
            self.draw(screen)
            pygame.display.flip()
            clock.tick(60)
            
        # Game over
        self.game_over_screen(screen)
