import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Psychedelic Footbag")

# Colors - Psychedelic palette
COLORS = [
    (255, 0, 128),  # Hot pink
    (128, 0, 255),  # Purple
    (0, 255, 255),  # Cyan
    (255, 255, 0),  # Yellow
    (0, 255, 128),  # Turquoise
    (255, 128, 0),  # Orange
]

# Background color cycling
bg_color_index = 0
bg_color_timer = 0
bg_color_change_speed = 0.5

# Game objects
class Footbag:
    def __init__(self):
        self.base_radius = 15
        self.position = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.velocity = pygame.Vector2(random.uniform(-2, 2), -6)  # Reduced initial velocity
        self.gravity = 0.2  # Slightly reduced gravity
        self.color_index = 0
        self.color_timer = 0
        
        # Blob physics parameters
        self.num_points = 12  # Number of points around the blob
        self.elasticity = 0.3  # How quickly points return to their original positions
        self.damping = 0.85  # Damping for point movement
        self.points = []  # Points defining the blob shape
        self.target_points = []  # Where points want to return to
        self.point_velocities = []  # Velocity of each point
        
        # Initialize blob points in a circle
        for i in range(self.num_points):
            angle = 2 * math.pi * i / self.num_points
            point = pygame.Vector2(
                self.position.x + math.cos(angle) * self.base_radius,
                self.position.y + math.sin(angle) * self.base_radius
            )
            self.points.append(point)
            self.target_points.append(pygame.Vector2(
                math.cos(angle) * self.base_radius,
                math.sin(angle) * self.base_radius
            ))
            self.point_velocities.append(pygame.Vector2(0, 0))
        
        # Track collisions for deformation effects
        self.last_collision = None
        self.collision_timer = 0
        
    def update(self):
        # Apply gravity
        self.velocity.y += self.gravity
        
        # Update position
        prev_position = pygame.Vector2(self.position)
        self.position += self.velocity
        
        # Bounce off walls
        collision_normal = None
        if self.position.x - self.base_radius < 0:
            self.position.x = self.base_radius
            self.velocity.x *= -0.8  # Reduced bounciness
            collision_normal = pygame.Vector2(1, 0)
        elif self.position.x + self.base_radius > WIDTH:
            self.position.x = WIDTH - self.base_radius
            self.velocity.x *= -0.8  # Reduced bounciness
            collision_normal = pygame.Vector2(-1, 0)
        
        # Bounce off ceiling (top)
        if self.position.y - self.base_radius < 0:
            self.position.y = self.base_radius
            self.velocity.y *= -0.7  # Reduced bounciness
            collision_normal = pygame.Vector2(0, 1)
        
        # Record collision for deformation effect
        if collision_normal:
            self.last_collision = collision_normal
            self.collision_timer = 10  # Duration of deformation effect
        elif self.collision_timer > 0:
            self.collision_timer -= 1
        else:
            self.last_collision = None
            
        # Update blob points
        position_delta = self.position - prev_position
        for i in range(self.num_points):
            # Move points with the center position
            self.points[i] += position_delta
            
            # Calculate current relative position from center
            relative_pos = self.points[i] - self.position
            
            # Target position is where the point would be in the circle
            target_pos = self.position + self.target_points[i]
            
            # Add force toward target position (elasticity)
            force = (target_pos - self.points[i]) * self.elasticity
            
            # Apply deformation based on velocity
            deform_factor = 0.2
            vel_deform = pygame.Vector2(
                -self.velocity.x * deform_factor,
                -self.velocity.y * deform_factor
            )
            
            # Add deformation from collision
            if self.last_collision and self.collision_timer > 0:
                collision_force = self.last_collision * (self.collision_timer / 10) * -7
                dot_product = relative_pos.dot(self.last_collision)
                if dot_product > 0:
                    force += collision_force * dot_product / self.base_radius
            
            # Update velocity and position of each point
            self.point_velocities[i] += force + vel_deform
            self.point_velocities[i] *= self.damping
            self.points[i] += self.point_velocities[i]
            
        # Cycle colors
        self.color_timer += 1
        if self.color_timer > 10:
            self.color_timer = 0
            self.color_index = (self.color_index + 1) % len(COLORS)
    
    def draw(self, surface):
        # Draw the flexible blob
        if len(self.points) >= 3:
            pygame.draw.polygon(surface, COLORS[self.color_index], [(p.x, p.y) for p in self.points])
            
            # Draw highlight
            glow_color = (min(COLORS[self.color_index][0] + 50, 255), 
                        min(COLORS[self.color_index][1] + 50, 255), 
                        min(COLORS[self.color_index][2] + 50, 255))
            pygame.draw.circle(surface, glow_color, (int(self.position.x), int(self.position.y)), int(self.base_radius * 0.5))
            
    def check_ground_collision(self):
        # Check if any point of the blob is below the ground
        for point in self.points:
            if point.y > HEIGHT:
                return True
        return False
    
    def get_collision_rect(self):
        # Get bounding rectangle for collision detection
        min_x = min(point.x for point in self.points)
        min_y = min(point.y for point in self.points)
        max_x = max(point.x for point in self.points)
        max_y = max(point.y for point in self.points)
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

class Leg:
    def __init__(self):
        # Leg dimensions
        self.foot_length = 80  # Longer foot
        self.foot_height = 15
        self.calf_length = 140  # Longer calf
        self.calf_width = 20
        self.thigh_length = 160  # Longer thigh
        self.thigh_width = 25
        
        # Joint positions
        self.ankle_pos = pygame.Vector2(WIDTH // 2, HEIGHT - 50)
        self.knee_pos = pygame.Vector2(WIDTH // 2, HEIGHT - 150)
        self.hip_pos = pygame.Vector2(WIDTH // 2, HEIGHT - 270)  # Centered at the bottom of the screen
        
        # Colors
        self.foot_color = COLORS[2]
        self.calf_color = COLORS[3]
        self.thigh_color = COLORS[4]
        
    def update(self, mouse_pos):
        # Ankle directly follows mouse - this is what we want
        ankle_target = pygame.Vector2(mouse_pos[0], min(mouse_pos[1], HEIGHT - 20))
        
        # Calculate vector from hip to desired ankle position
        hip_to_ankle = ankle_target - self.hip_pos
        distance_to_ankle = hip_to_ankle.length()
        
        # Maximum possible leg extension
        max_extension = self.thigh_length + self.calf_length - 40  # Slightly more constraint for stability
        
        # If trying to extend beyond max length, constrain ankle position
        if distance_to_ankle > max_extension:
            hip_to_ankle.scale_to_length(max_extension)
            self.ankle_pos = self.hip_pos + hip_to_ankle
        else:
            # Ankle directly follows mouse if within range
            self.ankle_pos = ankle_target
        
        # Calculate knee position using triangulation method
        # We'll use the law of cosines to find the knee position that creates
        # proper thigh and calf lengths
        
        # First normalize the direction from hip to ankle
        if distance_to_ankle > 0:
            direction = hip_to_ankle / distance_to_ankle
        else:
            direction = pygame.Vector2(1, 0)  # Default direction if hip and ankle are at same position
            
        # Calculate the perpendicular direction for knee bend (always upward)
        perp = pygame.Vector2(-direction.y, direction.x)
        
        # We want the knee to always bend upward (negative y in pygame coordinates)
        if perp.y > 0:  # If the perpendicular vector points downward
            perp *= -1  # Flip it to point upward
            
        # Calculate distance from hip to knee (using law of cosines)
        # c^2 = a^2 + b^2 - 2ab*cos(C)
        # Where a = thigh_length, b = hip_ankle_distance, c = calf_length
        # Solving for cos(C) to find the angle
        
        a = self.thigh_length
        b = distance_to_ankle
        c = self.calf_length
        
        # Avoid degenerate case
        if b < 0.0001:
            # If ankle is very close to hip, just put knee somewhere reasonable
            self.knee_pos = self.hip_pos + pygame.Vector2(a/2, 0)
            return
            
        # Calculate cosine of angle between thigh and hip-ankle line using law of cosines
        cos_angle = (a*a + b*b - c*c) / (2*a*b)
        
        # Clamp to valid cosine range (-1 to 1) to avoid math errors
        cos_angle = max(-0.99, min(0.99, cos_angle))
        
        # Get the angle
        angle = math.acos(cos_angle)
        
        # Calculate knee position at the calculated angle from hip
        # Determine rotation direction based on the cross product to ensure we rotate toward perp
        cross_z = direction.x * perp.y - direction.y * perp.x
        sign = 1 if cross_z > 0 else -1
        
        # Rotate direction vector by 'angle' toward perp
        knee_dir_x = direction.x * math.cos(angle * sign) - direction.y * math.sin(angle * sign)
        knee_dir_y = direction.x * math.sin(angle * sign) + direction.y * math.cos(angle * sign)
        
        # Apply the calculated direction and thigh length to get knee position
        self.knee_pos = self.hip_pos + pygame.Vector2(knee_dir_x, knee_dir_y) * self.thigh_length
        
    def draw(self, surface):
        # Draw thigh
        self.draw_limb(surface, self.hip_pos, self.knee_pos, self.thigh_width, self.thigh_color)
        
        # Draw calf
        self.draw_limb(surface, self.knee_pos, self.ankle_pos, self.calf_width, self.calf_color)
        
        # Draw foot
        foot_angle = math.atan2(0, self.foot_length)  # Foot is horizontal
        foot_end = (self.ankle_pos.x + self.foot_length, self.ankle_pos.y)
        self.draw_limb(surface, self.ankle_pos, foot_end, self.foot_height, self.foot_color)
        
        # Draw joints
        pygame.draw.circle(surface, (255, 255, 255), (int(self.hip_pos.x), int(self.hip_pos.y)), 8)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.knee_pos.x), int(self.knee_pos.y)), 6)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.ankle_pos.x), int(self.ankle_pos.y)), 5)
        
    def draw_limb(self, surface, start_pos, end_pos, width, color):
        # Calculate angle of the limb
        angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
        
        # Calculate corners of rectangle
        length = pygame.Vector2(start_pos).distance_to(end_pos)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        
        # Four corners of rectangle
        p1 = (start_pos[0] - width/2 * sin_a, start_pos[1] + width/2 * cos_a)
        p2 = (start_pos[0] + width/2 * sin_a, start_pos[1] - width/2 * cos_a)
        p3 = (end_pos[0] + width/2 * sin_a, end_pos[1] - width/2 * cos_a)
        p4 = (end_pos[0] - width/2 * sin_a, end_pos[1] + width/2 * cos_a)
        
        pygame.draw.polygon(surface, color, [p1, p2, p3, p4])
        
    def check_footbag_collision(self, footbag):
        # Check collision with foot
        foot_end = (self.ankle_pos.x + self.foot_length, self.ankle_pos.y)
        foot_rect = pygame.Rect(
            self.ankle_pos.x, 
            self.ankle_pos.y - self.foot_height/2,
            self.foot_length,
            self.foot_height
        )
        
        # Inflate rect slightly for better collision detection
        foot_rect.inflate_ip(5, 5)
        
        # Get the bounding rect for the blob
        footbag_rect = footbag.get_collision_rect()
        
        if foot_rect.colliderect(footbag_rect):
            # Calculate bounce direction and velocity
            bounce_direction = pygame.Vector2(footbag.position) - pygame.Vector2(
                (self.ankle_pos.x + foot_end[0]) / 2, 
                self.ankle_pos.y
            )
            bounce_direction.normalize_ip()
            
            # Bounce velocity depends on the leg's movement speed, with reduced bounciness
            leg_velocity = pygame.Vector2(pygame.mouse.get_rel()) * 0.15  # Reduced multiplier
            bounce_speed = max(6, leg_velocity.length() + 4)  # Reduced base speed
            
            # Apply force and set collision for deformation effect
            footbag.velocity = bounce_direction * bounce_speed
            footbag.last_collision = -bounce_direction  # Direction of impact
            footbag.collision_timer = 10
            
            # Add some random spin to make it more interesting
            for i in range(footbag.num_points):
                footbag.point_velocities[i] += pygame.Vector2(
                    random.uniform(-1, 1),
                    random.uniform(-1, 1)
                )
            
            return True
            
        # Check calf collision with blob points
        calf_line = (self.knee_pos, self.ankle_pos)
        if self.polygon_line_collision(calf_line, footbag.points):
            # Bounce off calf with reduced bounciness
            bounce_direction = pygame.Vector2(footbag.position) - pygame.Vector2(
                (self.knee_pos.x + self.ankle_pos.x) / 2, 
                (self.knee_pos.y + self.ankle_pos.y) / 2
            )
            bounce_direction.normalize_ip()
            
            # Apply force and set collision for deformation effect
            footbag.velocity = bounce_direction * 6  # Reduced bounce speed
            footbag.last_collision = -bounce_direction  # Direction of impact
            footbag.collision_timer = 8
            
            # Add some random spin to make it more interesting
            for i in range(footbag.num_points):
                footbag.point_velocities[i] += pygame.Vector2(
                    random.uniform(-1, 1),
                    random.uniform(-1, 1)
                )
                
            return True
            
        return False
    
    def line_circle_collision(self, line, circle_pos, circle_radius):
        # Simplified line-circle collision detection
        x1, y1 = line[0]
        x2, y2 = line[1]
        cx, cy = circle_pos
        
        # Vector from line start to circle center
        dx = cx - x1
        dy = cy - y1
        
        # Vector representing the line
        line_vec_x = x2 - x1
        line_vec_y = y2 - y1
        
        # Length of line
        line_length = math.sqrt(line_vec_x**2 + line_vec_y**2)
        
        # Normalize line vector
        if line_length > 0:
            line_vec_x /= line_length
            line_vec_y /= line_length
        
        # Project circle center onto line
        projection = dx * line_vec_x + dy * line_vec_y
        
        # Clamp projection to line segment
        projection = max(0, min(line_length, projection))
        
        # Closest point on line to circle center
        closest_x = x1 + projection * line_vec_x
        closest_y = y1 + projection * line_vec_y
        
        # Distance from closest point to circle center
        distance = math.sqrt((cx - closest_x)**2 + (cy - closest_y)**2)
        
        return distance <= circle_radius
        
    def polygon_line_collision(self, line, polygon_points):
        """Check if any of the polygon points are near enough to the line"""
        line_start, line_end = line
        line_vec = pygame.Vector2(line_end) - pygame.Vector2(line_start)
        line_length = line_vec.length()
        
        if line_length == 0:
            return False
            
        line_dir = line_vec / line_length
        
        # Check each point's distance to the line
        for point in polygon_points:
            point_to_start = pygame.Vector2(point) - pygame.Vector2(line_start)
            projection = point_to_start.dot(line_dir)
            
            # Clamp projection to line segment
            projection = max(0, min(line_length, projection))
            
            # Get closest point on line
            closest_point = pygame.Vector2(line_start) + line_dir * projection
            
            # Check distance
            distance = (pygame.Vector2(point) - closest_point).length()
            if distance <= self.calf_width / 2 + 5:  # Half width plus a little buffer
                return True
                
        return False

class Game:
    def __init__(self):
        self.leg = Leg()
        self.footbag = Footbag()
        self.running = True
        self.score = 0
        self.font = pygame.font.Font(None, 48)
        
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
        
    def draw(self):
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
            
        # Draw objects
        self.leg.draw(screen)
        self.footbag.draw(screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
        
    def game_over_screen(self):
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
        
    def run(self):
        clock = pygame.time.Clock()
        
        # Main game loop
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)
            
        # Game over
        self.game_over_screen()


# Create and run game
if __name__ == "__main__":
    # Hide mouse cursor
    pygame.mouse.set_visible(False)
    
    # Enable mouse motion tracking for velocity calculations
    pygame.event.set_grab(True)
    
    game = Game()
    
    while True:
        game.run()
