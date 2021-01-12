import pygame

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 900
TIMER_EVENT_TYPE = 30


class Clicker:
    def __init__(self):
        self.min_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 10
        self.max_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 5
        self.radius = self.min_radius
        self.centre = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.delay = 100
        pygame.time.set_timer(TIMER_EVENT_TYPE, self.delay)

    def render(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), self.centre, self.radius)

    def check_click(self, position):
        x, y = position
        cntr_x, cntr_y = self.centre
        d = self.radius ** 2 - ((cntr_x - x) ** 2 + (cntr_y - y) ** 2)
        if d >= 0:
            self.radius = min(self.radius + 2, self.max_radius)
            pygame.time.set_timer(TIMER_EVENT_TYPE, self.delay)

    def lose_mass(self):
        self.radius = max(self.radius - 1, self.min_radius)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)

    clicker = Clicker()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicker.check_click(event.pos)
            if event.type == TIMER_EVENT_TYPE:
                clicker.lose_mass()
        screen.fill((0, 0, 0))
        clicker.render(screen)
        pygame.display.flip()
    pygame.quit()
