import pygame
import random
import sys
import math
import time


# ============================================================
# CONFIG
# ============================================================

WIDTH = 1100
HEIGHT = 780

FPS = 60

BOARD_SIZE = 10

DIFFICULTIES = {
    "EASY": (10, 10),
    "NORMAL": (14, 30),
    "HARD": (18, 60),
}

CURRENT_DIFFICULTY = "NORMAL"


# ============================================================
# COLORS
# ============================================================

BG = (10, 12, 20)
PANEL = (18, 21, 33)
PANEL_2 = (23, 27, 42)

CELL_HIDDEN = (30, 35, 52)
CELL_HOVER = (39, 46, 68)
CELL_REVEALED = (22, 26, 39)

GRID = (48, 55, 75)

WHITE = (235, 240, 250)
MUTED = (130, 140, 160)

CYAN = (70, 220, 255)
GREEN = (75, 230, 150)
RED = (255, 75, 95)
YELLOW = (255, 205, 70)
PURPLE = (175, 110, 255)

NUMBER_COLORS = {
    1: (75, 180, 255),
    2: (75, 230, 150),
    3: (255, 90, 100),
    4: (170, 110, 255),
    5: (255, 150, 70),
    6: (70, 220, 220),
    7: (230, 230, 240),
    8: (150, 160, 180),
}


# ============================================================
# DIFFICULTY
# ============================================================

def difficulty_data(name):
    size, bombs = DIFFICULTIES[name]
    return size, bombs


# ============================================================
# CELL
# ============================================================

class Cell:

    def __init__(self):
        self.value = 0
        self.revealed = False
        self.flagged = False

        self.animation = 0.0
        self.flag_animation = 0.0


# ============================================================
# BOARD
# ============================================================

class Board:

    def __init__(self, size, bombs):
        self.size = size
        self.bombs = bombs

        self.cells = [
            [Cell() for _ in range(size)]
            for _ in range(size)
        ]

        self.first_move = True
        self.game_over = False
        self.won = False

        self.revealed_count = 0
        self.flag_count = 0

        self.explosion_cell = None

        self.generate_empty_board()

    # --------------------------------------------------------

    def generate_empty_board(self):
        for row in self.cells:
            for cell in row:
                cell.value = 0

    # --------------------------------------------------------

    def generate(self, safe_row, safe_col):

        # Reset
        self.cells = [
            [Cell() for _ in range(self.size)]
            for _ in range(self.size)
        ]

        bombs = 0

        while bombs < self.bombs:

            row = random.randrange(self.size)
            col = random.randrange(self.size)

            # First cell is safe
            if row == safe_row and col == safe_col:
                continue

            # Also keep the immediate neighborhood safe.
            # This makes the first move much nicer.
            if abs(row - safe_row) <= 1 and abs(col - safe_col) <= 1:
                continue

            if self.cells[row][col].value != 9:
                self.cells[row][col].value = 9
                bombs += 1

        # Calculate numbers
        for row in range(self.size):
            for col in range(self.size):

                if self.cells[row][col].value == 9:
                    continue

                count = 0

                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):

                        if dr == 0 and dc == 0:
                            continue

                        nr = row + dr
                        nc = col + dc

                        if (
                            0 <= nr < self.size
                            and 0 <= nc < self.size
                        ):
                            if self.cells[nr][nc].value == 9:
                                count += 1

                self.cells[row][col].value = count

        self.first_move = False

    # --------------------------------------------------------

    def neighbors(self, row, col):

        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):

                if dr == 0 and dc == 0:
                    continue

                nr = row + dr
                nc = col + dc

                if (
                    0 <= nr < self.size
                    and 0 <= nc < self.size
                ):
                    yield nr, nc

    # --------------------------------------------------------

    def reveal(self, row, col):

        if not (0 <= row < self.size and 0 <= col < self.size):
            return

        cell = self.cells[row][col]

        if cell.revealed or cell.flagged:
            return

        if self.first_move:
            self.generate(row, col)
            cell = self.cells[row][col]

        if cell.value == 9:

            self.game_over = True
            self.explosion_cell = (row, col)

            # Reveal every bomb
            for r in range(self.size):
                for c in range(self.size):

                    if self.cells[r][c].value == 9:
                        self.cells[r][c].revealed = True

            return

        self._flood_reveal(row, col)

        self.check_win()

    # --------------------------------------------------------

    def _flood_reveal(self, row, col):

        if not (0 <= row < self.size and 0 <= col < self.size):
            return

        cell = self.cells[row][col]

        if cell.revealed or cell.flagged:
            return

        if cell.value == 9:
            return

        cell.revealed = True
        cell.animation = 0.0

        self.revealed_count += 1

        # Empty cells automatically expand
        if cell.value == 0:

            for nr, nc in self.neighbors(row, col):

                neighbor = self.cells[nr][nc]

                if not neighbor.revealed:
                    self._flood_reveal(nr, nc)

    # --------------------------------------------------------

    def toggle_flag(self, row, col):

        if self.game_over:
            return

        cell = self.cells[row][col]

        if cell.revealed:
            return

        if not cell.flagged:

            if self.flag_count >= self.bombs:
                return

            cell.flagged = True
            cell.flag_animation = 0.0

            self.flag_count += 1

        else:

            cell.flagged = False
            cell.flag_animation = 0.0

            self.flag_count -= 1

    # --------------------------------------------------------

    def check_win(self):

        safe_cells = self.size * self.size - self.bombs

        if self.revealed_count >= safe_cells:

            self.won = True
            self.game_over = True

            # Automatically flag bombs
            for row in self.cells:
                for cell in row:
                    if cell.value == 9:
                        cell.flagged = True


# ============================================================
# PARTICLES
# ============================================================

class Particle:

    def __init__(self, x, y, color):

        self.x = x
        self.y = y

        angle = random.uniform(0, math.tau)
        speed = random.uniform(80, 260)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.life = random.uniform(0.5, 1.2)
        self.max_life = self.life

        self.size = random.randint(2, 6)
        self.color = color

    def update(self, dt):

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.vy += 300 * dt

        self.life -= dt

    def draw(self, screen):

        if self.life <= 0:
            return

        ratio = self.life / self.max_life

        radius = max(1, int(self.size * ratio))

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            radius
        )


# ============================================================
# BUTTON
# ============================================================

class Button:

    def __init__(self, rect, text):

        self.rect = pygame.Rect(rect)
        self.text = text

        self.hover = False
        self.pressed = False

    def update(self, mouse):

        self.hover = self.rect.collidepoint(mouse)

    def draw(self, screen, font):

        color = PANEL_2 if not self.hover else (34, 42, 63)

        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            CYAN if self.hover else GRID,
            self.rect,
            2,
            border_radius=12
        )

        text = font.render(
            self.text,
            True,
            WHITE
        )

        screen.blit(
            text,
            text.get_rect(center=self.rect.center)
        )


# ============================================================
# GAME
# ============================================================

class Minesweeper:

    def __init__(self):

        pygame.init()

        pygame.display.set_caption(
            "Minesweeper // Neon"
        )

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.Font(
            None,
            42
        )

        self.font_large = pygame.font.Font(
            None,
            32
        )

        self.font_medium = pygame.font.Font(
            None,
            24
        )

        self.font_small = pygame.font.Font(
            None,
            18
        )

        self.size, self.bombs = difficulty_data(
            CURRENT_DIFFICULTY
        )

        self.board = Board(
            self.size,
            self.bombs
        )

        self.start_time = None
        self.elapsed = 0

        self.particles = []

        self.restart_button = Button(
            (850, 690, 190, 50),
            "RESTART"
        )

        self.difficulty_buttons = []

        names = ["EASY", "NORMAL", "HARD"]

        for i, name in enumerate(names):

            self.difficulty_buttons.append(
                Button(
                    (
                        600 + i * 125,
                        95,
                        110,
                        40
                    ),
                    name
                )
            )

        self.running = True

        self.board_rect = pygame.Rect(
            50,
            120,
            500,
            500
        )

    # --------------------------------------------------------

    def reset(self, difficulty=None):

        global CURRENT_DIFFICULTY

        if difficulty is not None:

            CURRENT_DIFFICULTY = difficulty

            self.size, self.bombs = difficulty_data(
                difficulty
            )

        self.board = Board(
            self.size,
            self.bombs
        )

        self.start_time = None
        self.elapsed = 0

        self.particles.clear()

        # Board size
        board_size = min(
            500,
            HEIGHT - 190
        )

        self.board_rect = pygame.Rect(
            50,
            120,
            board_size,
            board_size
        )

    # --------------------------------------------------------

    def cell_rect(self, row, col):

        cell_size = self.board_rect.width / self.size

        return pygame.Rect(
            int(self.board_rect.x + col * cell_size),
            int(self.board_rect.y + row * cell_size),
            int(cell_size),
            int(cell_size)
        )

    # --------------------------------------------------------

    def get_cell(self, mouse):

        if not self.board_rect.collidepoint(mouse):
            return None

        cell_size = self.board_rect.width / self.size

        col = int(
            (mouse[0] - self.board_rect.x)
            / cell_size
        )

        row = int(
            (mouse[1] - self.board_rect.y)
            / cell_size
        )

        if (
            0 <= row < self.size
            and 0 <= col < self.size
        ):
            return row, col

        return None

    # --------------------------------------------------------

    def start_timer(self):

        if self.start_time is None:
            self.start_time = time.time()

    # --------------------------------------------------------

    def update_timer(self):

        if (
            self.start_time is not None
            and not self.board.game_over
        ):
            self.elapsed = int(
                time.time() - self.start_time
            )

    # --------------------------------------------------------

    def spawn_explosion(self, row, col):

        rect = self.cell_rect(row, col)

        for _ in range(100):

            self.particles.append(
                Particle(
                    rect.centerx,
                    rect.centery,
                    random.choice([
                        RED,
                        YELLOW,
                        (255, 120, 50),
                        WHITE
                    ])
                )
            )

    # --------------------------------------------------------

    def handle_events(self):

        mouse = pygame.mouse.get_pos()

        self.restart_button.update(mouse)

        for button in self.difficulty_buttons:
            button.update(mouse)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False
                return

            # -------------------------
            # Keyboard
            # -------------------------

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    self.reset()

                if event.key == pygame.K_ESCAPE:
                    self.running = False

            # -------------------------
            # Mouse
            # -------------------------

            if event.type == pygame.MOUSEBUTTONDOWN:

                # Restart
                if (
                    event.button == 1
                    and self.restart_button.rect.collidepoint(
                        event.pos
                    )
                ):
                    self.reset()
                    continue

                # Difficulty
                if event.button == 1:

                    for button in self.difficulty_buttons:

                        if button.rect.collidepoint(
                            event.pos
                        ):

                            self.reset(
                                button.text
                            )

                            break

                cell = self.get_cell(
                    event.pos
                )

                if cell is None:
                    continue

                row, col = cell

                # Left click
                if event.button == 1:

                    if not self.board.game_over:

                        self.start_timer()

                        was_bomb = (
                            not self.board.first_move
                            and self.board.cells[row][col].value == 9
                        )

                        self.board.reveal(
                            row,
                            col
                        )

                        if (
                            self.board.game_over
                            and not self.board.won
                            and was_bomb
                        ):
                            self.spawn_explosion(
                                row,
                                col
                            )

                # Right click
                elif event.button == 3:

                    self.board.toggle_flag(
                        row,
                        col
                    )

    # --------------------------------------------------------

    def update(self, dt):

        self.update_timer()

        for particle in self.particles:
            particle.update(dt)

        self.particles = [
            p for p in self.particles
            if p.life > 0
        ]

        # Cell animations
        for row in self.board.cells:

            for cell in row:

                if cell.revealed:
                    cell.animation = min(
                        1.0,
                        cell.animation + dt * 8
                    )

                if cell.flagged:
                    cell.flag_animation = min(
                        1.0,
                        cell.flag_animation + dt * 10
                    )

    # --------------------------------------------------------

    def draw_background(self):

        self.screen.fill(BG)

        # Decorative glow circles
        pygame.draw.circle(
            self.screen,
            (15, 30, 45),
            (1000, 100),
            260
        )

        pygame.draw.circle(
            self.screen,
            (25, 20, 45),
            (100, 700),
            250
        )

    # --------------------------------------------------------

    def draw_header(self):

        title = self.font_title.render(
            "MINESWEEPER",
            True,
            WHITE
        )

        self.screen.blit(
            title,
            (50, 35)
        )

        subtitle = self.font_small.render(
            "NEON // STRATEGY // SURVIVAL",
            True,
            CYAN
        )

        self.screen.blit(
            subtitle,
            (53, 78)
        )

        # Difficulty buttons
        for button in self.difficulty_buttons:
            button.draw(
                self.screen,
                self.font_small
            )

    # --------------------------------------------------------

    def draw_panel(self):

        panel = pygame.Rect(
            600,
            170,
            440,
            420
        )

        pygame.draw.rect(
            self.screen,
            PANEL,
            panel,
            border_radius=20
        )

        pygame.draw.rect(
            self.screen,
            GRID,
            panel,
            2,
            border_radius=20
        )

        # Bomb counter
        self.draw_stat(
            "MINES",
            str(
                max(
                    0,
                    self.bombs - self.board.flag_count
                )
            ),
            625,
            205,
            RED
        )

        # Timer
        self.draw_stat(
            "TIME",
            f"{self.elapsed:03d}",
            825,
            205,
            CYAN
        )

        # Instructions
        instruction_y = 320

        instructions = [
            ("LEFT CLICK", "Reveal a cell"),
            ("RIGHT CLICK", "Place a flag"),
            ("R", "Restart"),
            ("ESC", "Quit"),
        ]

        for key, description in instructions:

            key_surface = self.font_medium.render(
                key,
                True,
                CYAN
            )

            desc_surface = self.font_small.render(
                description,
                True,
                MUTED
            )

            self.screen.blit(
                key_surface,
                (625, instruction_y)
            )

            self.screen.blit(
                desc_surface,
                (625, instruction_y + 28)
            )

            instruction_y += 62

    # --------------------------------------------------------

    def draw_stat(
        self,
        label,
        value,
        x,
        y,
        color
    ):

        label_surface = self.font_small.render(
            label,
            True,
            MUTED
        )

        value_surface = self.font_large.render(
            value,
            True,
            color
        )

        self.screen.blit(
            label_surface,
            (x, y)
        )

        self.screen.blit(
            value_surface,
            (x, y + 25)
        )

    # --------------------------------------------------------

    def draw_board(self):

        mouse = pygame.mouse.get_pos()

        for row in range(self.size):

            for col in range(self.size):

                cell = self.board.cells[row][col]

                rect = self.cell_rect(
                    row,
                    col
                )

                hovered = (
                    rect.collidepoint(mouse)
                    and not self.board.game_over
                )

                # -------------------------
                # Shadow
                # -------------------------

                shadow = rect.move(0, 4)

                pygame.draw.rect(
                    self.screen,
                    (5, 7, 12),
                    shadow,
                    border_radius=8
                )

                # -------------------------
                # Revealed
                # -------------------------

                if cell.revealed:

                    pygame.draw.rect(
                        self.screen,
                        CELL_REVEALED,
                        rect,
                        border_radius=8
                    )

                    # Bomb
                    if cell.value == 9:

                        pygame.draw.circle(
                            self.screen,
                            RED,
                            rect.center,
                            int(rect.width * 0.22)
                        )

                        pygame.draw.circle(
                            self.screen,
                            (255, 180, 180),
                            (
                                rect.centerx - 5,
                                rect.centery - 5
                            ),
                            4
                        )

                    # Number
                    elif cell.value != 0:

                        color = NUMBER_COLORS.get(
                            cell.value,
                            WHITE
                        )

                        text = self.font_medium.render(
                            str(cell.value),
                            True,
                            color
                        )

                        self.screen.blit(
                            text,
                            text.get_rect(
                                center=rect.center
                            )
                        )

                # -------------------------
                # Hidden
                # -------------------------

                else:

                    color = (
                        CELL_HOVER
                        if hovered
                        else CELL_HIDDEN
                    )

                    pygame.draw.rect(
                        self.screen,
                        color,
                        rect,
                        border_radius=8
                    )

                    # Top highlight
                    pygame.draw.line(
                        self.screen,
                        (
                            60,
                            68,
                            90
                        ),
                        (
                            rect.x + 8,
                            rect.y + 5
                        ),
                        (
                            rect.right - 8,
                            rect.y + 5
                        ),
                        2
                    )

                    # Flag
                    if cell.flagged:

                        pole_x = rect.centerx - 4

                        pygame.draw.line(
                            self.screen,
                            WHITE,
                            (
                                pole_x,
                                rect.centery - 13
                            ),
                            (
                                pole_x,
                                rect.centery + 14
                            ),
                            3
                        )

                        pygame.draw.polygon(
                            self.screen,
                            RED,
                            [
                                (
                                    pole_x,
                                    rect.centery - 13
                                ),
                                (
                                    pole_x + 17,
                                    rect.centery - 6
                                ),
                                (
                                    pole_x,
                                    rect.centery + 2
                                )
                            ]
                        )

                # Grid
                pygame.draw.rect(
                    self.screen,
                    GRID,
                    rect,
                    1,
                    border_radius=8
                )

    # --------------------------------------------------------

    def draw_status(self):

        if not self.board.game_over:
            return

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (5, 7, 14, 90)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        if self.board.won:

            title = "YOU WIN"

            color = GREEN

            subtitle = (
                f"Cleared in {self.elapsed} seconds"
            )

        else:

            title = "BOOM"

            color = RED

            subtitle = (
                "Better luck next time..."
            )

        title_surface = self.font_title.render(
            title,
            True,
            color
        )

        subtitle_surface = self.font_medium.render(
            subtitle,
            True,
            WHITE
        )

        center_x = WIDTH // 2

        self.screen.blit(
            title_surface,
            title_surface.get_rect(
                center=(
                    center_x,
                    625
                )
            )
        )

        self.screen.blit(
            subtitle_surface,
            subtitle_surface.get_rect(
                center=(
                    center_x,
                    665
                )
            )
        )

    # --------------------------------------------------------

    def draw(self):

        self.draw_background()

        self.draw_header()

        self.draw_board()

        self.draw_panel()

        self.restart_button.draw(
            self.screen,
            self.font_medium
        )

        for particle in self.particles:
            particle.draw(
                self.screen
            )

        self.draw_status()

        pygame.display.flip()

    # --------------------------------------------------------

    def run(self):

        while self.running:

            dt = self.clock.tick(FPS) / 1000

            self.handle_events()

            self.update(dt)

            self.draw()

        pygame.quit()
        sys.exit()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    game = Minesweeper()

    game.run()
