import pygame

pygame.init()
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.Info().current_w, \
                                            pygame.display.Info().current_h
print(pygame.display.Info().current_h, pygame.display.Info().current_w)
pygame.quit()
TIMER_EVENT = pygame.USEREVENT + 1
AUTO_CLICK_EVENT = pygame.USEREVENT + 2


def to_fixed(num_obj, digits=0):
    return f"{num_obj:.{digits}f}"


class Clicker:
    def __init__(self):
        # self.min_radius, self.max_radius, self.radius - это значения
        # для размеров скелета кликера.
        self.min_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 10
        self.max_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 5
        self.radius = self.max_radius
        self.centre = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.is_paused = False
        self.delay = 75
        pygame.time.set_timer(TIMER_EVENT, self.delay)
        pygame.time.set_timer(AUTO_CLICK_EVENT, 1000)
        self.score = 0
        self.money = 100.0
        self.click = 1
        self.click_money = 0.2
        self.cps = 0.5  # клики в секунду (clicks per second)
        self.skin = None
        self.skin_copy = None
        # self.min_skin_size, self.max_skin_size, self.skin_size - это
        # аналоги значений скелета кликера, но уже для скина.
        self.min_skin_size = (self.min_radius * 2, self.min_radius * 2)
        self.max_skin_size = (self.max_radius * 2, self.max_radius * 2)
        self.skin_size = (self.radius * 2, self.radius * 2)

    def render(self, screen):
        # 1)=============КЛИКИ==============
        self.font_size = WINDOW_HEIGHT // 26
        self.font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        self.font_color = (200, 200, 200)
        text = self.font.render(f'Клики: {int(self.score)}', True, self.font_color)
        screen.blit(text, (40, WINDOW_HEIGHT // 20))
        # ==================================

        # 2)=============МОНЕТЫ=============
        self.font_size = WINDOW_HEIGHT // 26
        self.font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        self.font_color = (200, 200, 0)
        text = self.font.render(f'Монеты: {int(self.money)}', True, self.font_color)
        screen.blit(text, (40, WINDOW_HEIGHT // 20 * 2))
        # ==================================

        # 3)==============СКИН==============
        if self.skin_copy is not None:
            screen.blit(self.skin_copy, (
                self.centre[0] - self.radius, self.centre[1] - self.radius))
        else:
            pygame.draw.circle(screen, (255, 0, 0), self.centre, self.radius)
        # ==================================

        # 4)========КЛИКИ В СЕКУНДУ=========
        if self.cps:
            self.font_size = WINDOW_HEIGHT // 26
            self.font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
            self.font_color = (200, 200, 200)
            text = self.font.render(f'Клики в секунду: {to_fixed(self.cps, 2)}', True,
                                    self.font_color)
            screen.blit(text, (40, WINDOW_HEIGHT // 20 * 3))
        # ==================================

    def check_click(self, position):
        """Проверка на то, что клик был сделан в пределах круга.
         Увеличивает радиус круга (анимация)"""
        x, y = position
        centre_x, centre_y = self.centre
        d = self.radius ** 2 - ((centre_x - x) ** 2 + (centre_y - y) ** 2)
        if d >= 0:
            self.radius = min(self.radius + 2, self.max_radius)
            self.skin_size = (self.radius * 2, self.radius * 2)
            self.add_score()
            self.add_money()
            if self.skin is not None:
                self.skin_copy = pygame.transform.scale(self.skin, self.skin_size)

    def lose_mass(self):
        """Уменьшает радиус круга со временем (анимация)"""
        self.radius = max(self.radius - 1, self.min_radius)
        self.skin_size = (self.radius * 2, self.radius * 2)
        if self.skin is not None:
            self.skin_copy = pygame.transform.scale(self.skin, self.skin_size)

    def switch_pause(self):
        """Включает/выключает паузу (подробнее в классе Pause)"""
        self.is_paused = not self.is_paused
        pygame.time.set_timer(TIMER_EVENT, self.delay if not self.is_paused else 0)
        pygame.time.set_timer(AUTO_CLICK_EVENT, 1000 if not self.is_paused else 0)

    def add_score(self):
        self.score += self.click

    def add_money(self):
        self.money += self.click_money

    def auto_add(self):
        self.score += self.cps
        self.money += (self.cps / 5)

    def set_skin(self, skin=None):
        if skin is None:
            self.skin = skin
        else:
            self.skin = pygame.image.load(skin)


class Button:
    def __init__(self, form, position, enter_pos=None):
        x, y, w, h = position
        self.enter_pos = enter_pos
        self.form = form
        self.pause_button_size = WINDOW_WIDTH // 3, WINDOW_HEIGHT // 13.32
        self.font_size = 24
        self.active_clr = (61, 0, 153, 10)
        self.font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        self.font_color = (255, 255, 255)
        self.x, self.y = x, y
        self.width = w
        self.height = h
        coeff_x, coeff_y = 0, 0
        if self.enter_pos is not None:
            coeff_x = 25
            coeff_y = 10
        pygame.draw.rect(self.form,
                         self.active_clr,
                         (self.x - coeff_x, self.y - coeff_y,
                          self.width + coeff_x, self.height + coeff_y),
                         width=0,
                         border_radius=15)
        pygame.draw.rect(self.form,
                         (self.active_clr[0], self.active_clr[1], self.active_clr[2], 255),
                         (self.x, self.y, self.width, self.height),
                         width=5,
                         border_radius=15)

    def draw_button(self, num, entered=None):
        coeff_x, coeff_y = 0, 0
        if entered_button == entered and entered is not None:
            coeff_x = 25
            coeff_y = 10
        pygame.draw.rect(self.form, self.active_clr, (WINDOW_WIDTH // 3.3 - coeff_x,
                                                      self.buttons_titles[num][1]
                                                      - coeff_y,
                                                      self.pause_button_size[0] + coeff_x * 2,
                                                      self.pause_button_size[1] + coeff_y * 2),
                         width=0, border_radius=15)
        pygame.draw.rect(self.form, 'black', (WINDOW_WIDTH // 3.3 - coeff_x,
                                              self.buttons_titles[num][1]
                                              - coeff_y,
                                              self.pause_button_size[0] + coeff_x * 2,
                                              self.pause_button_size[1] + coeff_y * 2),
                         width=5, border_radius=15)
        text = self.font.render(self.buttons_titles[num][0], True, self.font_color)
        screen.blit(text, self.buttons_titles[num][2])

    def check_button_click(self, click_pos, button_pos):
        """Функция проверяет наличие курсора в поле кнопки"""
        x, y = click_pos
        x1, y1, x2, y2 = button_pos
        if x in range(int(x1), int(x2)) and y in range(int(y1), int(y2)):
            return True
        return False


class Pause:
    def __init__(self):
        self.active_clr = (61, 0, 153, 10)
        # self.width, self.height = WINDOW_WIDTH, WINDOW_HEIGHT

    def render(self, entered_btn=None):
        self.font_size = 24
        self.font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        self.font_color = (255, 255, 255)
        text = self.font.render('Игра на паузе', True, self.font_color)
        self.s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

        self.s.fill((0, 0, 0, 100))
        self.s.blit(text, (40, 120))
        self.pause_button_size = WINDOW_WIDTH // 3, WINDOW_HEIGHT // 13.32
        self.buttons_titles = {
            0: ('Продолжить игру', 250, (560, 260)),
            1: ('Настройки', 350, (595, 360)),
            2: ('Выйти', 450, (615, 460))
        }
        if entered_btn is None:
            self.draw_buttons()
        else:
            self.draw_buttons(entered=entered_btn)
        return self.s

    def draw_buttons(self, entered=None):
        for i in range(3):
            coeff_x, coeff_y = 0, 0
            if entered_button == entered and entered is not None:
                coeff_x = 25
                coeff_y = 10
            pygame.draw.rect(self.s, self.active_clr, (WINDOW_WIDTH // 3.3 - coeff_x,
                                                       self.buttons_titles[i][1]
                                                       - coeff_y,
                                                       self.pause_button_size[0] + coeff_x * 2,
                                                       self.pause_button_size[1] + coeff_y * 2),
                             width=0, border_radius=15)
            pygame.draw.rect(self.s, 'black', (WINDOW_WIDTH // 3.3 - coeff_x,
                                               self.buttons_titles[i][1]
                                               - coeff_y,
                                               self.pause_button_size[0] + coeff_x * 2,
                                               self.pause_button_size[1] + coeff_y * 2),
                             width=5, border_radius=15)
            text = self.font.render(self.buttons_titles[i][0], True, self.font_color)
            self.s.blit(text, self.buttons_titles[i][2])

    def check_button_click(self, click_pos, button_pos):
        """Функция проверяет наличие курсора в поле кнопки"""
        x, y = click_pos
        x1, y1, x2, y2 = button_pos
        if x in range(int(x1), int(x2)) and y in range(int(y1), int(y2)):
            return True
        return False


class Shop:
    def __init__(self):
        self.side = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 10
        self.ico = pygame.image.load('data/market.png')
        self.ico_size = self.ico_w, self.ico_h = self.ico.get_size()
        self.ico_copy = self.ico
        self.skins = {"blue_neon.png": 3500,
                      'earth.png': 5000,
                      'kolobok.png': 3000,
                      'purple_neon.png': 3000,
                      'save_point.png': 4000
                      }

        self.colors = {'red': 0,
                       'blue': 0,
                       'green': 0,
                       'light_gray': 300,
                       'gray': 300,
                       'dark_gray': 300,
                       }

        self.cursors = {}

        self.backgrounds = {}

        self.bought = []

    def buy(self, money, obj, category):
        if obj in self.bought:
            return True, money
        if category[obj] <= money:
            self.bought.append(obj)
            return True, money - category[obj]
        return False, money

    def render(self, screen):
        self.ico_copy = pygame.transform.scale(self.ico, (self.ico_w // 5, self.ico_h // 5))
        screen.blit(self.ico_copy, (int(WINDOW_WIDTH / 8 * 5), WINDOW_HEIGHT // 20))


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Clicker')
    clicker = Clicker()
    pause = Pause()
    shop = Shop()
    clicker.set_skin('Skins/github_easter_egg.png')

    running = True
    x, y = 0, 0
    # image = pygame.image.load("Skins\cursor_green.png")
    image = pygame.image.load('Skins\cursor_blue.png')
    pygame.mouse.set_visible(False)
    entered_button = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if clicker.is_paused:
                    entered_button = None
                    for i in range(3):
                        if pause.check_button_click((x, y), (pause.buttons_titles[i][-1][0],
                                                             pause.buttons_titles[i][-1][1],
                                                             pause.buttons_titles[i][-1][0] +
                                                             pause.pause_button_size[0],
                                                             pause.buttons_titles[i][-1][1] +
                                                             pause.pause_button_size[1])):
                            entered_button = i + 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                image = pygame.image.load("Skins\clicked_cursor_blue.png")
                # image = pygame.image.load("Skins\clicked_cursor_green.png")
            if event.type == pygame.MOUSEBUTTONUP:
                # image = pygame.image.load("Skins\cursor_green.png")
                image = pygame.image.load("Skins\cursor_blue.png")
            if clicker.is_paused:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        clicker.switch_pause()
                        pygame.display.set_caption('Clicker')
            else:
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    clicker.check_click(event.pos)
                if event.type == TIMER_EVENT:
                    clicker.lose_mass()
                if event.type == AUTO_CLICK_EVENT:
                    clicker.auto_add()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        clicker.switch_pause()
                        pygame.display.set_caption('Clicker (paused)')
        screen.fill((50, 50, 50))
        clicker.render(screen)
        shop.render(screen)
        if clicker.is_paused:
            if entered_button is not None:
                screen.blit(pause.render(entered_btn=entered_button), (0, 0))
            else:
                screen.blit(pause.render(), (0, 0))

        if image:
            image = pygame.transform.scale(image, (WINDOW_WIDTH // 26, WINDOW_HEIGHT // 20))
        screen.blit(image, (x - WINDOW_WIDTH // 26 // 3, y - WINDOW_HEIGHT // 20 // 3))

        pygame.display.flip()
    pygame.quit()
