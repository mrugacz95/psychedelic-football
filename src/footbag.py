import pygame
import math
import random
from src.constants import WIDTH, HEIGHT, COLORS

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
