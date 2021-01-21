import pygame
import dbSaver

pygame.init()
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.Info().current_w, \
                                            pygame.display.Info().current_h
print(pygame.display.Info().current_w, pygame.display.Info().current_h)
# Игорейсовский компец 1366 768

SURFACE = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
pygame.quit()
TIMER_EVENT = pygame.USEREVENT + 1
AUTO_CLICK_EVENT = pygame.USEREVENT + 2


def to_fixed(num_obj, digits=0):
    return f"{num_obj:.{digits}f}"


class Clicker:
    def __init__(self, values=None):
        if values is None:
            self.is_paused = False
            self.score = 0
            self.money = 100.0
            self.click = 1
            self.click_money = 0.2
            self.cps = 0.5  # клики в секунду (clicks per second)
            self.skin_path = None
        else:
            self.is_paused, self.score, self.money, self.click, self.click_money, self.cps, self.skin_path = values
        # self.min_radius, self.max_radius, self.radius - это значения
        # для размеров скелета кликера.
        self.font_size = WINDOW_HEIGHT // 26
        self.min_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 10
        self.max_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 5
        self.radius = self.min_radius
        self.centre = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.delay = 75
        # self.min_skin_size, self.max_skin_size, self.skin_size - это
        # аналоги значений скелета кликера, но уже для скина.
        self.skin_copy = None
        self.skin = None
        self.min_skin_size = (self.min_radius * 2, self.min_radius * 2)
        self.max_skin_size = (self.max_radius * 2, self.max_radius * 2)
        self.skin_size = (self.radius * 2, self.radius * 2)
        pygame.time.set_timer(TIMER_EVENT, self.delay)
        pygame.time.set_timer(AUTO_CLICK_EVENT, 1000)

    def render(self, screen):
        # 1)=============КЛИКИ==============
        font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        font_color = (200, 200, 200)
        text = font.render(f'Клики: {int(self.score)}', True, font_color)
        screen.blit(text, (40, WINDOW_HEIGHT // 20))
        # ==================================

        # 2)=============МОНЕТЫ=============
        font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        font_color = (200, 200, 0)
        text = font.render(f'Монеты: {int(self.money)}', True, font_color)
        screen.blit(text, (40, WINDOW_HEIGHT // 20 * 2))
        # ==================================

        # 3)==============СКИН==============
        if self.skin_path is None:
            pygame.draw.circle(screen, (255, 0, 0), self.centre, self.radius)
        if self.skin is None and self.skin_path is not None:
            self.skin = pygame.image.load(self.skin_path)
        if self.skin is not None:
            self.skin_copy = pygame.transform.scale(self.skin, self.skin_size)
            screen.blit(self.skin_copy,
                        (self.centre[0] - self.radius, self.centre[1] - self.radius))
        # ==================================

        # 4)========КЛИКИ В СЕКУНДУ=========
        if self.cps:
            font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
            font_color = (200, 200, 200)
            text = font.render(f'Клики в секунду: {to_fixed(self.cps, 2)}', True,
                               font_color)
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
        self.skin_path = skin

    def to_save_info(self):
        """Метод этого класса вернёт список с информацией о данном классе (нужна для работы с БД)"""
        return [self.is_paused, self.score, self.money, self.click, self.click_money, self.cps,
                self.skin_path]


class Button:
    """Класс кнопки"""

    def __init__(self, form, position, text='', cursor_pos=(None, None), text_coords=(None, None),
                 click_event=False):
        """Инициализация и отрисовка кнопки на форме"""
        # self, форма на которой рисуется кнопка, координаты верхней левой и правой нижней точек
        # кнопки, позиция курсора в данный момент, текст кнопки и его координаты,
        # факт нажатия на кнопку
        self.title = text
        self.x, self.y, self.width, self.height = position
        self.click_event = click_event
        self.cursor_pos = cursor_pos
        self.form = form
        self.font_color = (255, 255, 255)
        self.font_size = 24
        self.active_clr = (42, 82, 190, 100)
        self.alpha = 255
        self.border_color = 'black'
        self.pause_button_size = WINDOW_WIDTH // 3, WINDOW_HEIGHT // 13.32
        self.coeff_x, self.coeff_y = 0, 0

        self.install_event_filter()

        pygame.draw.rect(self.form,
                         self.active_clr,
                         (self.x, self.y,
                          self.width, self.height),
                         width=0,
                         border_radius=15)
        pygame.draw.rect(self.form,
                         self.border_color,
                         (self.x, self.y,
                          self.width, self.height),
                         width=self.width // (self.width // 5),
                         border_radius=self.width // (self.width // 15))

        self.font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        self.text = self.font.render(text, True, self.font_color)
        screen.blit(self.text, (text_coords[0] - self.coeff_x // 5 * len(text[0]) // 2,
                                text_coords[1] - self.coeff_y // 5 * 2))
        # self.active_clr = (255, 255, 255, self.alpha)
        # self.font_color = (42, 82, 190, self.alpha) ----Убрать!!

    def install_event_filter(self):
        """EventFilter, в котором происходит обработка событий"""
        if self.check_button_enter(self.cursor_pos, (self.x, self.y,
                                                     self.x + self.width,
                                                     self.y + self.height)):
            self.coeff_x = 25
            self.coeff_y = 10
            self.x -= self.coeff_x
            self.y -= self.coeff_y
            self.width += self.coeff_x * 2
            self.height += self.coeff_y * 2
            self.font_size = self.font_size + self.coeff_x // 5
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.active_clr = (255, 255, 255, self.alpha)
                self.font_color = (42, 82, 190, self.alpha)
                if self.title == 'Продолжить игру':
                    clicker.switch_pause()
                elif self.title == 'Выйти':
                    pygame.quit()
                elif self.title == 'Настройки':
                    print('Настройки в разработке..')
                elif self.title == 'Магазин':
                    global right_menu_is_showing
                    if not right_menu_is_showing and click_timer():
                        right_menu_is_showing = True
                    elif click_timer():
                        right_menu_is_showing = False
            if event.type == pygame.MOUSEMOTION:
                self.font_color = (255, 255, 255)
                self.active_clr = (42, 82, 190, self.alpha)
            if event.type == pygame.MOUSEBUTTONUP:
                self.font_color = (255, 255, 255)
                self.active_clr = (42, 82, 190, self.alpha)

    def check_button_enter(self, click_pos, button_pos):
        """Функция проверяет наличие над кнопкой курсора"""
        if click_pos is None:
            return False
        x, y = click_pos
        x1, y1, x2, y2 = button_pos
        if x in range(int(x1), int(x2)) and y in range(int(y1), int(y2)):
            return True
        return False


class Pause:
    def __init__(self):
        self.active_clr = (61, 0, 153, 10)

    def render(self):
        self.font_size = WINDOW_WIDTH // (WINDOW_WIDTH // 24)
        self.font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        self.font_color = (255, 255, 255)
        text = self.font.render('Игра на паузе', True, self.font_color)

        SURFACE.fill((100, 100, 100, 100))
        SURFACE.blit(text, (WINDOW_WIDTH // (WINDOW_WIDTH // 40),
                            WINDOW_HEIGHT // WINDOW_HEIGHT // 120))
        self.pause_button_size = WINDOW_WIDTH // 3, WINDOW_HEIGHT // 13.32
        self.buttons_titles = {
            0: ('Продолжить игру', 250, (550, 260)),
            1: ('Настройки', 350, (590, 360)),
            2: ('Выйти', 450, (610, 460))
        }
        self.draw_buttons()
        return SURFACE

    def draw_buttons(self):
        """Функция рисует кнопки в меню паузы"""
        for i in range(3):
            Button(screen, (WINDOW_WIDTH // 3.3,
                            self.buttons_titles[i][1],
                            self.pause_button_size[0],
                            self.pause_button_size[1]),
                   text=(self.buttons_titles[i][0]),
                   text_coords=self.buttons_titles[i][-1],
                   cursor_pos=(x, y))

    def check_button_enter(self, click_pos, button_pos):
        """Функция проверяет наличие курсора в поле кнопки"""
        x, y = click_pos
        x1, y1, x2, y2 = button_pos
        if x in range(int(x1), int(x2)) and y in range(int(y1), int(y2)):
            return True
        return False


class RightMenu:
    def __init__(self):
        self.width, self.height = WINDOW_WIDTH // 3, WINDOW_HEIGHT - 50
        self.color = (20, 20, 20)
        self.pos = (WINDOW_WIDTH - WINDOW_WIDTH // 3, 25)
        points = [(self.pos[0] + 100, self.pos[1]), (self.pos[0], self.pos[1] + self.height),
                  (self.pos[0] + self.width, self.pos[1] + self.height),
                  (self.pos[0] + self.width, self.pos[1])]
        pygame.draw.polygon(screen, self.color, points, width=0)
        skins_button = Button(screen, (self.pos[0] - 25, self.pos[1] + 655, 210, 75),
                              text='Скины', text_coords=(self.pos[0] + 50, self.pos[1] + 655 + 20),
                              cursor_pos=(x, y))
        boosters_button = Button(screen, (self.pos[0] + 225, self.pos[1] + 655, 210, 75),
                                 text='Ускорители',
                                 text_coords=(self.pos[0] + 285, self.pos[1] + 655 + 20),
                                 cursor_pos=(x, y))


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


def click_timer():
    global clock
    result = True if clock.tick() / 1000 > 0.1 else False
    if not result:
        return result
    clock = pygame.time.Clock()
    return result


if __name__ == '__main__':
    pygame.init()
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Clicker')
    try:
        data = dbSaver.download('data/save_data_1.db')
        clicker = Clicker(data)
    except FileNotFoundError:
        clicker = Clicker()
    pause = Pause()
    shop = Shop()
    clicker.set_skin('Skins/github_easter_egg.png')
    print(clicker.to_save_info())

    running = True
    right_menu_is_showing = False
    image2 = False
    take_pause = False
    click = False
    x, y = None, None

    # image = pygame.image.load("Skins\cursor_green.png")
    image = pygame.image.load('Skins\cursor_blue.png')

    clock = pygame.time.Clock()

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                clicker.is_paused = False
                dbSaver.upload('data/save_data_1.db', clicker.to_save_info())
                running = False
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                take_pause = False
                if clicker.is_paused:
                    take_pause = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                image2 = pygame.image.load("Skins\click_effect.png")
                click = False
                if clicker.is_paused:
                    click = True
            if event.type == pygame.MOUSEBUTTONUP:
                # image = pygame.image.load("Skins\cursor_green.png")
                image = pygame.image.load("Skins\cursor_blue.png")
                image2 = False
            if clicker.is_paused:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and click_timer():
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
        shop_button = Button(screen, (50, 665, 200, 75), text='Магазин', cursor_pos=(x, y),
                             text_coords=(105, 665 + 20))
        # shop.render(screen)
        if clicker.is_paused:
            if take_pause:
                screen.blit(pause.render(), (0, 0))
            else:
                screen.blit(pause.render(), (0, 0))
        if right_menu_is_showing:
            right_menu = RightMenu()

        if image:
            image = pygame.transform.scale(image, (WINDOW_WIDTH // 26, WINDOW_HEIGHT // 20))
            screen.blit(image, (x - WINDOW_WIDTH // 26 // 3, y - WINDOW_HEIGHT // 20 // 3))
        if image2:
            image2 = pygame.transform.scale(image2, (WINDOW_WIDTH // 26, WINDOW_HEIGHT // 20))
            screen.blit(image2, (x - WINDOW_WIDTH // 26 // 3, y - WINDOW_HEIGHT // 20 // 3))

        pygame.display.flip()
    pygame.quit()
