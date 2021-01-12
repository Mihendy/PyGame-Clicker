import pygame

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 900
TIMER_EVENT_TYPE = 30


class Clicker:
    def __init__(self):
        self.min_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 10
        self.max_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 5
        self.radius = self.min_radius
        self.centre = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.is_paused = False
        self.delay = 75
        pygame.time.set_timer(TIMER_EVENT_TYPE, self.delay)
        self.score = 0
        self.money = 100.0
        self.click = 1
        self.click_money = 0.2

    def render(self, screen):
        # ==============ОЧКИ==============
        font_size = 24
        font = pygame.font.Font("Fonts/beer money.ttf", font_size)
        font_color = (200, 200, 200)
        text = font.render(f'Очки: {self.score}', 1, font_color)
        screen.blit(text, (40, 40))
        # ================================
        # =============МОНЕТЫ=============
        font_size = 24
        font = pygame.font.Font("Fonts/beer money.ttf", font_size)
        font_color = (200, 200, 0)
        text = font.render(f'Монеты: {int(self.money)}', 1, font_color)
        screen.blit(text, (40, 80))
        # ================================
        pygame.draw.circle(screen, (255, 0, 0), self.centre, self.radius)

    def check_click(self, position):
        """Проверка на то, что клик был сделан в пределах круга. Увеличивает радиус круга (анимация)"""
        x, y = position
        centre_x, centre_y = self.centre
        d = self.radius ** 2 - ((centre_x - x) ** 2 + (centre_y - y) ** 2)
        if d >= 0:
            self.radius = min(self.radius + 2, self.max_radius)

    def lose_mass(self):
        """Уменьшает радиус круга со временем (анимация)"""
        self.radius = max(self.radius - 1, self.min_radius)

    def switch_pause(self):
        """Включает/выключает паузу (подробнее в классе Pause)"""
        self.is_paused = not self.is_paused
        pygame.time.set_timer(TIMER_EVENT_TYPE, self.delay if not self.is_paused else 0)

    def add_score(self):
        self.score += self.click

    def add_money(self):
        self.money += self.click_money


class Pause:
    def __init__(self):
        self.width, self.height = WINDOW_WIDTH, WINDOW_HEIGHT

    def render(self):
        font_size = 24
        font = pygame.font.Font("Fonts/beer money.ttf", font_size)
        font_color = (255, 255, 255)
        text = font.render('Игра на паузе', 1, font_color)
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        s.fill((100, 100, 100, 100))
        s.blit(text, (40, 120))
        return s


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Clicker')
    clicker = Clicker()
    pause = Pause()

    running = True
    while running:
        for event in pygame.event.get():
            if clicker.is_paused:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        clicker.switch_pause()
                        pygame.display.set_caption('Clicker')
            else:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clicker.check_click(event.pos)
                    clicker.add_money()
                    clicker.add_score()
                if event.type == TIMER_EVENT_TYPE:
                    clicker.lose_mass()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        clicker.switch_pause()
                        pygame.display.set_caption('Clicker (paused)')
        screen.fill((50, 50, 50))
        clicker.render(screen)
        if clicker.is_paused:
            screen.blit(pause.render(), (0, 0))
        pygame.display.flip()
    pygame.quit()
