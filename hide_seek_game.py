import pygame
import sys
import random
import heapq
import math
from enum import Enum

pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(0.5)

GRID_SIZE = 10
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
        self.computer_difficulty = "normal"  # 'normal' or 'hard'
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

        self.jerry_running_frames = [
            pygame.transform.scale(
                pygame.image.load(f"jerry/frame_{i:02d}_delay-0.08s.png"), 
                (CELL_SIZE, CELL_SIZE)
            )
            for i in range(14)  
        ]
        self.jerry_running_frame_index = 0
        self.jerry_running_frame_timer = 0
        self.jerry_running_frame_duration = 50  # milliseconds = 0.05s
        self.show_jerry_running = False
        self.jerry_running_pos = None
        self.jerry_running_start_time = 0


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
        self.seeker2_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.hidden_pos = None
        self.feedback_text = ""
        self.winner = None
        self.hiding_spots = []
        self.generate_hiding_spots()

        self.tutorial_image = pygame.image.load("assets/tutorial.png")
        self.tutorial_image = pygame.transform.scale(self.tutorial_image, (887, 426))

        self.player1_keys_image = pygame.image.load("assets/player1_keys.jfif")
        self.player1_keys_image = pygame.transform.scale(self.player1_keys_image, (160, 100))

        self.player2_keys_image = pygame.image.load("assets/player2_keys.jpg")
        self.player2_keys_image = pygame.transform.scale(self.player2_keys_image, (160, 100))

        self.FIND_JERRY_FIRST = pygame.image.load("assets/FIND_JERRY_FIRST.png")
        self.FIND_JERRY_FIRST = pygame.transform.scale(self.FIND_JERRY_FIRST, (160, 160))

        self.surprise_image = pygame.image.load("assets/surprise-gift.png")
        self.surprise_image = pygame.transform.scale(self.surprise_image, (160, 160))

        # --- Frozen images ---
        self.tom_frozen_image = pygame.transform.scale(pygame.image.load("tom/tom_frozen.png"), (CELL_SIZE, CELL_SIZE))
        self.spike_frozen_image = pygame.transform.scale(pygame.image.load("spike/spike_frozen.png"), (CELL_SIZE, CELL_SIZE))
        # If you have a tom frozen image, use: self.tom_frozen_image = pygame.transform.scale(pygame.image.load("tom/tom_frozen.png"), (CELL_SIZE, CELL_SIZE))

        # Freeze state
        self.player1_frozen_turns = 0
        self.player2_frozen_turns = 0
        # Unfreeze animation state
        self.player1_unfreezing = False
        self.player2_unfreezing = False
        self.player1_unfreeze_timer = 0
        self.player2_unfreeze_timer = 0
        self.unfreeze_anim_duration = 500  # ms
        self.unfreeze_anim_jitter = 6  # px

        # --- Gift Box Animation ---
        self.gift_box_frames = [
            pygame.transform.scale(
                pygame.image.load(f"suprise_box/on_board/frame_{i:03d}_delay-0.03s.gif"),
                (CELL_SIZE, CELL_SIZE)
            ) for i in range(45)
        ]
        self.gift_box_frame_index = 0
        self.gift_box_frame_timer = 0
        self.gift_box_frame_duration = 30  # ms per frame
        self.gift_box_location = None
        self.place_gift_box()

        # --- Gift Box Pop Animation ---
        self.gift_box_pop_frames = [
            pygame.transform.scale(
                pygame.image.load(f"suprise_box/take/frame_{i:03d}_delay-0.03s.gif"),
                (CELL_SIZE, CELL_SIZE)
            ) for i in range(114, 150)
        ]
        self.gift_box_popping = False
        self.gift_box_pop_frame_index = 0
        self.gift_box_pop_frame_timer = 0
        self.gift_box_pop_frame_duration = 25  # ms per frame (faster)
        self.gift_box_pop_position = None

        # --- Score tracking ---
        self.scores = {"Tom": 0, "Spike": 0, "Computer": 0}
        self.last_game_mode = None
        self.debug_message = None

    def show_title_screen(self):
        # Always reset scores and last_game_mode when entering main menu
        self.scores = {"Tom": 0, "Spike": 0, "Computer": 0}
        self.last_game_mode = None
        background = pygame.image.load("assets/title_screen.png")
        background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

        button_color = (255, 200, 0)
        button_rect_pvc = pygame.Rect(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT - 220, 240, 50)
        button_rect_pvp = pygame.Rect(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT - 150, 240, 50)
        button_rect_tutorial = pygame.Rect(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT - 80, 240, 40)

        # Difficulty selection UI
        radio_normal = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 300, 30, 30)
        radio_hard = pygame.Rect(WINDOW_WIDTH // 2 + 40, WINDOW_HEIGHT - 300, 30, 30)
        start_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT - 220, 160, 50)
        show_difficulty = False
        selected_difficulty = "normal"

        running_title = True
        while running_title:
            screen.blit(background, (0, 0))

            # Draw buttons
            if not show_difficulty:
                pygame.draw.rect(screen, button_color, button_rect_pvc)
                pygame.draw.rect(screen, button_color, button_rect_pvp)
                pygame.draw.rect(screen, button_color, button_rect_tutorial)
                start_text_pvc = FONT.render("Player vs Computer", True, (0, 0, 0))
                start_text_pvp = FONT.render("Player vs Player", True, (0, 0, 0))
                tutorial_text = FONT.render("Tutorial", True, (0, 0, 0))
                screen.blit(start_text_pvc, start_text_pvc.get_rect(center=button_rect_pvc.center))
                screen.blit(start_text_pvp, start_text_pvp.get_rect(center=button_rect_pvp.center))
                screen.blit(tutorial_text, tutorial_text.get_rect(center=button_rect_tutorial.center))
            else:
                # Draw difficulty selection background
                bg_rect = pygame.Rect(WINDOW_WIDTH // 2 - 170, WINDOW_HEIGHT - 360, 360, 200)
                pygame.draw.rect(screen, (245, 240, 255), bg_rect, border_radius=18)
                pygame.draw.rect(screen, (120, 120, 180), bg_rect, 4, border_radius=18)
                # Draw difficulty selection
                diff_label = FONT.render("Computer Difficulty:", True, (0, 0, 0))
                screen.blit(diff_label, (WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 340))
                # Radio buttons
                pygame.draw.circle(screen, BLACK, radio_normal.center, 15, 2)
                pygame.draw.circle(screen, BLACK, radio_hard.center, 15, 2)
                if selected_difficulty == "normal":
                    pygame.draw.circle(screen, (0, 200, 0), radio_normal.center, 9)
                else:
                    pygame.draw.circle(screen, (0, 200, 0), radio_hard.center, 9)
                normal_text = FONT.render("Normal", True, (0, 0, 0))
                hard_text = FONT.render("Hard", True, (0, 0, 0))
                screen.blit(normal_text, (radio_normal.right + 10, radio_normal.y - 2))
                screen.blit(hard_text, (radio_hard.right + 10, radio_hard.y - 2))
                # Start button
                pygame.draw.rect(screen, button_color, start_button_rect)
                start_text = FONT.render("Start", True, (0, 0, 0))
                screen.blit(start_text, start_text.get_rect(center=start_button_rect.center))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not show_difficulty:
                        if button_rect_pvc.collidepoint(event.pos):
                            show_difficulty = True
                        elif button_rect_pvp.collidepoint(event.pos):
                            self.game_mode = 'pvp'
                            running_title = False
                            self.start_game()
                        elif button_rect_tutorial.collidepoint(event.pos):
                            self.show_tutorial_screen()
                    else:
                        if radio_normal.collidepoint(event.pos):
                            selected_difficulty = "normal"
                        elif radio_hard.collidepoint(event.pos):
                            selected_difficulty = "hard"
                        elif start_button_rect.collidepoint(event.pos):
                            self.game_mode = 'pvc'
                            self.computer_difficulty = selected_difficulty
                            running_title = False
                            self.start_game()

    def show_tutorial_screen(self):
        running_tutorial = True
        button_width = 160
        button_height = 38
        button_x = 24
        button_y = 24
        self.main_menu_button = pygame.Rect(button_x, button_y, button_width, button_height)

        while running_tutorial:
            screen.fill((240, 240, 255))

            # כותרת
            title = self.big_font.render("Tutorial", True, BLACK)
            screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 30))

            # 🧠 הצגת תמונה ראשית במרכז
            tutorial_rect = self.tutorial_image.get_rect(center=(WINDOW_WIDTH // 2, 150 + self.tutorial_image.get_height() // 3.2))
            screen.blit(self.tutorial_image, tutorial_rect.topleft)

            # 🕹️ Player 1 keys – ימין למטה
            p1_x = WINDOW_WIDTH - 200
            p1_y = WINDOW_HEIGHT - 180
            screen.blit(self.player1_keys_image, (p1_x, p1_y))
            p1_text = self.font.render("Player 1", True, BLACK)
            screen.blit(p1_text, (p1_x + 40, p1_y + 110))

            # 🧀 Find Jerry First – באמצע בין השניים
            fjf_rect = self.FIND_JERRY_FIRST.get_rect(center=(WINDOW_WIDTH // 2, p1_y + 50))
            screen.blit(self.FIND_JERRY_FIRST, fjf_rect.topleft)

             # 📦 Surprise gift explanation image – מתחת לתמונה הראשית
            surprise_rect = self.surprise_image.get_rect(center=(105, tutorial_rect.bottom + -290))
            screen.blit(self.surprise_image, surprise_rect.topleft)

            # 🕹️ Player 2 keys – שמאל למטה
            p2_x = 60
            p2_y = WINDOW_HEIGHT - 180
            screen.blit(self.player2_keys_image, (p2_x, p2_y))
            p2_text = self.font.render("Player 2", True, BLACK)
            screen.blit(p2_text, (p2_x + 40, p2_y + 110))

            # 🔙 Main Menu button
            self.main_menu_button = pygame.Rect(button_x, button_y, button_width, button_height)
            pygame.draw.rect(screen, (200, 200, 255), self.main_menu_button, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.main_menu_button, 3, border_radius=8)
            menu_text = self.font.render("Main Menu", True, (0, 0, 0))
            screen.blit(menu_text, menu_text.get_rect(center=self.main_menu_button.center))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.main_menu_button.collidepoint(event.pos):
                        running_tutorial = False

    def place_gift_box(self):
        # Place the gift box at a random location not occupied by players or hiding spots
        excluded = [(0, 0), (GRID_SIZE-1, GRID_SIZE-1)] + self.hiding_spots
        while True:
            pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if pos not in excluded:
                self.gift_box_location = pos
                break

    def generate_hiding_spots(self):
        self.hiding_spots = []
        # Define starting positions that should be excluded
        excluded_positions = [(0, 0), (GRID_SIZE-1, GRID_SIZE-1)]  # Tom's and Spike's starting positions
        
        for _ in range(random.randint(8, 12)):
            while True:
                pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
                if pos not in self.hiding_spots and pos not in excluded_positions:
                    self.hiding_spots.append(pos)
                    break
        # After hiding spots are generated, place the gift box
        self.place_gift_box()

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
            # Prevent blocking a gift box
            if self.gift_box_location is not None:
                if (x, y) == self.gift_box_location or (x, y + 1) == self.gift_box_location:
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
            # Prevent blocking a gift box
            if self.gift_box_location is not None:
                if (x, y) == self.gift_box_location or (x + 1, y) == self.gift_box_location:
                    return False
        # Prevent trapping a hiding spot in a corner with two blocks
        # For each corner, if a hiding spot is there, check if this block would trap it
        corners = [(0,0), (0,GRID_SIZE-1), (GRID_SIZE-1,0), (GRID_SIZE-1,GRID_SIZE-1)]
        for hx, hy in self.hiding_spots:
            if (hx, hy) in corners:
                # For each corner, check the two adjacent cells
                if (hx, hy) == (0,0):
                    adj1 = (0,1)
                    adj2 = (1,0)
                elif (hx, hy) == (0,GRID_SIZE-1):
                    adj1 = (0,GRID_SIZE-2)
                    adj2 = (1,GRID_SIZE-1)
                elif (hx, hy) == (GRID_SIZE-1,0):
                    adj1 = (GRID_SIZE-2,0)
                    adj2 = (GRID_SIZE-1,1)
                elif (hx, hy) == (GRID_SIZE-1,GRID_SIZE-1):
                    adj1 = (GRID_SIZE-2,GRID_SIZE-1)
                    adj2 = (GRID_SIZE-1,GRID_SIZE-2)
                # If this block would block either adjacent cell, and the other is already blocked, disallow
                blocks_adj1 = self.is_position_blocked(adj1) or \
                    ((orientation == "horizontal" and (x, y) == adj1) or (orientation == "vertical" and (x, y) == adj1))
                blocks_adj2 = self.is_position_blocked(adj2) or \
                    ((orientation == "horizontal" and (x, y) == adj2) or (orientation == "vertical" and (x, y) == adj2))
                if blocks_adj1 and blocks_adj2:
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
        # Use difficulty to branch AI logic
        if self.computer_difficulty == "normal":
            # --- Move Target logic (same as hard mode) ---
            if not self.player2_moved_target:
                computer_dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
                player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                if computer_dist > 6 and player_dist <= 4:
                    self.move_target_to_new_location()
                    self.player2_moved_target = True
                    self.state = GameState.PLAYER1_TURN
                    return
            # --- Block placement logic (improved for normal mode) ---
            player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
            computer_dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
            
            # --- Gift box logic: go for the gift if it helps ---
            go_for_gift = False
            if self.gift_box_location:
                # Get path to gift and to Jerry
                path_to_gift = self.a_star_path(self.seeker2_pos, self.gift_box_location)
                path_to_jerry = self.a_star_path(self.seeker2_pos, self.hidden_pos)
                # If the gift is on the way to Jerry, or if freezing the player would let computer win
                player_path_to_jerry = self.a_star_path(self.seeker1_pos, self.hidden_pos)
                if self.gift_box_location in path_to_jerry:
                    go_for_gift = True
                else:
                    # If computer is behind, but freezing player would let it catch up or win
                    if player_dist < computer_dist and (computer_dist - player_dist) <= 2:
                        # Estimate: if player is frozen for 2 turns, computer can catch up
                        go_for_gift = True
            if go_for_gift:
                # Move toward the gift box
                path = self.a_star_path(self.seeker2_pos, self.gift_box_location)
                if len(path) > 1:
                    next_pos = path[1]
                    dx = next_pos[0] - self.seeker2_pos[0]
                    dy = next_pos[1] - self.seeker2_pos[1]
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
                    self.seeker2_pos = next_pos
                    # Trigger gift box animation and freeze opponent immediately
                    if self.seeker2_pos == self.gift_box_location:
                        self.gift_box_popping = True
                        self.gift_box_pop_position = self.gift_box_location
                        self.gift_box_pop_frame_index = 0
                        self.gift_box_pop_frame_timer = pygame.time.get_ticks()
                        self.gift_box_location = None
                        self.freeze_opponent(2)
                    self.state = GameState.PLAYER1_TURN
                    return
            # --- Block placement logic for normal mode ---
            should_place_block = False
            if player_dist <= 5 and computer_dist > player_dist:
                should_place_block = True
            elif player_dist <= 3:
                should_place_block = True
            elif player_dist < computer_dist:
                should_place_block = True

            if should_place_block and self.player2_blocks_remaining > 0 and random.random() < 0.5:  # 50% chance for normal mode
                if self.computer_place_block():
                    self.state = GameState.PLAYER1_TURN
                    return
            # --- Movement logic: feedback-based ---
            x, y = self.seeker2_pos
            feedback_distance = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
            prev_pos = getattr(self, '_prev_seeker2_pos', None)
            best_moves = []
            min_new_distance = feedback_distance
            for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if self.is_position_blocked((nx, ny)):
                        continue
                    new_distance = self.a_star_distance((nx, ny), self.hidden_pos)
                    if new_distance < min_new_distance:
                        min_new_distance = new_distance
                        best_moves = [(nx, ny)]
                    elif new_distance == min_new_distance:
                        best_moves.append((nx, ny))
            # Prefer moves that decrease the distance
            if best_moves and min_new_distance < feedback_distance:
                chosen_move = random.choice(best_moves)
            else:
                # If no move decreases the distance, allow moves that keep the same distance, but avoid going back to previous position
                same_dist_moves = []
                for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        if self.is_position_blocked((nx, ny)):
                            continue
                        if self.a_star_distance((nx, ny), self.hidden_pos) == feedback_distance:
                            if prev_pos is None or (nx, ny) != prev_pos:
                                same_dist_moves.append((nx, ny))
                if same_dist_moves:
                    chosen_move = random.choice(same_dist_moves)
                else:
                    # If stuck, just pick any valid move
                    valid_moves = []
                    for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                            if not self.is_position_blocked((nx, ny)):
                                valid_moves.append((nx, ny))
                    if valid_moves:
                        chosen_move = random.choice(valid_moves)
                    else:
                        chosen_move = (x, y)
            dx = chosen_move[0] - x
            dy = chosen_move[1] - y
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
            self._prev_seeker2_pos = self.seeker2_pos
            self.seeker2_pos = chosen_move
            if self.seeker2_pos == self.hidden_pos:
                self.winner = "Computer"
                # debug_msg = f"DEBUG: last_game_mode={self.last_game_mode}, Computer score before={self.scores['Computer']}"
                if self.last_game_mode == 'pvc':
                    self.scores["Computer"] += 1
                    # debug_msg += f", after={self.scores['Computer']}"
                # self.debug_message = debug_msg
                pygame.mixer.music.stop()
                pygame.mixer.music.load("sound_track/lose.mp3")
                pygame.mixer.music.play()
                self.state = GameState.GAME_OVER
            else:
                self.state = GameState.PLAYER1_TURN
            return
        # Hard: original logic
        # First, decide if computer should use Move Target button
        if not self.player2_moved_target:
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
        
        # --- Gift box logic: go for the gift if it helps (hard mode) ---
        go_for_gift = False
        if self.gift_box_location:
            path_to_gift = self.a_star_path(self.seeker2_pos, self.gift_box_location)
            path_to_jerry = self.a_star_path(self.seeker2_pos, self.hidden_pos)
            player_path_to_jerry = self.a_star_path(self.seeker1_pos, self.hidden_pos)
            if self.gift_box_location in path_to_jerry:
                go_for_gift = True
            else:
                if player_dist < computer_dist and (computer_dist - player_dist) <= 2:
                    go_for_gift = True
        if go_for_gift:
            path = self.a_star_path(self.seeker2_pos, self.gift_box_location)
            if len(path) > 1:
                next_pos = path[1]
                dx = next_pos[0] - self.seeker2_pos[0]
                dy = next_pos[1] - self.seeker2_pos[1]
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
                self.seeker2_pos = next_pos
                # Trigger gift box animation and freeze opponent immediately
                if self.seeker2_pos == self.gift_box_location:
                    self.gift_box_popping = True
                    self.gift_box_pop_position = self.gift_box_location
                    self.gift_box_pop_frame_index = 0
                    self.gift_box_pop_frame_timer = pygame.time.get_ticks()
                    self.gift_box_location = None
                    self.freeze_opponent(2)
                self.state = GameState.PLAYER1_TURN
                return
        
        # Enhanced block placement logic for hard mode
        # More aggressive and strategic than normal mode
        should_place_block = False
        
        # Condition 1: Player is close to Jerry and computer is farther
        if player_dist <= 5 and computer_dist > player_dist:
            should_place_block = True
        
        # Condition 2: Player is getting very close (within 3 steps)
        elif player_dist <= 3:
            should_place_block = True
        
        # Condition 3: Player is closer than computer by any margin
        elif player_dist < computer_dist:
            should_place_block = True
        
        # Condition 4: Strategic blocking - even if computer is closer, block to maintain advantage
        elif computer_dist <= 4 and player_dist <= computer_dist + 2:
            should_place_block = True
        
        # Higher probability and more aggressive for hard mode
        if should_place_block and self.player2_blocks_remaining > 0 and random.random() < 0.9:
            if self.computer_place_block():
                self.state = GameState.PLAYER1_TURN
                return
        
        # --- Block placement logic for normal mode ---
        should_place_block = False
        if player_dist <= 5 and computer_dist > player_dist:
            should_place_block = True
        elif player_dist <= 3:
            should_place_block = True
        elif player_dist < computer_dist:
            should_place_block = True

        if should_place_block and self.player2_blocks_remaining > 0 and random.random() < 0.5:  # 50% chance for normal mode
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
                debug_msg = f"DEBUG: last_game_mode={self.last_game_mode}, Computer score before={self.scores['Computer']}"
                if self.last_game_mode == 'pvc':
                    self.scores["Computer"] += 1
                    debug_msg += f", after={self.scores['Computer']}"
                self.debug_message = debug_msg
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
        
        # Draw animated gift box if present and not popping
        if self.gift_box_location and not self.gift_box_popping:
            gx, gy = self.gift_box_location
            rect = pygame.Rect(GRID_OFFSET_X + gy * CELL_SIZE, GRID_OFFSET_Y + gx * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            now = pygame.time.get_ticks()
            if now - self.gift_box_frame_timer > self.gift_box_frame_duration:
                self.gift_box_frame_index = (self.gift_box_frame_index + 1) % len(self.gift_box_frames)
                self.gift_box_frame_timer = now
            current_frame = self.gift_box_frames[self.gift_box_frame_index]
            screen.blit(current_frame, rect.topleft)
        
        # Draw player images (this will be on top of cheese if they're on a hiding spot)
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(GRID_OFFSET_X + y * CELL_SIZE, GRID_OFFSET_Y + x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (x, y) == self.seeker1_pos:
                    if self.player1_frozen_turns > 0:
                        screen.blit(self.tom_frozen_image, rect.topleft)
                    elif self.player1_unfreezing:
                        now = pygame.time.get_ticks()
                        if now - self.player1_unfreeze_timer < self.unfreeze_anim_duration:
                            jitter = self.unfreeze_anim_jitter
                            offset_x = random.randint(-jitter, jitter)
                            offset_y = random.randint(-jitter, jitter)
                            screen.blit(self.tom_frozen_image, (rect.x + offset_x, rect.y + offset_y))
                        else:
                            self.player1_unfreezing = False
                            self.tom_direction = "idle"
                            screen.blit(self.tom_images[self.tom_direction], rect.topleft)
                    else:
                        screen.blit(self.tom_images[self.tom_direction], rect.topleft)
                elif (x, y) == self.seeker2_pos:
                    if self.player2_frozen_turns > 0:
                        screen.blit(self.spike_frozen_image, rect.topleft)
                    elif self.player2_unfreezing:
                        now = pygame.time.get_ticks()
                        if now - self.player2_unfreeze_timer < self.unfreeze_anim_duration:
                            jitter = self.unfreeze_anim_jitter
                            offset_x = random.randint(-jitter, jitter)
                            offset_y = random.randint(-jitter, jitter)
                            screen.blit(self.spike_frozen_image, (rect.x + offset_x, rect.y + offset_y))
                        else:
                            self.player2_unfreezing = False
                            self.spike_direction = "idle"
                            screen.blit(self.spike_images[self.spike_direction], rect.topleft)
                    else:
                        screen.blit(self.spike_images[self.spike_direction], rect.topleft)
                if self.state == GameState.GAME_OVER and (x, y) == self.hidden_pos:
                    screen.blit(self.jerry_image, rect.topleft)
        
        # Draw popping animation if active (on top of player)
        if self.gift_box_popping and self.gift_box_pop_position:
            gx, gy = self.gift_box_pop_position
            rect = pygame.Rect(GRID_OFFSET_X + gy * CELL_SIZE, GRID_OFFSET_Y + gx * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            now = pygame.time.get_ticks()
            if now - self.gift_box_pop_frame_timer > self.gift_box_pop_frame_duration:
                self.gift_box_pop_frame_index += 1
                self.gift_box_pop_frame_timer = now
            if self.gift_box_pop_frame_index < len(self.gift_box_pop_frames):
                current_frame = self.gift_box_pop_frames[self.gift_box_pop_frame_index]
                screen.blit(current_frame, rect.topleft)
            else:
                # Animation finished, remove box
                self.gift_box_popping = False
                self.gift_box_pop_position = None
        
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
            # ✨ הצגת ג'רי רץ במיקום הישן 
        if self.show_jerry_running and self.jerry_running_pos:
            if pygame.time.get_ticks() - self.jerry_running_start_time < 1100:
                now = pygame.time.get_ticks()
                if now - self.jerry_running_frame_timer > self.jerry_running_frame_duration:
                    if self.jerry_running_frame_index < len(self.jerry_running_frames) - 1:
                        self.jerry_running_frame_index += 1
                    self.jerry_running_frame_timer = now

                x, y = self.jerry_running_pos
                rect = pygame.Rect(
                    GRID_OFFSET_X + y * CELL_SIZE, 
                    GRID_OFFSET_Y + x * CELL_SIZE, 
                    CELL_SIZE, CELL_SIZE
                )
                current_frame = self.jerry_running_frames[self.jerry_running_frame_index]
                screen.blit(current_frame, rect.topleft)
            else:
                self.show_jerry_running = False


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
        pygame.draw.rect(screen, (200, 200, 255), self.main_menu_button, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.main_menu_button, 3, border_radius=8)
        menu_text = self.font.render("Main Menu", True, (0, 0, 0))
        menu_rect = menu_text.get_rect(center=self.main_menu_button.center)
        screen.blit(menu_text, menu_rect)
        # Next Round button (to the right of Main Menu), only show if game is over
        if self.state == GameState.GAME_OVER:
            self.next_round_button = pygame.Rect(24 + button_width + button_spacing, button_y, button_width, button_height)
            pygame.draw.rect(screen, (200, 200, 255), self.next_round_button, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.next_round_button, 3, border_radius=8)
            next_text = self.font.render("Next Round", True, (0, 0, 0))
            next_rect = next_text.get_rect(center=self.next_round_button.center)
            screen.blit(next_text, next_rect)
        else:
            self.next_round_button = None

        # --- Display winner at the top center if game is over ---
        if self.state == GameState.GAME_OVER and self.winner:
            win_text = self.big_font.render(f"{self.winner} Wins!", True, BLACK)
            win_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, 40))
            screen.blit(win_text, win_rect)
            restart_text = self.font.render("", True, BLACK)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, 80))
            screen.blit(restart_text, restart_rect)

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

                move_text = self.font.render("Warn Jerry (Tom)", True, (0, 0, 0))
                move_rect = move_text.get_rect(center=self.move_target_button.center)
                screen.blit(move_text, move_rect)
                action_y += 44
            elif self.state == GameState.PLAYER2_TURN and not self.player2_moved_target and self.game_mode == 'pvp':
                self.move_target_button = pygame.Rect(ui_x, action_y, 180, 36)
                pygame.draw.rect(screen, (255, 200, 0), self.move_target_button, border_radius=8)
                pygame.draw.rect(screen, BLACK, self.move_target_button, 3, border_radius=8)

                move_text = self.font.render("Warn Jerry (Spike)", True, (0, 0, 0))
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

        # Allow clicking main menu anytime
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] and self.main_menu_button.collidepoint(pygame.mouse.get_pos()):
            pygame.mixer.music.stop()
            self.state = GameState.MENU
            self.show_title_screen()

        # --- Display scores at the top right ---
        score_margin = 24
        score_text = None
        if self.last_game_mode == 'pvp':
            score_text = self.font.render(f"Score: Tom {self.scores['Tom']}  |  Spike {self.scores['Spike']}", True, BLACK)
        elif self.last_game_mode == 'pvc':
            score_text = self.font.render(f"Score: Tom {self.scores['Tom']}  |  Computer {self.scores['Computer']}", True, BLACK)
        if score_text:
            score_rect = score_text.get_rect(topright=(WINDOW_WIDTH - score_margin, score_margin))
            screen.blit(score_text, score_rect)

        # --- Display debug message if present ---
        if hasattr(self, 'debug_message') and self.debug_message:
            debug_font = pygame.font.SysFont("Consolas", 22)
            debug_text = debug_font.render(self.debug_message, True, (200, 0, 0))
            screen.blit(debug_text, (40, 80))

    def move_target_to_new_location(self):
        """Move Jerry to a new random hiding location, but never to a position where a player is standing"""
        if self.hiding_spots:
            self.jerry_running_pos = self.hidden_pos
            self.show_jerry_running = True
            self.jerry_running_start_time = pygame.time.get_ticks()
            self.jerry_running_frame_index = 0
            self.jerry_running_frame_timer = pygame.time.get_ticks()

            # Choose a new location different from current and not occupied by a player
            possible_spots = [pos for pos in self.hiding_spots if pos != self.hidden_pos and pos != self.seeker1_pos and pos != self.seeker2_pos]
            if not possible_spots:
                # If all other spots are occupied, fallback to any spot not occupied by a player
                possible_spots = [pos for pos in self.hiding_spots if pos != self.seeker1_pos and pos != self.seeker2_pos]
            if possible_spots:
                new_pos = random.choice(possible_spots)
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
        self.seeker2_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
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
        # Reset freeze state
        self.player1_frozen_turns = 0
        self.player2_frozen_turns = 0
        self.player1_unfreezing = False
        self.player2_unfreezing = False
        self.player1_unfreeze_timer = 0
        self.player2_unfreeze_timer = 0
        # Reset gift box animation
        self.gift_box_frame_index = 0
        self.gift_box_frame_timer = pygame.time.get_ticks()
        # Track last game mode for score display (always set to current game mode)
        if self.game_mode:
            self.last_game_mode = self.game_mode

    def computer_place_block(self):
        """Computer places a block strategically to interfere with player's path"""
        if self.player2_blocks_remaining <= 0:
            return False
            
        player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
        computer_dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
        
        # Only place block if player is closer to Jerry than computer
        if player_dist >= computer_dist:
            return False
        
        # For normal mode, be more aggressive with block placement
        # Lower the threshold for "significant impact"
        min_impact = 1 if self.computer_difficulty == "normal" else 1  # Hard mode can also place blocks with 1-step impact
        
        # Try to block the player's path
        best_block = None
        best_impact = 0
        best_score = -1  # Higher score is better
        
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                # Try horizontal block
                if self.can_place_block(x, y, "horizontal"):
                    # Check if this block would block the player's path
                    old_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    old_computer_dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
                    
                    # Temporarily place block
                    self.blocks.append((x, y, "horizontal"))
                    new_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    new_computer_dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
                    self.blocks.pop()  # Remove temporary block
                    
                    # Calculate impact (how much it increases player's path)
                    player_impact = new_player_dist - old_player_dist
                    computer_impact = new_computer_dist - old_computer_dist
                    
                    # Score this block placement
                    # Higher score if it blocks player more and doesn't block computer
                    score = player_impact * 2 - computer_impact
                    
                    # Hard mode gets bonus for strategic positioning
                    if self.computer_difficulty == "hard" and self.hidden_pos is not None:
                        # Bonus for significant impact
                        if player_impact >= 3:
                            score += 2
                        # Bonus for blocking close to Jerry
                        target_dist = abs(x - self.hidden_pos[0]) + abs(y - self.hidden_pos[1])
                        if target_dist <= 2:
                            score += 1
                    
                    if player_impact > best_impact and new_player_dist != float('inf') and score > best_score:
                        best_impact = player_impact
                        best_score = score
                        best_block = (x, y, "horizontal")
                
                # Try vertical block
                if self.can_place_block(x, y, "vertical"):
                    # Check if this block would block the player's path
                    old_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    old_computer_dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
                    
                    # Temporarily place block
                    self.blocks.append((x, y, "vertical"))
                    new_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    new_computer_dist = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
                    self.blocks.pop()  # Remove temporary block
                    
                    # Calculate impact (how much it increases player's path)
                    player_impact = new_player_dist - old_player_dist
                    computer_impact = new_computer_dist - old_computer_dist
                    
                    # Score this block placement
                    # Higher score if it blocks player more and doesn't block computer
                    score = player_impact * 2 - computer_impact
                    
                    # Hard mode gets bonus for strategic positioning
                    if self.computer_difficulty == "hard" and self.hidden_pos is not None:
                        # Bonus for significant impact
                        if player_impact >= 3:
                            score += 2
                        # Bonus for blocking close to Jerry
                        target_dist = abs(x - self.hidden_pos[0]) + abs(y - self.hidden_pos[1])
                        if target_dist <= 2:
                            score += 1
                    
                    if player_impact > best_impact and new_player_dist != float('inf') and score > best_score:
                        best_impact = player_impact
                        best_score = score
                        best_block = (x, y, "vertical")
        
        # Place the best block if it has significant impact
        if best_block and best_impact >= min_impact:
            x, y, orientation = best_block
            self.place_block(x, y, orientation, 2)
            return True
        
        # If no good strategic block found, try to block on the player's likely path
        player_path = self.get_player_likely_path()
        if len(player_path) > 1:  # If we have a path to block
            # Try to block on the next few steps of the player's path
            for i in range(1, min(4, len(player_path))):  # Look at next 3 steps
                path_pos = player_path[i]
                # Try horizontal block on path
                if self.can_place_block(path_pos[0], path_pos[1], "horizontal"):
                    # Check if this actually blocks the player's path
                    old_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    self.blocks.append((path_pos[0], path_pos[1], "horizontal"))
                    new_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    self.blocks.pop()
                    if new_player_dist > old_player_dist and new_player_dist != float('inf'):
                        self.place_block(path_pos[0], path_pos[1], "horizontal", 2)
                        return True
                # Try vertical block on path
                if self.can_place_block(path_pos[0], path_pos[1], "vertical"):
                    # Check if this actually blocks the player's path
                    old_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    self.blocks.append((path_pos[0], path_pos[1], "vertical"))
                    new_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                    self.blocks.pop()
                    if new_player_dist > old_player_dist and new_player_dist != float('inf'):
                        self.place_block(path_pos[0], path_pos[1], "vertical", 2)
                        return True
        
        # Fallback: try to block near the player's current position
        if player_dist <= 4:  # Increased range for normal mode
            # Try to block in the direction the player is likely to move
            for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                nx, ny = self.seeker1_pos[0] + dx, self.seeker1_pos[1] + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    # Try horizontal block near player
                    if self.can_place_block(nx, ny, "horizontal"):
                        # Check if this actually blocks the player's path
                        old_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                        self.blocks.append((nx, ny, "horizontal"))
                        new_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                        self.blocks.pop()
                        if new_player_dist > old_player_dist and new_player_dist != float('inf'):
                            self.place_block(nx, ny, "horizontal", 2)
                            return True
                    # Try vertical block near player
                    if self.can_place_block(nx, ny, "vertical"):
                        # Check if this actually blocks the player's path
                        old_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                        self.blocks.append((nx, ny, "vertical"))
                        new_player_dist = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                        self.blocks.pop()
                        if new_player_dist > old_player_dist and new_player_dist != float('inf'):
                            self.place_block(nx, ny, "vertical", 2)
                            return True
        
        return False

    def get_player_likely_path(self):
        """Get the likely path the player will take to reach Jerry"""
        if not hasattr(self, '_player_path_cache') or self._player_path_cache[0] != (self.seeker1_pos, self.hidden_pos):
            # Use A* to find the shortest path from player to Jerry
            path = self.a_star_path(self.seeker1_pos, self.hidden_pos)
            self._player_path_cache = ((self.seeker1_pos, self.hidden_pos), path)
        return self._player_path_cache[1]

    def a_star_path(self, start, goal):
        """A* algorithm that returns the actual path, not just distance"""
        if start == goal:
            return [start]
        
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: abs(start[0]-goal[0]) + abs(start[1]-goal[1])}
        
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path
            
            for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                neighbor = (current[0]+dx, current[1]+dy)
                if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE:
                    if self.is_position_blocked(neighbor):
                        continue
                    
                    temp_g_score = g_score[current] + 1
                    if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = temp_g_score
                        f_score[neighbor] = temp_g_score + abs(neighbor[0]-goal[0]) + abs(neighbor[1]-goal[1])
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return []  # No path found

    def run(self):
        self.show_title_screen()
        running = True
        player_turn = 1  # 1 for Tom, 2 for Spike (in PvP)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == GameState.MENU:
                        self.start_game()
                        player_turn = 1
                    elif self.state == GameState.GAME_OVER:
                        # Do nothing on key press after game over; wait for Next Round button
                        pass
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
                            # Check for gift box collection
                            if self.gift_box_location and self.seeker1_pos == self.gift_box_location:
                                self.gift_box_popping = True
                                self.gift_box_pop_position = self.gift_box_location
                                self.gift_box_pop_frame_index = 0
                                self.gift_box_pop_frame_timer = pygame.time.get_ticks()
                                self.gift_box_location = None
                                self.freeze_opponent(1)
                            if self.seeker1_pos == self.hidden_pos:
                                self.winner = "Tom (Player 1)"
                                if self.last_game_mode == 'pvp':
                                    self.scores["Tom"] += 1
                                else:
                                    self.scores["Tom"] += 1
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
                                # Check for gift box collection
                                if self.gift_box_location and self.seeker2_pos == self.gift_box_location:
                                    self.gift_box_popping = True
                                    self.gift_box_pop_position = self.gift_box_location
                                    self.gift_box_pop_frame_index = 0
                                    self.gift_box_pop_frame_timer = pygame.time.get_ticks()
                                    self.gift_box_location = None
                                    self.freeze_opponent(2)
                                if self.seeker2_pos == self.hidden_pos:
                                    self.winner = "Spike (Player 2)"
                                    if self.last_game_mode == 'pvp':
                                        self.scores["Spike"] += 1
                                    elif self.last_game_mode == 'pvc':
                                        self.scores["Computer"] += 1
                                    pygame.mixer.music.stop()
                                    if self.game_mode == 'pvp':
                                        pygame.mixer.music.load("sound_track/spike_win.wav")
                                    else:
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
                        # No need to reset here anymore
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

            # Handle freezing and skipping turns
            # Player 1 frozen logic
            if self.state == GameState.PLAYER1_TURN and self.player1_frozen_turns > 0:
                self.player1_frozen_turns -= 1
                if self.player1_frozen_turns == 0:
                    self.player1_unfreezing = True
                    self.player1_unfreeze_timer = pygame.time.get_ticks()
                self.state = GameState.PLAYER2_TURN if self.game_mode == 'pvp' else GameState.PLAYER2_TURN
                continue
            # Player 2 frozen logic
            if self.state == GameState.PLAYER2_TURN and self.player2_frozen_turns > 0:
                self.player2_frozen_turns -= 1
                if self.player2_frozen_turns == 0:
                    self.player2_unfreezing = True
                    self.player2_unfreeze_timer = pygame.time.get_ticks()
                self.state = GameState.PLAYER1_TURN
                continue

            # --- Computer collects gift box logic ---
            if self.state == GameState.PLAYER2_TURN and self.game_mode != 'pvp':
                if self.gift_box_location and self.seeker2_pos == self.gift_box_location:
                    self.gift_box_popping = True
                    self.gift_box_pop_position = self.gift_box_location
                    self.gift_box_pop_frame_index = 0
                    self.gift_box_pop_frame_timer = pygame.time.get_ticks()
                    self.gift_box_location = None
                    self.freeze_opponent(2)

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

    def freeze_opponent(self, player):
        # player: 1 or 2 (the one who collected the gift)
        if player == 1:
            self.player2_frozen_turns = 2
        else:
            self.player1_frozen_turns = 2

if __name__ == "__main__":
    HideSeekGame().run()
