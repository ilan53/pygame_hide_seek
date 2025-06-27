import pygame
import sys
import random
import heapq
from enum import Enum

pygame.init()
pygame.mixer.init()

GRID_SIZE = 8
CELL_SIZE = 60
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
WINDOW_WIDTH = WIDTH + 200
WINDOW_HEIGHT = HEIGHT + 100
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
LIGHT_GREEN = (180, 255, 230) 
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GREEN = (0, 128, 0)
PURPLE = (160, 32, 240)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
FONT = pygame.font.SysFont("Segoe UI Emoji", 28)

class GameState(Enum):
    MENU = 1
    PLAYER1_TURN = 2
    PLAYER2_TURN = 3
    GAME_OVER = 4

class HideSeekGame:
    def __init__(self):
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

        self.jerry_images = [
            pygame.transform.scale(pygame.image.load("jerry/jerry_hiding1.png"), (CELL_SIZE, CELL_SIZE)),
            pygame.transform.scale(pygame.image.load("jerry/jerry_hiding2.png"), (CELL_SIZE, CELL_SIZE)),
            pygame.transform.scale(pygame.image.load("jerry/jerry_hiding3.png"), (CELL_SIZE, CELL_SIZE))
        ]
        self.jerry_image = self.jerry_images[0]  

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
        self.max_steps = 15
        self.steps_remaining = self.max_steps
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
                "🎯 Each player gets 15 steps to find him",
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
        for _ in range(random.randint(8, 12)):
            while True:
                pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
                if pos not in self.hiding_spots:
                    self.hiding_spots.append(pos)
                    break

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
        
        # Regular movement logic
        best_move = None
        best_score = float('inf')
        x, y = self.seeker2_pos
        
        # Consider both distance to Jerry and blocking player's path
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
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
                rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, DARK_GREEN if (x, y) in self.hiding_spots else WHITE, rect)
                if (x, y) == self.seeker1_pos:
                    screen.blit(self.tom_images[self.tom_direction], rect.topleft)
                elif (x, y) == self.seeker2_pos:
                   screen.blit(self.spike_images[self.spike_direction], rect.topleft)
                if self.state == GameState.GAME_OVER and (x, y) == self.hidden_pos:
                    screen.blit(self.jerry_image, rect.topleft)
                pygame.draw.rect(screen, BLACK, rect, 2)

    def draw_ui(self):
        ui_x = WIDTH + 10
        if self.state == GameState.PLAYER1_TURN or self.state == GameState.PLAYER2_TURN:
            screen.blit(self.font.render(f"Steps: {self.steps_remaining}", True, BLACK), (ui_x, 50))
            # Show distance to Jerry for both players
            if self.hidden_pos is not None:
                dist1 = self.a_star_distance(self.seeker1_pos, self.hidden_pos)
                dist2 = self.a_star_distance(self.seeker2_pos, self.hidden_pos)
                screen.blit(self.font.render(f"Tom→Jerry: {dist1} steps", True, BLACK), (ui_x, 80))
                screen.blit(self.font.render(f"Spike→Jerry: {dist2} steps", True, BLACK), (ui_x, 110))
            
            # Show computer thinking indicator
            if self.state == GameState.PLAYER2_TURN and self.game_mode != 'pvp':
                if not self.player2_moved_target:
                    screen.blit(self.font.render("Computer is thinking...", True, RED), (ui_x, 140))
                    screen.blit(self.font.render("(Can use Move Target)", True, ORANGE), (ui_x, 160))
                else:
                    screen.blit(self.font.render("Computer is thinking...", True, RED), (ui_x, 140))
            
            # Draw Move Target button for current player if they haven't used it
            if self.state == GameState.PLAYER1_TURN and not self.player1_moved_target:
                self.move_target_button = pygame.Rect(ui_x, 200, 180, 40)
                pygame.draw.rect(screen, (100, 200, 100), self.move_target_button)
                move_text = self.font.render("Move Target (Tom)", True, (0, 0, 0))
                move_rect = move_text.get_rect(center=self.move_target_button.center)
                screen.blit(move_text, move_rect)
            elif self.state == GameState.PLAYER2_TURN and not self.player2_moved_target and self.game_mode == 'pvp':
                self.move_target_button = pygame.Rect(ui_x, 200, 180, 40)
                pygame.draw.rect(screen, (200, 100, 100), self.move_target_button)
                move_text = self.font.render("Move Target (Spike)", True, (0, 0, 0))
                move_rect = move_text.get_rect(center=self.move_target_button.center)
                screen.blit(move_text, move_rect)
            else:
                self.move_target_button = None
                
        if self.feedback_text in self.feedback_images:
            screen.blit(self.feedback_images[self.feedback_text], (ui_x, 250))
        elif self.state == GameState.GAME_OVER:
            screen.blit(self.big_font.render(f"{self.winner} Wins!", True, BLACK), (ui_x, 50))
            screen.blit(self.font.render("Press any key to restart", True, BLACK), (ui_x, 100))
            # Draw Next Round button
            self.next_round_button = pygame.Rect(ui_x, 160, 180, 50)
            pygame.draw.rect(screen, (255, 200, 0), self.next_round_button)
            next_text = self.font.render("Next Round", True, (0, 0, 0))
            next_rect = next_text.get_rect(center=self.next_round_button.center)
            screen.blit(next_text, next_rect)
        else:
            self.next_round_button = None

    def move_target_to_new_location(self):
        """Move Jerry to a new random hiding location"""
        if self.hiding_spots:
            # Choose a new location different from current
            new_pos = random.choice(self.hiding_spots)
            while new_pos == self.hidden_pos and len(self.hiding_spots) > 1:
                new_pos = random.choice(self.hiding_spots)
            self.hidden_pos = new_pos
            self.jerry_image = random.choice(self.jerry_images)
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
        self.steps_remaining = self.max_steps
        self.feedback_text = ""
        self.winner = None
        self.tom_direction = "idle"
        self.spike_direction = "idle"
        self.jerry_image = random.choice(self.jerry_images)
        self.state = GameState.PLAYER1_TURN
        self.player1_moved_target = False
        self.player2_moved_target = False

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
                        x, y = self.seeker1_pos
                        moved = False
                        if event.key == pygame.K_UP and x > 0:
                            self.seeker1_pos = (x - 1, y)
                            self.tom_direction = "up"
                            moved = True
                        elif event.key == pygame.K_DOWN and x < GRID_SIZE - 1:
                            self.seeker1_pos = (x + 1, y)
                            self.tom_direction = "down"
                            moved = True
                        elif event.key == pygame.K_LEFT and y > 0:
                            self.seeker1_pos = (x, y - 1)
                            self.tom_direction = "left"
                            moved = True
                        elif event.key == pygame.K_RIGHT and y < GRID_SIZE - 1:
                            self.seeker1_pos = (x, y + 1)
                            self.tom_direction = "right"
                            moved = True
                        if moved:
                            self.steps_remaining -= 1
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
                            x, y = self.seeker2_pos
                            moved = False
                            if event.key == pygame.K_w and x > 0:
                                self.seeker2_pos = (x - 1, y)
                                self.spike_direction = "up"
                                moved = True
                            elif event.key == pygame.K_s and x < GRID_SIZE - 1:
                                self.seeker2_pos = (x + 1, y)
                                self.spike_direction = "down"
                                moved = True
                            elif event.key == pygame.K_a and y > 0:
                                self.seeker2_pos = (x, y - 1)
                                self.spike_direction = "left"
                                moved = True
                            elif event.key == pygame.K_d and y < GRID_SIZE - 1:
                                self.seeker2_pos = (x, y + 1)
                                self.spike_direction = "right"
                                moved = True
                            if moved:
                                self.steps_remaining -= 1
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
                    if self.state == GameState.GAME_OVER and self.next_round_button and self.next_round_button.collidepoint(event.pos):
                        self.start_game()
                        player_turn = 1
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

            if self.state == GameState.PLAYER2_TURN and self.game_mode != 'pvp':
                if not self.computer_thinking:
                    self.computer_thinking = True
                    self.computer_think_time = pygame.time.get_ticks()
                elif pygame.time.get_ticks() - self.computer_think_time > 800:  # 800ms delay
                    self.computer_move()
                    self.computer_thinking = False

            screen.fill(LIGHT_GREEN)
            if self.state != GameState.MENU:
                self.draw_grid()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    HideSeekGame().run()
