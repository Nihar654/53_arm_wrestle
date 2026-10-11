import math
import random
import pygame


class GameEngine:

    AI_TIME_STEP = 1.0 / 60.0
    AI_SURGE_DURATION = 2.0
    AI_COOLDOWN_DURATION = 4.0
    AI_SURGE_MULTIPLIER = 2.5
    AI_COOLDOWN_MULTIPLIER = 0.35
    PLAYER_PUSH_STRENGTH = 4.2
    NORMAL_STAMINA_RECOVERY = 0.8
    COUNTER_SURGE_WINDOW = 0.5
    COUNTER_SURGE_DURATION = 1.5
    COUNTER_SURGE_PUSH_MULTIPLIER = 2.0
    COUNTER_SURGE_STAMINA_RECOVERY = 2.0

    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.arm_position = 0.0
        self.target_limit = 100.0
        self.last_key = None
        
        self.stamina = 100.0
        self.max_stamina = 100.0
        
        self.winner = None
        self.game_state = "PLAYING"
        self.ai_strength = 0.35
        self.ai_cycle_time = 0.0
        self.ai_phase = "SURGE"
        self.ai_previous_phase = "SURGE"
        self.counter_surge_window_remaining = 0.0
        self.counter_surge_time_remaining = 0.0
        
        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:
            if self.stamina <= 10:
                return
                
            if event.key == pygame.K_LEFT:
                if self.last_key != pygame.K_LEFT: 
                    if (
                        self.counter_surge_window_remaining > 0.0
                        and self.counter_surge_time_remaining <= 0.0
                    ):
                        self.counter_surge_time_remaining = self.COUNTER_SURGE_DURATION
                        self.counter_surge_window_remaining = 0.0
                    push_strength = self.PLAYER_PUSH_STRENGTH
                    if self.counter_surge_time_remaining > 0.0:
                        push_strength *= self.COUNTER_SURGE_PUSH_MULTIPLIER
                    self.arm_position -= push_strength
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_LEFT
            elif event.key == pygame.K_RIGHT:
                if self.last_key != pygame.K_RIGHT: 
                    if (
                        self.counter_surge_window_remaining > 0.0
                        and self.counter_surge_time_remaining <= 0.0
                    ):
                        self.counter_surge_time_remaining = self.COUNTER_SURGE_DURATION
                        self.counter_surge_window_remaining = 0.0
                    push_strength = self.PLAYER_PUSH_STRENGTH
                    if self.counter_surge_time_remaining > 0.0:
                        push_strength *= self.COUNTER_SURGE_PUSH_MULTIPLIER
                    self.arm_position -= push_strength
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_RIGHT

    def update(self):
        if self.game_state != "PLAYING":
            return

        cycle_duration = self.AI_SURGE_DURATION + self.AI_COOLDOWN_DURATION
        self.ai_previous_phase = self.ai_phase
        self.ai_cycle_time = (self.ai_cycle_time + self.AI_TIME_STEP) % cycle_duration
        if self.ai_cycle_time < self.AI_SURGE_DURATION:
            self.ai_phase = "SURGE"
            ai_multiplier = self.AI_SURGE_MULTIPLIER
        else:
            self.ai_phase = "COOLDOWN"
            ai_multiplier = self.AI_COOLDOWN_MULTIPLIER

        if self.counter_surge_window_remaining > 0.0:
            self.counter_surge_window_remaining = max(
                0.0,
                self.counter_surge_window_remaining - self.AI_TIME_STEP,
            )

        if self.counter_surge_time_remaining > 0.0:
            self.counter_surge_time_remaining = max(
                0.0,
                self.counter_surge_time_remaining - self.AI_TIME_STEP,
            )

        if self.ai_previous_phase == "SURGE" and self.ai_phase == "COOLDOWN":
            self.counter_surge_window_remaining = self.COUNTER_SURGE_WINDOW

        ai_variance = random.uniform(0.3, 1.0)
        self.arm_position += self.ai_strength * ai_multiplier * ai_variance

        if self.stamina < self.max_stamina:
            recovery = self.NORMAL_STAMINA_RECOVERY
            if self.counter_surge_time_remaining > 0.0:
                recovery = self.COUNTER_SURGE_STAMINA_RECOVERY
            self.stamina = min(self.max_stamina, self.stamina + recovery)

        if self.arm_position <= -self.target_limit:
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"
        elif self.arm_position >= self.target_limit:
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"

    def reset(self):
        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self.ai_cycle_time = 0.0
        self.ai_phase = "SURGE"
        self.ai_previous_phase = "SURGE"
        self.counter_surge_window_remaining = 0.0
        self.counter_surge_time_remaining = 0.0

    def render(self, screen):
        screen.fill((25, 28, 35))

        title_surf = self.font_big.render("ARM WRESTLE SHOWDOWN", True, (240, 240, 240))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 12))

        player_header = self.font_med.render("PLAYER", True, (80, 160, 255))
        computer_header = self.font_med.render("COMPUTER", True, (255, 100, 80))
        screen.blit(player_header, (60, 55))
        screen.blit(computer_header, (self.width - 150, 55))

        table_rect = pygame.Rect(40, 100, self.width - 80, 310)
        pygame.draw.rect(screen, (110, 50, 15), table_rect, border_radius=14)
        pygame.draw.rect(screen, (70, 30, 8), table_rect, width=5, border_radius=14)

        pygame.draw.line(screen, (45, 18, 4), (self.width // 2, 100), (self.width // 2, 410), 4)

        offset_x = (self.arm_position / self.target_limit) * 95
        hand_x = (self.width // 2) + int(offset_x)
        hand_y = 235

        p_shoulder = (70, 330)
        p_elbow = (140, 215)
        c_shoulder = (self.width - 70, 330)
        c_elbow = (self.width - 140, 215)

        pygame.draw.line(screen, (200, 145, 110), p_shoulder, p_elbow, 32)
        pygame.draw.line(screen, (215, 160, 125), p_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (185, 130, 95), p_elbow, 18)

        pygame.draw.line(screen, (170, 110, 85), c_shoulder, c_elbow, 32)
        pygame.draw.line(screen, (185, 125, 95), c_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (150, 95, 70), c_elbow, 18)

        pygame.draw.circle(screen, (225, 175, 140), (hand_x, hand_y), 24)
        pygame.draw.circle(screen, (160, 115, 85), (hand_x, hand_y), 24, width=3)

        stamina_label = self.font_med.render("STAMINA", True, (220, 220, 220))
        screen.blit(stamina_label, (40, 445))

        stamina_bg = pygame.Rect(140, 448, 240, 22)
        stamina_fill = pygame.Rect(140, 448, int(240 * (self.stamina / self.max_stamina)), 22)
        pygame.draw.rect(screen, (45, 50, 60), stamina_bg, border_radius=6)
        bar_color = (60, 210, 100) if self.stamina > 25 else (220, 60, 60)
        pygame.draw.rect(screen, bar_color, stamina_fill, border_radius=6)

        if self.game_state == "PLAYING":
            if self.ai_phase == "SURGE":
                surge_warning = self.font_med.render(
                    "COMPUTER SURGE - PUSH HARD!", True, (255, 210, 60)
                )
                surge_rect = surge_warning.get_rect(
                    center=(self.width // 2, 495)
                )
                pygame.draw.rect(screen, (55, 42, 15), surge_rect.inflate(18, 8), border_radius=6)
                screen.blit(surge_warning, surge_rect)

            if self.stamina <= 10:
                exhaustion_warning = self.font_med.render(
                    "EXHAUSTED - RECOVERING STAMINA", True, (255, 100, 100)
                )
                exhaustion_rect = exhaustion_warning.get_rect(
                    center=(self.width // 2, 530)
                )
                pygame.draw.rect(
                    screen,
                    (60, 22, 28),
                    exhaustion_rect.inflate(18, 8),
                    border_radius=6,
                )
                screen.blit(exhaustion_warning, exhaustion_rect)

            if self.counter_surge_time_remaining > 0.0:
                comeback_warning = self.font_med.render(
                    "COMEBACK BONUS - 2X PUSH!", True, (100, 240, 140)
                )
                comeback_rect = comeback_warning.get_rect(
                    center=(self.width // 2, 565)
                )
                pygame.draw.rect(
                    screen,
                    (18, 65, 38),
                    comeback_rect.inflate(18, 8),
                    border_radius=6,
                )
                screen.blit(comeback_warning, comeback_rect)

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            win_text = "PLAYER WINS THE MATCH!" if self.winner == "PLAYER" else "COMPUTER WINS!"
            color = (80, 240, 100) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 45)
            )

            restart_surf = self.font_med.render(
                "Press [R] to Rematch", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10)
            )
