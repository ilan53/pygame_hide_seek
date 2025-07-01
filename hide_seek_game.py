import pygame
import sys
import random
import heapq
import math
from enum import Enum

pygame.init()
pygame.mixer.init()

GRID_SIZE = 8
CELL_SIZE = 60
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
WINDOW_WIDTH = WIDTH + 400
WINDOW_HEIGHT = HEIGHT + 200
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
LIGHT_GREEN = (180, 255, 230) 
RED = (255, 0, 0)
ORANGE = (255, 165, 0)

# --- Center the grid in the window ---
GRID_OFFSET_X = (WINDOW_WIDTH - WIDTH) // 3
GRID_OFFSET_Y = 120  # Slightly more space for buttons above

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
FONT = pygame.font.SysFont("Segoe UI Emoji", 28)

class GameState(Enum):
    MENU = 1
    PLAYER1_TURN = 2
    PLAYER2_TURN = 3
    GAME_OVER = 4

class HideSeekGame:
    def __init__(self):
        self.stars = [
            {
                "x": random.randint(0, WINDOW_WIDTH),
                "y": random.randint(0, WINDOW_HEIGHT),
                "size": random.randint(2, 5),
                "speed": random.uniform(0.3, 0.8),
                "color": random.choice([(255,255,255), (255,230,200), (200,220,255), (255,255,180)]),
                "alpha": random.randint(100, 255),
                "alpha_direction": random.choice([-1, 1])
            }
            for _ in range(60)
        ]
        self.main_menu_button = None
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        self.game_mode = None  # 'pvc' or 'pvp'
        self.next_round_button = None
        self.move_target_button = None
        self.computer_thinking = False
        self.computer_think_time = 0
        self.player1_moved_target = False
        self.player2_moved_target = False
        
        # Block system variables
        self.blocks = []  # List of block positions and orientations
        self.player1_blocks_remaining = 1
        self.player2_blocks_remaining = 1
        self.place_block_button = None
        self.block_placement_mode = False
        self.block_orientation = "horizontal"  # "horizontal" or "vertical"
        # Block preview variables
        self.block_preview_pos = None  # (x, y) position for preview
        self.block_preview_valid = False  # Whether the preview position is valid

        self.tom_images = {
            "up": pygame.image.load("tom/tom_walking_up.png"),
            "down": pygame.image.load("tom/tom_walking_down.png"),
            "left": pygame.image.load("tom/tom_walking_left.png"),
            "right": pygame.image.load("tom/tom_walking_right.png"),
            "idle": pygame.image.load("tom/tom_standing.png"),
        }
        for key in self.tom_images:
            self.tom_images[key] = pygame.transform.scale(self.tom_images[key], (CELL_SIZE, CELL_SIZE))
        self.tom_direction = "idle"

        self.spike_images = {
            "up": pygame.image.load("spike/spike_walking_up.png"),
            "down": pygame.image.load("spike/spike_walking_down.png"),
            "left": pygame.image.load("spike/spike_walking_left.png"),
            "right": pygame.image.load("spike/spike_walking_right.png"),
            "idle": pygame.image.load("spike/spike_standing.png"),
        }
        for key in self.spike_images:
            self.spike_images[key] = pygame.transform.scale(self.spike_images[key], (CELL_SIZE, CELL_SIZE))
        self.spike_direction = "idle"

        # Load block images
        self.block_horizontal = pygame.transform.scale(pygame.image.load("assets/block_horizontal.png"), (CELL_SIZE * 2, CELL_SIZE))
        self.block_vertical = pygame.transform.scale(pygame.image.load("assets/block_vertical.png"), (CELL_SIZE, CELL_SIZE * 2))

        # Load cheese wedge image for hiding spots
        self.cheese_image = pygame.transform.scale(pygame.image.load("assets/Cheese-wedge.png"), (CELL_SIZE, CELL_SIZE))

        self.jerry_image = pygame.transform.scale(pygame.image.load("jerry/jerry_hiding2.png"), (CELL_SIZE, CELL_SIZE))


        self.feedback_images = {
            "FOUND": pygame.image.load("feed_back/found.png"),
            "BURNING": pygame.image.load("feed_back/burning_hot.png"),
            "HOT": pygame.image.load("feed_back/hot.png"),
            "WARM": pygame.image.load("feed_back/warm.png"),
            "COOL": pygame.image.load("feed_back/cool.png"),
            "COLD": pygame.image.load("feed_back/cold.png")
        }
        for key in self.feedback_images:
            self.feedback_images[key] = pygame.transform.scale(self.feedback_images[key], (180, 180))

        self.state = GameState.MENU
        self.seeker1_pos = (0, 0)
        self.seeker2_pos = (7, 7)
        self.hidden_pos = None
        self.feedback_text = ""
        self.winner = None
        self.hiding_spots = []
        self.generate_hiding_spots()

    def show_title_screen(self):
        background = pygame.image.load("assets/title_screen.png")
        background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

        button_color = (255, 200, 0)
        button_rect_pvc = pygame.Rect(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT - 180, 240, 50)
        button_rect_pvp = pygame.Rect(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT - 110, 240, 50)

        running_title = True
        while running_title:
            screen.blit(background, (0, 0))

            # Draw buttons
            pygame.draw.rect(screen, button_color, button_rect_pvc)
            pygame.draw.rect(screen, button_color, button_rect_pvp)
            start_text_pvc = FONT.render("Player vs Computer", True, (0, 0, 0))
            start_text_pvp = FONT.render("Player vs Player", True, (0, 0, 0))
            screen.blit(start_text_pvc, start_text_pvc.get_rect(center=button_rect_pvc.center))
            screen.blit(start_text_pvp, start_text_pvp.get_rect(center=button_rect_pvp.center))

            # Instructions
            instructions = [
                "🎮 Choose a mode:",
                "Player vs Computer: Tom (You) vs Spike (Computer)",
                "Player vs Player: Tom (Player 1) vs Spike (Player 2)",
                "🐭 Jerry hides randomly each game,",
                "You have to find him first!",
                "🔥 Hot = close | ❄️ Cold = far"
            ]
            for i, line in enumerate(instructions):
                instr = FONT.render(line, True, (0, 0, 0))
                instr_rect = instr.get_rect(center=(WINDOW_WIDTH // 2, 60 + i * 32))
                screen.blit(instr, instr_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect_pvc.collidepoint(event.pos):
                        self.game_mode = 'pvc'
                        running_title = False
                        self.start_game()
                    elif button_rect_pvp.collidepoint(event.pos):
                        self.game_mode = 'pvp'
                        running_title = False
                        self.start_game()

    def generate_hiding_spots(self):
        self.hiding_spots = []
        # Define starting positions that should be excluded
        excluded_positions = [(0, 0), (7, 7)]  # Tom's and Spike's starting positions
        
        for _ in range(random.randint(6, 8)):
            while True:
                pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
                if pos not in self.hiding_spots and pos not in excluded_positions:
                    self.hiding_spots.append(pos)
                    break

    def is_position_blocked(self, pos):
        """Check if a position is blocked by any block"""
        x, y = pos
        for block in self.blocks:
            block_x, block_y, orientation = block
            if orientation == "horizontal":
                if x == block_x and y == block_y or x == block_x and y == block_y + 1:
                    return True
            else:  # vertical
                if x == block_x and y == block_y or x == block_x + 1 and y == block_y:
                    return True
        return False

    def can_place_block(self, x, y, orientation):
        """Check if a block can be placed at the given position and orientation"""
        if orientation == "horizontal":
            # Check if both cells are within bounds
            if y + 1 >= GRID_SIZE:
                return False
            # Check if either cell is blocked
            if self.is_position_blocked((x, y)) or self.is_position_blocked((x, y + 1)):
                return False
            # Check if either cell is occupied by a player
            if (x, y) == self.seeker1_pos or (x, y) == self.seeker2_pos:
                return False
            if (x, y + 1) == self.seeker1_pos or (x, y + 1) == self.seeker2_pos:
                return False
            # Check if either cell is a hiding spot
            if (x, y) in self.hiding_spots or (x, y + 1) in self.hiding_spots:
                return False
        else:  # vertical
            # Check if both cells are within bounds
            if x + 1 >= GRID_SIZE:
                return False
            # Check if either cell is blocked
            if self.is_position_blocked((x, y)) or self.is_position_blocked((x + 1, y)):
                return False
            # Check if either cell is occupied by a player
            if (x, y) == self.seeker1_pos or (x, y) == self.seeker2_pos:
                return False
            if (x + 1, y) == self.seeker1_pos or (x + 1, y) == self.seeker2_pos:
                return False
            # Check if either cell is a hiding spot
            if (x, y) in self.hiding_spots or (x + 1, y) in self.hiding_spots:
                return False
        return True

    def place_block(self, x, y, orientation, player):
        """Place a block at the given position and orientation"""
        if self.can_place_block(x, y, orientation):
            self.blocks.append((x, y, orientation))
            if player == 1:
                self.player1_blocks_remaining -= 1
            else:
                self.player2_blocks_remaining -= 1
            return True
        return False

    def a_star_distance(self, start, goal):
        if start == goal:
            return 0
        open_set = [(0, start)]
        g_score = {start: 0}
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                return g_score[current]
            for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                neighbor = (current[0]+dx, current[1]+dy)
                if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE:
                    # Check if the neighbor position is blocked
                    if self.is_position_blocked(neighbor):
                        continue
                    temp = g_score[current] + 1
                    if neighbor not in g_score or temp < g_score[neighbor]:
                        g_score[neighbor] = temp
                        f = temp + abs(neighbor[0]-goal[0]) + abs(neighbor[1]-goal[1])
                        heapq.heappush(open_set, (f, neighbor))
        return float('inf')

    def get_feedback(self, distance):
        if distance == 0:
            return "FOUND"
        elif distance <= 2:
            return "BURNING"
        elif distance <= 4:
            return "HOT"
        elif distance <= 6:
            return "WARM"
        elif distance <= 10:
            return "COOL"
        return "COLD"

    def computer_move(self):
        # First, decide if computer should use Move Target button
        if not self.player2_moved_target:
            # Computer uses Move Target if it's far from Jerry and player is closer
            computer_dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
            player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
            
            # Use Move Target if computer is far and player is getting close
            if computer_dist > 6 and player_dist <= 4:
                self.move_target_to_new_location()
                self.player2_moved_target = True
                self.state = GameState.PLAYER1_TURN
                return
        
        # Decide whether to place a block or move
        player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
        computer_dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
        
        # Place block if player is close to Jerry and computer has blocks remaining
        if (player_dist <= 3 and computer_dist > player_dist and 
            self.player2_blocks_remaining > 0 and random.random() < 0.7):
            if self.computer_place_block():
                self.state = GameState.PLAYER1_TURN
                return
        
        # Regular movement logic
        best_move = None
        best_score = float('inf')
        x, y = self.seeker2_pos
        
        # Consider both distance to Jerry and blocking player's path
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                # Check if the move is blocked
                if self.is_position_blocked((nx, ny)):
                    continue
                    
                d = self.a_star_distance((nx, ny), self.hidden_pos)
                
                # Bonus score for moving towards Jerry
                score = d
                
                # Consider blocking player's path if player is close to Jerry
                player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                if player_dist <= 3:
                    # Try to get closer to Jerry to compete
                    score = d * 0.8  # Prioritize getting to Jerry
                
                if score < best_score:
                    best_score = score
                    best_move = (nx, ny)
        
        if best_move:
            dx = best_move[0] - self.seeker2_pos[0]
            dy = best_move[1] - self.seeker2_pos[1]
            if dx == -1:
                self.spike_direction = "up"
            elif dx == 1:
                self.spike_direction = "down"
            elif dy == -1:
                self.spike_direction = "left"
            elif dy == 1:
                self.spike_direction = "right"
            else:
                self.spike_direction = "idle"

            self.seeker2_pos = best_move
            if self.seeker2_pos == self.hidden_pos:
                self.winner = "Computer"
                pygame.mixer.music.stop()
                pygame.mixer.music.load("sound_track/lose.mp3")
                pygame.mixer.music.play()
                self.state = GameState.GAME_OVER
            else:
                self.state = GameState.PLAYER1_TURN

    def draw_grid(self):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(GRID_OFFSET_X + y * CELL_SIZE, GRID_OFFSET_Y + x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                # pygame.draw.rect(screen, WHITE, rect)  # Removed to make background transparent
                pygame.draw.rect(screen, BLACK, rect, 2)
        
        # Draw cheese wedges for hiding spots (but not where players are standing)
        for x, y in self.hiding_spots:
            # Only draw cheese if no player is on this spot
            if (x, y) != self.seeker1_pos and (x, y) != self.seeker2_pos:
                rect = pygame.Rect(GRID_OFFSET_X + y * CELL_SIZE, GRID_OFFSET_Y + x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                screen.blit(self.cheese_image, rect.topleft)
        
        # Draw player images (this will be on top of cheese if they're on a hiding spot)
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(GRID_OFFSET_X + y * CELL_SIZE, GRID_OFFSET_Y + x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (x, y) == self.seeker1_pos:
                    screen.blit(self.tom_images[self.tom_direction], rect.topleft)
                elif (x, y) == self.seeker2_pos:
                   screen.blit(self.spike_images[self.spike_direction], rect.topleft)
                if self.state == GameState.GAME_OVER and (x, y) == self.hidden_pos:
                    screen.blit(self.jerry_image, rect.topleft)
        
        # Draw blocks
        for block in self.blocks:
            x, y, orientation = block
            if orientation == "horizontal":
                block_rect = pygame.Rect(GRID_OFFSET_X + y * CELL_SIZE, GRID_OFFSET_Y + x * CELL_SIZE, CELL_SIZE * 2, CELL_SIZE)
                screen.blit(self.block_horizontal, block_rect.topleft)
            else:  # vertical
                block_rect = pygame.Rect(GRID_OFFSET_X + y * CELL_SIZE, GRID_OFFSET_Y + x * CELL_SIZE, CELL_SIZE, CELL_SIZE * 2)
                screen.blit(self.block_vertical, block_rect.topleft)
        
        # Draw block preview
        if self.block_placement_mode and self.block_preview_pos is not None:
            x, y = self.block_preview_pos
            preview_color = GREEN if self.block_preview_valid else RED
            
            if self.block_orientation == "horizontal":
                # Draw preview rectangle for horizontal block
                preview_rect = pygame.Rect(GRID_OFFSET_X + y * CELL_SIZE, GRID_OFFSET_Y + x * CELL_SIZE, CELL_SIZE * 2, CELL_SIZE)
                pygame.draw.rect(screen, preview_color, preview_rect, 3)
                # Draw semi-transparent overlay
                preview_surface = pygame.Surface((CELL_SIZE * 2, CELL_SIZE))
                preview_surface.set_alpha(100)
                preview_surface.fill(preview_color)
                screen.blit(preview_surface, preview_rect.topleft)
            else:  # vertical
                # Draw preview rectangle for vertical block
                preview_rect = pygame.Rect(GRID_OFFSET_X + y * CELL_SIZE, GRID_OFFSET_Y + x * CELL_SIZE, CELL_SIZE, CELL_SIZE * 2)
                pygame.draw.rect(screen, preview_color, preview_rect, 3)
                # Draw semi-transparent overlay
                preview_surface = pygame.Surface((CELL_SIZE, CELL_SIZE * 2))
                preview_surface.set_alpha(100)
                preview_surface.fill(preview_color)
                screen.blit(preview_surface, preview_rect.topleft)

    def draw_animated_background(self):
        screen.fill((230, 230, 255))  
        for star in self.stars:
            star["y"] -= star["speed"]
            star["size"] += 0.015
            star["alpha"] += star["alpha_direction"] * 2
            if star["alpha"] > 255:
                star["alpha"] = 255
                star["alpha_direction"] = -1
            elif star["alpha"] < 80:
                star["alpha"] = 80
                star["alpha_direction"] = 1
            if star["y"] < 0:
                star["x"] = random.randint(0, WINDOW_WIDTH)
                star["y"] = WINDOW_HEIGHT + random.randint(0, 100)
                star["size"] = random.randint(2, 4)
                star["speed"] = random.uniform(0.3, 0.8)
                star["color"] = random.choice([(255,255,255), (255,230,200), (200,220,255), (255,255,180)])

            surface = pygame.Surface((int(star["size"]*2), int(star["size"]*2)), pygame.SRCALPHA)
            pygame.draw.circle(surface, star["color"] + (int(star["alpha"]),), (int(star["size"]), int(star["size"])), int(star["size"]))
            screen.blit(surface, (int(star["x"] - star["size"]), int(star["y"] - star["size"])))

    def draw_ui(self):
        # Place Main Menu and Next Round buttons in the same row at the top, with smaller padding
        button_y = 24
        button_width = 160
        button_height = 38
        button_spacing = 12
        # Main Menu button (leftmost)
        self.main_menu_button = pygame.Rect(24, button_y, button_width, button_height)
        pygame.draw.rect(screen, (200, 200, 255), self.main_menu_button)
        menu_text = self.font.render("Main Menu", True, (0, 0, 0))
        menu_rect = menu_text.get_rect(center=self.main_menu_button.center)
        screen.blit(menu_text, menu_rect)
        # Next Round button (to the right of Main Menu), only show if game is over
        if self.state == GameState.GAME_OVER:
            self.next_round_button = pygame.Rect(24 + button_width + button_spacing, button_y, button_width, button_height)
            pygame.draw.rect(screen, (255, 200, 0), self.next_round_button)
            next_text = self.font.render("Next Round", True, (0, 0, 0))
            next_rect = next_text.get_rect(center=self.next_round_button.center)
            screen.blit(next_text, next_rect)
        else:
            self.next_round_button = None

        # --- Move side text and action buttons to the right side ---
        ui_x = WINDOW_WIDTH - 220
        ui_y = 80
        line_height = 32
        if self.state == GameState.PLAYER1_TURN or self.state == GameState.PLAYER2_TURN:
            # Show distance to Jerry for both players
            if self.hidden_pos is not None:
                dist1 = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                dist2 = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
                screen.blit(self.font.render(f"Tom -> Jerry: {dist1} steps", True, BLACK), (ui_x, ui_y))
                screen.blit(self.font.render(f"Spike -> Jerry: {dist2} steps", True, BLACK), (ui_x, ui_y + line_height))
            screen.blit(self.font.render(f"Tom blocks: {self.player1_blocks_remaining}", True, BLACK), (ui_x, ui_y + 2 * line_height))
            screen.blit(self.font.render(f"Spike blocks: {self.player2_blocks_remaining}", True, BLACK), (ui_x, ui_y + 3 * line_height))
            # Show computer thinking indicator
            if self.state == GameState.PLAYER2_TURN and self.game_mode != 'pvp':
                screen.blit(self.font.render("Computer is thinking...", True, (255, 200, 0)), (ui_x, ui_y + 4 * line_height))
                if not self.player2_moved_target:
                    screen.blit(self.font.render("(Can use Move Target)", True, (160, 32, 240)), (ui_x, ui_y + 5 * line_height))
            # Draw Move Target button for current player if they haven't used it
            action_y = ui_y + 6 * line_height
            if self.state == GameState.PLAYER1_TURN and not self.player1_moved_target:
                self.move_target_button = pygame.Rect(ui_x, action_y, 180, 36)
                pygame.draw.rect(screen, (255, 200, 0), self.move_target_button, border_radius=8)
                pygame.draw.rect(screen, BLACK, self.move_target_button, 3, border_radius=8)

                move_text = self.font.render("Move Target (Tom)", True, (0, 0, 0))
                move_rect = move_text.get_rect(center=self.move_target_button.center)
                screen.blit(move_text, move_rect)
                action_y += 44
            elif self.state == GameState.PLAYER2_TURN and not self.player2_moved_target and self.game_mode == 'pvp':
                self.move_target_button = pygame.Rect(ui_x, action_y, 180, 36)
                pygame.draw.rect(screen, (200, 100, 100), self.move_target_button)
                move_text = self.font.render("Move Target (Spike)", True, (0, 0, 0))
                move_rect = move_text.get_rect(center=self.move_target_button.center)
                screen.blit(move_text, move_rect)
                action_y += 44
            else:
                self.move_target_button = None
            # Draw Place Block button for current player if they have blocks remaining
            current_player = 1 if self.state == GameState.PLAYER1_TURN else 2
            blocks_remaining = self.player1_blocks_remaining if current_player == 1 else self.player2_blocks_remaining
            if blocks_remaining > 0:
                self.place_block_button = pygame.Rect(ui_x, action_y, 180, 36)
                button_color = (100, 150, 200) if current_player == 1 else (200, 100, 150)
                pygame.draw.rect(screen, (160, 32, 240), self.place_block_button, border_radius=8)
                pygame.draw.rect(screen, BLACK, self.place_block_button, 3, border_radius=8)

                player_name = "Tom" if current_player == 1 else "Spike"
                block_text = self.font.render(f"Place Block ({player_name})", True, (0, 0, 0))
                block_rect = block_text.get_rect(center=self.place_block_button.center)
                screen.blit(block_text, block_rect)
                # Show current block orientation
                orientation_text = self.font.render(f"Orientation: {self.block_orientation}", True, BLACK)
                screen.blit(orientation_text, (ui_x, action_y + 40))
                screen.blit(self.font.render("Press 'R' to rotate", True, BLACK), (ui_x, action_y + 60))
                # Show block placement instructions
                if self.block_placement_mode:
                    screen.blit(self.font.render("Click on grid to place block", True, (160, 32, 240)), (ui_x, action_y + 80))
                    if self.block_preview_valid:
                        screen.blit(self.font.render("Green = Valid placement", True, GREEN), (ui_x, action_y + 100))
                    else:
                        screen.blit(self.font.render("Red = Invalid placement", True, RED), (ui_x, action_y + 100))
            else:
                self.place_block_button = None
        # Feedback image and game over text remain on the right
        if self.feedback_text in self.feedback_images:
            screen.blit(self.feedback_images[self.feedback_text], (ui_x, WINDOW_HEIGHT - 240))
        elif self.state == GameState.GAME_OVER:
            screen.blit(self.big_font.render(f"{self.winner} Wins!", True, BLACK), (ui_x, 50))
            screen.blit(self.font.render("Press any key to restart", True, BLACK), (ui_x, 100))

        # Allow clicking main menu anytime
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] and self.main_menu_button.collidepoint(pygame.mouse.get_pos()):
            pygame.mixer.music.stop()
            self.state = GameState.MENU
            self.show_title_screen()

    def move_target_to_new_location(self):
        """Move Jerry to a new random hiding location"""
        if self.hiding_spots:
            # Choose a new location different from current
            new_pos = random.choice(self.hiding_spots)
            while new_pos == self.hidden_pos and len(self.hiding_spots) > 1:
                new_pos = random.choice(self.hiding_spots)
            self.hidden_pos = new_pos
            # Update feedback for current player
            if self.state == GameState.PLAYER1_TURN:
                dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                self.feedback_text = self.get_feedback(dist)
            elif self.state == GameState.PLAYER2_TURN:
                dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
                self.feedback_text = self.get_feedback(dist)

    def start_game(self):
        pygame.mixer.music.load("sound_track/backgroud_music.mp3")
        pygame.mixer.music.play(-1) 
        self.generate_hiding_spots()
        self.hidden_pos = random.choice(self.hiding_spots)
        self.seeker1_pos = (0, 0)
        self.seeker2_pos = (7, 7)
        self.feedback_text = ""
        self.winner = None
        self.tom_direction = "idle"
        self.spike_direction = "idle"
        self.state = GameState.PLAYER1_TURN
        self.player1_moved_target = False
        self.player2_moved_target = False
        # Reset block system
        self.blocks = []
        self.player1_blocks_remaining = 1
        self.player2_blocks_remaining = 1
        self.block_placement_mode = False
        self.block_orientation = "horizontal"
        self.block_preview_pos = None
        self.block_preview_valid = False

    def computer_place_block(self):
        """Computer places a block strategically to interfere with player's path"""
        if self.player2_blocks_remaining <= 0:
            return False
            
        player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
        computer_dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
        
        # Only place block if player is closer to Jerry than computer
        if player_dist >= computer_dist:
            return False
        
        # Try to block the player's path
        best_block = None
        best_impact = 0
        
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                # Try horizontal block
                if self.can_place_block(x, y, "horizontal"):
                    # Check if this block would block the player's path
                    old_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    
                    # Temporarily place block
                    self.blocks.append((x, y, "horizontal"))
                    new_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    self.blocks.pop()  # Remove temporary block
                    
                    # Calculate impact (how much it increases player's path)
                    impact = new_dist - old_dist
                    if impact > best_impact and new_dist != float('inf'):
                        best_impact = impact
                        best_block = (x, y, "horizontal")
                
                # Try vertical block
                if self.can_place_block(x, y, "vertical"):
                    # Check if this block would block the player's path
                    old_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    
                    # Temporarily place block
                    self.blocks.append((x, y, "vertical"))
                    new_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    self.blocks.pop()  # Remove temporary block
                    
                    # Calculate impact (how much it increases player's path)
                    impact = new_dist - old_dist
                    if impact > best_impact and new_dist != float('inf'):
                        best_impact = impact
                        best_block = (x, y, "vertical")
        
        # Place the best block if it has significant impact
        if best_block and best_impact >= 2:
            x, y, orientation = best_block
            self.place_block(x, y, orientation, 2)
            return True
        
        # If no good strategic block found, try to block near the player's current position
        if player_dist <= 3:
            for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                nx, ny = self.seeker1_pos[0] + dx, self.seeker1_pos[1] + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    # Try horizontal block near player
                    if self.can_place_block(nx, ny, "horizontal"):
                        self.place_block(nx, ny, "horizontal", 2)
                        return True
                    # Try vertical block near player
                    if self.can_place_block(nx, ny, "vertical"):
                        self.place_block(nx, ny, "vertical", 2)
                        return True
        
        return False

    def run(self):
        self.show_title_screen()
        running = True
        player_turn = 1  # 1 for Tom, 2 for Spike (in PvP)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == GameState.MENU or self.state == GameState.GAME_OVER:
                        self.start_game()
                        player_turn = 1
                    elif self.state == GameState.PLAYER1_TURN:
                        # Block rotation
                        if event.key == pygame.K_r:
                            self.block_orientation = "vertical" if self.block_orientation == "horizontal" else "horizontal"
                        # Movement with block checking
                        x, y = self.seeker1_pos
                        moved = False
                        if event.key == pygame.K_UP and x > 0:
                            new_pos = (x - 1, y)
                            if not self.is_position_blocked(new_pos):
                                self.seeker1_pos = new_pos
                                self.tom_direction = "up"
                                moved = True
                        elif event.key == pygame.K_DOWN and x < GRID_SIZE - 1:
                            new_pos = (x + 1, y)
                            if not self.is_position_blocked(new_pos):
                                self.seeker1_pos = new_pos
                                self.tom_direction = "down"
                                moved = True
                        elif event.key == pygame.K_LEFT and y > 0:
                            new_pos = (x, y - 1)
                            if not self.is_position_blocked(new_pos):
                                self.seeker1_pos = new_pos
                                self.tom_direction = "left"
                                moved = True
                        elif event.key == pygame.K_RIGHT and y < GRID_SIZE - 1:
                            new_pos = (x, y + 1)
                            if not self.is_position_blocked(new_pos):
                                self.seeker1_pos = new_pos
                                self.tom_direction = "right"
                                moved = True
                        if moved:
                            if self.seeker1_pos == self.hidden_pos:
                                self.winner = "Tom (Player 1)"
                                pygame.mixer.music.stop()
                                pygame.mixer.music.load("sound_track/win.wav")
                                pygame.mixer.music.play()
                                self.state = GameState.GAME_OVER
                            else:
                                dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                                self.feedback_text = self.get_feedback(dist)
                                if self.game_mode == 'pvp':
                                    self.state = GameState.PLAYER2_TURN
                                else:
                                    self.state = GameState.PLAYER2_TURN
                    elif self.state == GameState.PLAYER2_TURN:
                        if self.game_mode == 'pvp':
                            # Block rotation
                            if event.key == pygame.K_r:
                                self.block_orientation = "vertical" if self.block_orientation == "horizontal" else "horizontal"
                            # Movement with block checking
                            x, y = self.seeker2_pos
                            moved = False
                            if event.key == pygame.K_w and x > 0:
                                new_pos = (x - 1, y)
                                if not self.is_position_blocked(new_pos):
                                    self.seeker2_pos = new_pos
                                    self.spike_direction = "up"
                                    moved = True
                            elif event.key == pygame.K_s and x < GRID_SIZE - 1:
                                new_pos = (x + 1, y)
                                if not self.is_position_blocked(new_pos):
                                    self.seeker2_pos = new_pos
                                    self.spike_direction = "down"
                                    moved = True
                            elif event.key == pygame.K_a and y > 0:
                                new_pos = (x, y - 1)
                                if not self.is_position_blocked(new_pos):
                                    self.seeker2_pos = new_pos
                                    self.spike_direction = "left"
                                    moved = True
                            elif event.key == pygame.K_d and y < GRID_SIZE - 1:
                                new_pos = (x, y + 1)
                                if not self.is_position_blocked(new_pos):
                                    self.seeker2_pos = new_pos
                                    self.spike_direction = "right"
                                    moved = True
                            if moved:
                                if self.seeker2_pos == self.hidden_pos:
                                    self.winner = "Spike (Player 2)"
                                    pygame.mixer.music.stop()
                                    pygame.mixer.music.load("sound_track/lose.mp3")
                                    pygame.mixer.music.play()
                                    self.state = GameState.GAME_OVER
                                else:
                                    dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
                                    self.feedback_text = self.get_feedback(dist)
                                    self.state = GameState.PLAYER1_TURN
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if  self.next_round_button and self.next_round_button.collidepoint(event.pos):
                        self.start_game()
                        player_turn = 1
                    elif self.state == GameState.GAME_OVER and self.main_menu_button and self.main_menu_button.collidepoint(event.pos):
                        self.state = GameState.MENU
                        self.show_title_screen()    
                    elif self.move_target_button and self.move_target_button.collidepoint(event.pos):
                        if self.state == GameState.PLAYER1_TURN and not self.player1_moved_target:
                            self.move_target_to_new_location()
                            self.player1_moved_target = True
                            # End turn and switch to player 2
                            if self.game_mode == 'pvp':
                                self.state = GameState.PLAYER2_TURN
                            else:
                                self.state = GameState.PLAYER2_TURN
                        elif self.state == GameState.PLAYER2_TURN and not self.player2_moved_target:
                            self.move_target_to_new_location()
                            self.player2_moved_target = True
                            # End turn and switch to player 1
                            self.state = GameState.PLAYER1_TURN
                    elif self.place_block_button and self.place_block_button.collidepoint(event.pos):
                        # Enter block placement mode
                        self.block_placement_mode = True
                    elif self.block_placement_mode:
                        # Handle block placement
                        mouse_x, mouse_y = event.pos
                        if mouse_x >= GRID_OFFSET_X and mouse_y >= GRID_OFFSET_Y:  # Click is on the grid
                            grid_x = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE
                            grid_y = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
                            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                                current_player = 1 if self.state == GameState.PLAYER1_TURN else 2
                                if self.place_block(grid_x, grid_y, self.block_orientation, current_player):
                                    self.block_placement_mode = False
                                    self.block_preview_pos = None
                                    # End turn after placing block
                                    if self.game_mode == 'pvp':
                                        if self.state == GameState.PLAYER1_TURN:
                                            self.state = GameState.PLAYER2_TURN
                                        else:
                                            self.state = GameState.PLAYER1_TURN
                                    else:
                                        if self.state == GameState.PLAYER1_TURN:
                                            self.state = GameState.PLAYER2_TURN
                elif event.type == pygame.MOUSEMOTION:
                    # Update block preview position
                    if self.block_placement_mode:
                        mouse_x, mouse_y = event.pos
                        if mouse_x >= GRID_OFFSET_X and mouse_y >= GRID_OFFSET_Y:  # Mouse is on the grid
                            grid_x = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE
                            grid_y = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
                            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                                self.block_preview_pos = (grid_x, grid_y)
                                self.block_preview_valid = self.can_place_block(grid_x, grid_y, self.block_orientation)
                            else:
                                self.block_preview_pos = None
                        else:
                            self.block_preview_pos = None

            if self.state == GameState.PLAYER2_TURN and self.game_mode != 'pvp':
                if not self.computer_thinking:
                    self.computer_thinking = True
                    self.computer_think_time = pygame.time.get_ticks()
                elif pygame.time.get_ticks() - self.computer_think_time > 800:  # 800ms delay
                    self.computer_move()
                    self.computer_thinking = False

            screen.fill(LIGHT_GREEN)
            self.draw_animated_background()
            if self.state != GameState.MENU:
                self.draw_grid()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    HideSeekGame().run()
