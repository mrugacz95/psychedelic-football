import pygame
import math
import random
from src.constants import WIDTH, HEIGHT, COLORS

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
