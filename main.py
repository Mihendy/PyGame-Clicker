import pygame
import json
import os

# =========Эта часть кода определяет размер окна пользователя============
pygame.init()
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.Info().current_w, \
                                            pygame.display.Info().current_h
print(pygame.display.Info().current_w, pygame.display.Info().current_h)
SURFACE = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
pygame.quit()
# =========Эта часть кода определяет размер окна пользователя============

# =========Эта часть кода определяет константы, необходимые для работы программы============
COLORS = {
    'blue azure': (42, 82, 190),  # Цвет заполнения заднего фона элементов интерфейса (кнопки).
    'black': (0, 0, 0),  # Цвет border элементов интерфейса.
    'white-white': (200, 200, 200),  # Цвет шрифта.
    'yellow-yellow': (200, 200, 0),  # Цвет шрифта.
    'dark gray': (20, 20, 20)  # Цвет магазина.
}
TIMER_EVENT = pygame.USEREVENT + 1
AUTO_CLICK_EVENT = pygame.USEREVENT + 2
TIMER_EVENT_DELAY = 75
AUTO_CLICK_DELAY = 1000
SKINS_SHOWING = True
cursor_clicked = False
# =========Эта часть кода определяет константы, необходимые для работы программы============


def is_mouse_enter(button_pos):
    """Функция проверяет наличие над объектом курсора"""
    x1, y1, x2, y2 = button_pos
    if x in range(int(x1), int(x2)) and y in range(int(y1), int(y2)):
        return True
    return False


def to_fixed(num_obj, digits=0):
    """ Функция ограничения знаков после запятой у float"""
    return f"{num_obj:.{digits}f}"


class Clicker:
    """Класс кликера (кружочка на основе которого построена игра)"""

    def __init__(self, values=None):
        if values is None:
            self.is_paused = False
            self.score = 0
            self.money = 100.0
            self.click = 1
            self.cps = 0.0  # клики в секунду (clicks per second)
            self.skin_path = None
            self.color = 'red'
        else:
            self.is_paused, self.score, self.money, self.click, \
            self.cps, self.skin_path, self.color = values
        self.money = float(self.money)
        # self.min_radius, self.max_radius, self.radius - это значения для размеров скелета кликера.
        self.font_size = WINDOW_HEIGHT // 26
        self.min_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 10
        self.max_radius = min(WINDOW_WIDTH, WINDOW_HEIGHT) // 5
        self.radius = self.min_radius
        self.centre = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        # self.min_skin_size, self.max_skin_size, self.skin_size - это
        # аналоги значений скелета кликера, но уже для скина.
        self.skin_copy = None
        self.skin = None
        self.min_skin_size = (self.min_radius * 2, self.min_radius * 2)
        self.max_skin_size = (self.max_radius * 2, self.max_radius * 2)
        self.skin_size = (self.radius * 2, self.radius * 2)

    def render(self, screen):
        """ Вывод результата вычислений на экран"""
        # 1)=============КЛИКИ==============
        font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        font_color = COLORS['white-white']
        text = font.render(f'Клики: {int(self.score)}', True, font_color)
        screen.blit(text, (40, WINDOW_HEIGHT // 20))
        # ==================================

        # 2)=============МОНЕТЫ=============
        font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        font_color = COLORS['yellow-yellow']
        text = font.render(f'Монеты: {int(self.money)}', True, font_color)
        screen.blit(text, (40, WINDOW_HEIGHT // 20 * 2))
        # ==================================

        # 3)==============СКИН==============
        if self.skin_path == 'None':
            self.skin_path = None
        if self.skin_path is None:
            pygame.draw.circle(screen, self.color, self.centre, self.radius)
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
            font_color = COLORS['white-white']
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
            self.add()
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
        pygame.time.set_timer(TIMER_EVENT, TIMER_EVENT_DELAY if not self.is_paused else 0)
        pygame.time.set_timer(AUTO_CLICK_EVENT, AUTO_CLICK_DELAY if not self.is_paused else 0)

    def add(self):
        """Добавляет деньги и клики (в игровом цикле сработает,
                если нажать ЛКМ в круге)"""
        self.score += self.click
        self.money += self.click / 5

    def auto_add(self):
        """Добавляет деньги и клики каждую секунду без участья игрока
                (в игровом цикле сработает,если выйдет таймер)"""
        self.score += self.cps
        self.money += (self.cps / 5)

    def set_skin(self, skin=None):
        """Метод меняет скин кликера"""
        self.skin_path = skin
        self.skin = None
        self.skin_copy = None

    def to_save_info(self):
        """Метод этого класса вернёт список с информацией о данном классе
                (нужен для работы с сохранениями)"""
        return [self.is_paused, self.score, to_fixed(self.money, 3), self.click, self.cps,
                self.skin_path, self.color]


class Button:
    """Класс кнопки"""

    def __init__(self, form, position, text=''):
        """Инициализация и отрисовка кнопки на форме"""
        # +++ О аргументах, передаваемых в "__init__" +++
        # self, форма на которой рисуется кнопка, координаты верхней левой и правой нижней точек
        # кнопки, позиция курсора в данный момент, текст кнопки и его координаты,

        self.title = text
        self.x, self.y, self.width, self.height = position
        self.form = form
        self.alpha = 255
        self.active_clr = (*COLORS['blue azure'], self.alpha)
        self.font_color = COLORS['white-white']
        self.font_size = WINDOW_WIDTH // (WINDOW_WIDTH // 24)
        self.border_color = COLORS['black']
        self.pause_button_size = WINDOW_WIDTH // 3, WINDOW_HEIGHT // 13.32
        self.coeff_x, self.coeff_y = 0, 0

        self.install_event_filter()
        pygame.draw.rect(self.form,
                         self.active_clr,
                         (self.x + self.width // (self.width // 3),
                          self.y + self.width // (self.width // 3),
                          self.width - self.width // (self.width // 3) * 2,
                          self.height - self.width // (self.width // 3) * 2),
                         width=0,
                         border_radius=WINDOW_HEIGHT // (WINDOW_HEIGHT // 15))
        pygame.draw.rect(self.form,
                         self.border_color,
                         (self.x, self.y,
                          self.width, self.height),
                         width=self.width // (self.width // 5),
                         border_radius=self.width // (self.width // 15))

        self.font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        self.text = self.font.render(text, True, self.font_color)
        screen.blit(self.text, (self.x + ((self.width - self.text.get_width()) // 2),
                                self.y + ((self.height - self.text.get_height()) // 2)))

    def is_button_enter(self):
        """Метод проверяет наличие над кнопкой курсора"""
        x1, y1, x2, y2 = self.x, self.y, self.x + self.width, self.y + self.height
        if x in range(int(x1), int(x2)) and y in range(int(y1), int(y2)):
            return True
        return False

    def install_event_filter(self):
        """EventFilter, в котором происходит обработка событий
        (Кастомизация кнопки при нажатии и наведении.)"""
        global x, y
        if self.is_button_enter():
            self.coeff_x = WINDOW_WIDTH // (WINDOW_WIDTH // 25)
            self.coeff_y = WINDOW_WIDTH // (WINDOW_WIDTH // 10)
            self.x -= self.coeff_x
            self.y -= self.coeff_y
            self.width += self.coeff_x * 2
            self.height += self.coeff_y * 2
            self.font_size = self.font_size + self.coeff_x // 5
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.active_clr = (*COLORS['white-white'], self.alpha)
                self.font_color = (*COLORS['blue azure'], self.alpha)
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
                self.font_color = COLORS['white-white']
                self.active_clr = (*COLORS['blue azure'], self.alpha)


# class Settings:
#     def __init__(self):
#         global clock, IS_DARK_MODE, COLORS
#         self.alpha = 255
#         pygame.draw.rect(screen, COLORS[1], (WINDOW_WIDTH // (WINDOW_WIDTH // 100),
#                                              int(WINDOW_HEIGHT * 0.130),
#                                              WINDOW_WIDTH // (WINDOW_WIDTH // 1000),
#                                              int(WINDOW_HEIGHT * 0.651)),
#                          width=WINDOW_HEIGHT // (WINDOW_HEIGHT // 15),
#                          border_radius=WINDOW_HEIGHT // (WINDOW_HEIGHT // 15))
#         pygame.draw.rect(screen, COLORS[0], (WINDOW_WIDTH // (WINDOW_WIDTH // 100),
#                                              int(WINDOW_HEIGHT * 0.130),
#                                              WINDOW_WIDTH // (WINDOW_WIDTH // 1000),
#                                              int(WINDOW_HEIGHT * 0.651)),
#                          width=0,
#                          border_radius=WINDOW_HEIGHT // (WINDOW_HEIGHT // 15))
#         back_btn = Button(screen, (WINDOW_WIDTH // (WINDOW_WIDTH // 100),
#                                    int(WINDOW_HEIGHT * 0.130),
#                                    WINDOW_WIDTH // (WINDOW_WIDTH // 300),
#                                    int(WINDOW_HEIGHT * 0.651)), 'Назад')
#         if back_btn.is_button_enter() and event.type == pygame.MOUSEBUTTONDOWN:
#             global SETTINGS_IS_SHOWING
#             SETTINGS_IS_SHOWING = False
#         btn_text = 'Тёмная тема' if IS_DARK_MODE else 'Cветлая тема'
#         display_mode_btn = Button(screen, (WINDOW_WIDTH // (WINDOW_WIDTH // 400),
#                                            int(WINDOW_HEIGHT * 0.130),
#                                            WINDOW_WIDTH // (WINDOW_WIDTH // 300),
#                                            int(WINDOW_HEIGHT * 0.651)), btn_text)
#         if display_mode_btn.is_button_enter() and event.type == pygame.MOUSEBUTTONDOWN:
#             if IS_DARK_MODE:
#                 COLORS = ((20, 20, 20), (0, 0, 0), (200, 0, 0))
#             else:
#                 COLORS = ((42, 82, 190), (0, 0, 0), (255, 255, 255))
#             IS_DARK_MODE = not IS_DARK_MODE


class Pause:
    """ Класс окна паузы игры """

    def __init__(self):
        self.active_clr = (61, 0, 153, 10)
        self.font_size = WINDOW_WIDTH // (WINDOW_WIDTH // 24)
        self.pause_button_size = WINDOW_WIDTH // 3, WINDOW_HEIGHT // 13.32
        self.buttons_titles = {
            0: ('Продолжить игру', WINDOW_HEIGHT * 0.3417),
            1: ('Настройки', WINDOW_HEIGHT * 0.455),
            2: ('Выйти', WINDOW_HEIGHT * 0.4394)
        }

    def render(self):
        """Отрисовка окна паузы"""
        font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        font_color = (255, 255, 255)
        text = font.render('Игра на паузе', True, font_color)
        SURFACE.fill((100, 100, 100, 100))
        SURFACE.blit(text, (WINDOW_WIDTH // (WINDOW_WIDTH // 40),
                            WINDOW_HEIGHT // WINDOW_HEIGHT // 120))
        self.draw_buttons()
        return SURFACE

    def draw_buttons(self):
        """Отрисовка кнопок в меню паузы и реализация остановки или продолжения работы программы"""
        for i in range(3):
            if i == 1:
                continue
            btn = Button(screen, (WINDOW_WIDTH // 3.3,
                                  self.buttons_titles[i][1],
                                  self.pause_button_size[0],
                                  self.pause_button_size[1]), self.buttons_titles[i][0])
            if btn.is_button_enter() and event.type == pygame.MOUSEBUTTONDOWN:
                if i == 0:  # Кнопка продолжения игры
                    clicker.switch_pause()
                elif i == 2:  # Кнопка выхода из игры
                    global running
                    running = False


class RightMenu:
    """Класс тела магазина предметов"""

    def __init__(self):
        self.color = COLORS['dark gray']
        self.pos = (WINDOW_WIDTH - WINDOW_WIDTH // 3, WINDOW_HEIGHT // (WINDOW_HEIGHT // 25))
        self.button_pos = self.pos[:]

        # =============Координаты основного тела магазина==============
        self.main_points = [(int(WINDOW_WIDTH / 4 * 3 - A), 0),
                            (WINDOW_WIDTH - A, 0),
                            (WINDOW_WIDTH - A, WINDOW_HEIGHT),
                            (int(WINDOW_WIDTH / 1.5 - A), WINDOW_HEIGHT)]
        # =============Координаты основного тела магазина==============

        pygame.draw.polygon(screen, self.color, self.main_points,
                            width=0)  # Отрисовка тела магазина

        # =============Отрисовка приятной полоски сверху магазина==============
        pygame.draw.rect(screen, COLORS['white-white'],
                         (0 - A * 5, 0, WINDOW_WIDTH * 1.5, WINDOW_HEIGHT * 0.032))
        # =============Отрисовка приятной полоски сверху магазина==============

        # =============Отрисовка кнопки раздела скинов (кастомизации) элементов==============
        self.skins_button = Button(screen, (WINDOW_WIDTH / 1.55 - A * 2, WINDOW_HEIGHT / 1.14,
                                            int(WINDOW_WIDTH / 9), int(WINDOW_HEIGHT / 14)),
                                   'Скины')
        # =============Отрисовка кнопки раздела скинов (кастомизации) элементов==============

        # =============Отрисовка кнопки раздела ускорителей накопления кликов или монет=============
        self.boosters_button = Button(screen, (WINDOW_WIDTH / 1.25 - A * 2,
                                               WINDOW_HEIGHT / 1.14, int(WINDOW_WIDTH / 9),
                                               int(WINDOW_HEIGHT / 14)), 'Ускорители')
        # =============Отрисовка кнопки раздела ускорителей накопления кликов или монет=============

    def show_animation(self, items, colors, boosters):
        """Анимация показа магазина с предметами"""
        # Мы уделили побольше времени анимации, чем расчитывали, и сделали её приятнее,
        # задав элементам магазина разную скорость, а также мы организовали работу анимации в обе
        # стороны, чтобы смотрелось более реалистично.
        skins = items + colors
        points = []
        if SKINS_SHOWING:
            for i in range(len(skins)):
                y_coff = i // 3
                x_coff = i % 3
                w, h = WINDOW_WIDTH // 19, WINDOW_HEIGHT // 9
                x, y = (int(WINDOW_WIDTH / 4 * 3 + WINDOW_WIDTH // 40 + (WINDOW_WIDTH // 40 + w)
                            * x_coff - A), WINDOW_WIDTH // 40 + (h + WINDOW_WIDTH // 40) * y_coff)
                skins[i].render(screen, (x, y), (w, h))
                if isinstance(skins[i], ColorCell):
                    points.append((x, y, w, h, skins[i].color, skins[i].price))
                else:
                    points.append((x, y, w, h, skins[i].ico_name, skins[i].price))
            return points
        else:
            for i in range(len(boosters)):
                y_coff = i // 3
                x_coff = i % 3
                w, h = WINDOW_WIDTH // 19, WINDOW_HEIGHT // 9
                x, y = (int(WINDOW_WIDTH / 4 * 3 + WINDOW_WIDTH // 40 + (WINDOW_WIDTH // 40 + w)
                            * x_coff - A), WINDOW_WIDTH // 40 + (h + WINDOW_WIDTH // 40) * y_coff)
                boosters[i].render(screen, (
                    int(WINDOW_WIDTH / 4 * 3 + WINDOW_WIDTH // 40 + (
                            WINDOW_WIDTH // 40 + w) * x_coff - A),
                    WINDOW_WIDTH // 40 + (h + WINDOW_WIDTH // 40) * y_coff), (w, h))
                points.append((x, y, w, h, boosters[i].ico_name, boosters[i].price))
            return points


class Shop:
    """Класс прилавка с товарами (предметами) которые можно приобрести в магазине"""
    # в словариках будут находится предметы, которые можно купить

    def __init__(self, info=None):
        self.skins = {"blue_neon.png": 3500,
                      'earth.png': 5000,
                      'kolobok.png': 3000,
                      'purple_neon.png': 3000,
                      'save_point.png': 4000
                      }

        self.colors_dict = {'red': 0,
                            'blue': 0,
                            'green': 0,
                            'gray': 300,
                            }

        self.cursors = {}

        if info is not None:
            self.bought = info[0]
            self.boosters_dict = info[1]
        else:
            self.bought = []
            self.boosters_dict = {'clicks_per_click_x1.png': 50,
                                  'clicks_per_click_x10.png': 5500,
                                  'clicks_per_click_x100.png': 50000,
                                  'clicks_per_second_x0.01.png': 5,
                                  'clicks_per_second_x0.1.png': 105,
                                  'clicks_per_second_x0.5.png': 1000,
                                  'clicks_per_second_x5.png': 5000,
                                  'clicks_per_second_x10.png': 15000,
                                  'clicks_per_second_x100.png': 500000,
                                  }
        # распределение предметов
        self.items = []
        for k, v in self.skins.items():
            self.items.append(ItemCell(v, k, self.is_bought(k)))
        self.colors = []
        for k, v in self.colors_dict.items():
            self.colors.append(ColorCell(v, k, self.is_bought(k)))
            self.boosters = []
        for k, v in self.boosters_dict.items():
            self.boosters.append(ItemCell(v, k, False))

    def buy(self, money, obj, category):
        """Важнейший метод магазина, все транзакции проходят здесь :D"""
        if obj in self.bought:
            return True, money
        if category[obj] <= money:
            self.bought.append(obj)
            return True, money - category[obj]
        return False, money

    def is_bought(self, name):
        """Метод, проверяющий товар на то, что он уже куплен игроком"""
        return name in self.bought


class ItemCell:
    """ Класс ячейки товара (предмета) """

    def __init__(self, price, ico_name, is_bought):
        """В конструкторе этого класса передаются все необходимые значения для
         дальнейшей работы магазина (цена, товар, купален_или_нет)"""
        self.price, self.ico, self.is_bought, self.ico_name = price, pygame.image.load(
            f'Skins/{ico_name}'), is_bought, f'Skins/{ico_name}'

    def render(self, screen, pos, size):
        """Отображает ячейку товара"""
        width, height = size
        x, y = pos
        font = pygame.font.Font("Fonts/beer money.ttf", 18)
        text = font.render(str(self.price), True,
                           (50, 150, 50) if self.price <= MONEY else (150, 50, 50))
        ico = pygame.transform.scale(self.ico, (width, width))
        screen.blit(ico, (x, y))
        if not self.is_bought:
            screen.blit(text, (x + 5, y + width / 20 * 19))
            pygame.draw.rect(screen, (150, 150, 150), (x, y, width, height), 3)
        pygame.draw.rect(screen, (150, 150, 150), (x, y, width, width), 3)


class ColorCell:
    """ 'Потомак' предыдущего класса: похож по структуре, но они имеют мало общего"""
    def __init__(self, price, color, is_bought):
        self.price, self.color, self.is_bought = price, color, is_bought

    def render(self, screen, pos, size):
        """Отображает ячейку товара"""
        width, height = size
        x, y = pos
        font = pygame.font.Font("Fonts/beer money.ttf", 18)
        text = font.render(str(self.price), True,
                           (50, 150, 50) if self.price <= MONEY else (150, 50, 50))
        pygame.draw.ellipse(screen, self.color, (x, y, width, width))
        if not self.is_bought:
            screen.blit(text, (x + 5, y + width / 20 * 19))
            pygame.draw.rect(screen, (150, 150, 150), (x, y, width, height), 3)
        pygame.draw.rect(screen, (150, 150, 150), (x, y, width, width), 3)


def buy_booster():
    """ Совершение покупки ускорителя в магазине """
    if elem[4] == 'Skins/clicks_per_click_x1.png':
        shop.boosters_dict['clicks_per_click_x1.png'] = min(int(
            elem[-1] * 1.3), 9999999999999)
        clicker.money -= elem[-1]
        clicker.click += 1
    if elem[4] == 'Skins/clicks_per_click_x10.png':
        shop.boosters_dict['clicks_per_click_x10.png'] = min(int(
            elem[-1] * 1.3), 9999999999999)
        clicker.money -= elem[-1]
        clicker.click += 10
    if elem[4] == 'Skins/clicks_per_click_x100.png':
        shop.boosters_dict['clicks_per_click_x100.png'] = min(int(
            elem[-1] * 1.5), 9999999999999)
        clicker.money -= elem[-1]
        clicker.click += 100
    if elem[4] == 'Skins/clicks_per_second_x0.01.png':
        shop.boosters_dict['clicks_per_second_x0.01.png'] = min(int(
            elem[-1] * 1.1 + 1), 9999999999999)
        clicker.money -= elem[-1]
        clicker.cps += 0.01
    if elem[4] == 'Skins/clicks_per_second_x0.1.png':
        shop.boosters_dict['clicks_per_second_x0.1.png'] = min(int(
            elem[-1] * 1.2), 9999999999999)
        clicker.money -= elem[-1]
        clicker.cps += 0.1
    if elem[4] == 'Skins/clicks_per_second_x0.5.png':
        shop.boosters_dict['clicks_per_second_x0.5.png'] = min(int(
            elem[-1] * 1.25), 9999999999999)
        clicker.money -= elem[-1]
        clicker.cps += 0.5
    if elem[4] == 'Skins/clicks_per_second_x5.png':
        shop.boosters_dict['clicks_per_second_x5.png'] = min(int(
            elem[-1] * 1.25), 9999999999999)
        clicker.money -= elem[-1]
        clicker.cps += 5
    if elem[4] == 'Skins/clicks_per_second_x10.png':
        shop.boosters_dict['clicks_per_second_x10.png'] = min(int(
            elem[-1] * 1.3), 9999999999999)
        clicker.money -= elem[-1]
        clicker.cps += 10
    if elem[4] == 'Skins/clicks_per_second_x100.png':
        shop.boosters_dict['clicks_per_second_x100.png'] = min(int(
            elem[-1] * 1.4), 9999999999999)
        clicker.money -= elem[-1]
        clicker.cps += 100


if __name__ == '__main__':  # Запуск игры.

    # Подготовка к запуску игрового цикла:
    pygame.init()
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Clicker')

    if not os.path.exists('data'):
        os.mkdir("data")

    try:
        with open('data/clicker.json') as file:
            data = json.load(file)
        # data = dbSaver.download('data/save_data_1.db')
        clicker = Clicker(data)
    except FileNotFoundError:
        clicker = Clicker()

    pause = Pause()

    try:
        with open('data/shop.json') as file:
            data = json.load(file)
        shop = Shop(data)
    except FileNotFoundError:
        shop = Shop()

    A = -WINDOW_WIDTH
    print(clicker.to_save_info())
    running = True
    right_menu_is_open = False

    cursor_clicked = False

    take_pause = False
    x, y = 0, 0
    # image = pygame.image.load("Skins\cursor_green.png")
    cursor = pygame.image.load('Skins\cursor_blue.png')
    # image = pygame.image.load('Skins\cursor_blood.png')
    clock = pygame.time.Clock()
    start = True
    v = 1500
    flag = True
    c = 0

    # Игровой цикл:
    while running:
        if start:
            pygame.time.set_timer(TIMER_EVENT, TIMER_EVENT_DELAY)
            pygame.time.set_timer(AUTO_CLICK_EVENT, AUTO_CLICK_DELAY)
            start = not start
        else:
            MONEY = clicker.money
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEMOTION:
                    x, y = event.pos
                    take_pause = False
                    if clicker.is_paused:
                        take_pause = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cursor_clicked = pygame.image.load("Skins\click_effect.png")
                    click = True
                if event.type == pygame.MOUSEBUTTONUP:
                    cursor = pygame.image.load("Skins\cursor_blue.png")

                    cursor_clicked = False
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
            right_menu = RightMenu()
            points = right_menu.show_animation(shop.items, shop.colors, shop.boosters)
            if not clicker.is_paused:
                # если игра не на паузе, то
                shop_button = Button(screen, (
                    WINDOW_WIDTH / 38, WINDOW_HEIGHT / 1.14, int(WINDOW_WIDTH / 9),
                    int(WINDOW_HEIGHT / 14)), 'Магазин')
                pause_button = Button(screen, (WINDOW_WIDTH / 38, 800,
                                               int(WINDOW_WIDTH / 9), int(WINDOW_HEIGHT / 14)),
                                      'Пауза')
                if shop_button.is_button_enter() and click:
                    right_menu_is_open = not right_menu_is_open
                if pause_button.is_button_enter() and click:
                    clicker.switch_pause()
                #  проверка на взаимодействия с магазином
                if right_menu.skins_button.is_button_enter() and click:
                    SKINS_SHOWING = True
                if right_menu.boosters_button.is_button_enter() and click:
                    SKINS_SHOWING = False
                if SKINS_SHOWING:
                    for elem in points:
                        if is_mouse_enter((elem[0], elem[1],
                                           elem[0] + elem[2],
                                           elem[1] + elem[3])) and click:
                            if len(elem[4].split('.')) == 1:
                                flag, money = shop.buy(clicker.money, elem[4], shop.colors_dict)
                                if flag:
                                    clicker.set_skin()
                                    clicker.color = elem[4]
                                    clicker.money = money
                                    shop = Shop([shop.bought, shop.boosters_dict])
                            else:
                                flag, money = shop.buy(clicker.money,
                                                       elem[4].split('/')[-1], shop.skins)
                                if flag:
                                    clicker.set_skin(elem[4])
                                    clicker.money = money
                                    shop = Shop([shop.bought, shop.boosters_dict])
                if not SKINS_SHOWING:
                    for elem in points:
                        if is_mouse_enter((elem[0], elem[1],
                                           elem[0] + elem[2],
                                           elem[1] + elem[3])) and click \
                                and clicker.money >= elem[-1]:
                            buy_booster()
                            shop = Shop([shop.bought, shop.boosters_dict])
            #  пауза
            if clicker.is_paused:
                if take_pause:
                    screen.blit(pause.render(), (0, 0))
                else:
                    screen.blit(pause.render(), (0, 0))
                right_menu_is_open = False
            # if SETTINGS_IS_SHOWING:
            #     settings = Settings()
            if right_menu_is_open:
                A = min(A + v * clock.tick() / 1000, 0)
            else:
                A = max(A - v * clock.tick() / 1000, -WINDOW_WIDTH // 2)
            if cursor:
                cursor = pygame.transform.scale(cursor, (WINDOW_WIDTH // (WINDOW_WIDTH // 45),
                                                         WINDOW_WIDTH // (WINDOW_WIDTH // 35)))
                screen.blit(cursor, (x - WINDOW_WIDTH // 26 // 3, y - WINDOW_HEIGHT // 20 // 3))
            if cursor_clicked:
                cursor_clicked =\
                    pygame.transform.scale(cursor_clicked, (WINDOW_WIDTH // (WINDOW_WIDTH // 45),
                                                            WINDOW_WIDTH // (WINDOW_WIDTH // 35)))
                screen.blit(cursor_clicked, (x - WINDOW_WIDTH // 26 // 3, y - WINDOW_HEIGHT // 60))
            pygame.display.flip()
    clicker.is_paused = False
    # dbSaver.upload('data/save_data_1.db', clicker.to_save_info())
    with open('data/shop.json', 'w') as file:
        json.dump([shop.bought, shop.boosters_dict], file)
    with open('data/clicker.json', 'w') as file:
        json.dump(clicker.to_save_info(), file)
    pygame.quit()
