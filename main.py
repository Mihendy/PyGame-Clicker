import pygame
import json

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
            self.color = 'red'
        else:
            self.is_paused, self.score, self.money, self.click, \
            self.click_money, self.cps, self.skin_path, self.color = values
        self.money = float(self.money)
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
        self.skin = None
        self.skin_copy = None

    def to_save_info(self):
        """Метод этого класса вернёт список с информацией о данном классе (нужна для работы с БД)"""
        return [self.is_paused, self.score, to_fixed(self.money, 3), self.click, self.click_money,
                self.cps, self.skin_path, self.color]


class Button:
    """Класс кнопки"""

    def __init__(self, form, position, text='', click_event=False):
        """Инициализация и отрисовка кнопки на форме"""
        # self, форма на которой рисуется кнопка, координаты верхней левой и правой нижней точек
        # кнопки, позиция курсора в данный момент, текст кнопки и его координаты,
        # факт нажатия на кнопку
        self.title = text
        self.x, self.y, self.width, self.height = position
        self.click_event = click_event
        self.form = form
        self.font_color = (255, 255, 255)
        self.font_size = WINDOW_WIDTH // (WINDOW_WIDTH // 24)
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

    def install_event_filter(self):
        """EventFilter, в котором происходит обработка событий"""
        global x, y
        if check_button_enter((self.x, self.y,
                               self.x + self.width,
                               self.y + self.height)):
            self.coeff_x = WINDOW_WIDTH // (WINDOW_WIDTH // 25)
            self.coeff_y = WINDOW_WIDTH // (WINDOW_WIDTH // 10)
            self.x -= self.coeff_x
            self.y -= self.coeff_y
            self.width += self.coeff_x * 2
            self.height += self.coeff_y * 2
            self.font_size = self.font_size + self.coeff_x // 5
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.active_clr = (255, 255, 255, self.alpha)
                self.font_color = (42, 82, 190, self.alpha)
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
                self.font_color = (255, 255, 255)
                self.active_clr = (42, 82, 190, self.alpha)


class Pause:
    def __init__(self):
        self.active_clr = (61, 0, 153, 10)
        self.font_size = WINDOW_WIDTH // (WINDOW_WIDTH // 24)
        self.pause_button_size = WINDOW_WIDTH // 3, WINDOW_HEIGHT // 13.32
        self.buttons_titles = {
            0: ('Продолжить игру', WINDOW_HEIGHT * 0.3255),
            1: ('Настройки', WINDOW_HEIGHT * 0.455),
            2: ('Выйти', WINDOW_HEIGHT * 0.585)
        }

    def render(self):
        font = pygame.font.Font("Fonts/beer money.ttf", self.font_size)
        font_color = (255, 255, 255)
        text = font.render('Игра на паузе', True, font_color)
        SURFACE.fill((100, 100, 100, 100))
        SURFACE.blit(text, (WINDOW_WIDTH // (WINDOW_WIDTH // 40),
                            WINDOW_HEIGHT // WINDOW_HEIGHT // 120))
        self.draw_buttons()
        return SURFACE

    def draw_buttons(self):
        """Функция рисует кнопки в меню паузы"""
        for i in range(3):
            btn = Button(screen, (WINDOW_WIDTH // 3.3,
                                  self.buttons_titles[i][1],
                                  self.pause_button_size[0],
                                  self.pause_button_size[1]), self.buttons_titles[i][0])
            if check_button_enter((btn.x, btn.y,
                                   btn.x + btn.width,
                                   btn.y + btn.height)) and event.type == pygame.MOUSEBUTTONDOWN:
                if i == 0:  # Кнопка продолжения игры
                    clicker.switch_pause()
                elif i == 1:  # Кнопка Настроек игры
                    print('Настройки в разработке')
                elif i == 2:  # Кнопка выхода из игры
                    global running
                    running = False


class RightMenu:
    def __init__(self):
        # self.width, self.height = WINDOW_WIDTH // 3, WINDOW_HEIGHT - WINDOW_HEIGHT // 22
        self.color = (20, 20, 20)
        self.pos = (WINDOW_WIDTH - WINDOW_WIDTH // 3, WINDOW_HEIGHT // (WINDOW_HEIGHT // 25))
        self.button_pos = self.pos[:]
        self.main_points = [(int(WINDOW_WIDTH / 4 * 3 - A), 0),
                            (WINDOW_WIDTH - A, 0),
                            (WINDOW_WIDTH - A, WINDOW_HEIGHT),
                            (int(WINDOW_WIDTH / 1.5 - A), WINDOW_HEIGHT)]

    def show(self, items, colors):
        skins = items + colors
        pygame.draw.polygon(screen, self.color, self.main_points, width=0)
        skins_button = Button(screen, (WINDOW_WIDTH / 1.55 - A * 2, WINDOW_HEIGHT / 1.14,
                                       int(WINDOW_WIDTH / 9), int(WINDOW_HEIGHT / 14)), 'Скины')
        boosters_button = Button(screen, (right_menu_btns_start_pos[0] + 200, WINDOW_HEIGHT / 1.14,
                                          int(WINDOW_WIDTH / 9), int(WINDOW_HEIGHT / 14)),
                                 'Ускорители')
        pygame.draw.rect(screen, 'white', (0 - A * 5, 0, WINDOW_WIDTH * 1.5, WINDOW_HEIGHT * 0.032))
        if flag:
            points = []
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
        # else:
        #     for i in range(len(boosters)):
        #         y_coff = i // 3
        #         x_coff = i % 3
        #         w, h = WINDOW_WIDTH // 19, WINDOW_HEIGHT // 9
        #         items[i].render(screen, (
        #             int(WINDOW_WIDTH / 4 * 3 + WINDOW_WIDTH // 40 + (
        #                     WINDOW_WIDTH // 40 + w) * x_coff - A),
        #             WINDOW_WIDTH // 40 + (h + WINDOW_WIDTH // 40) * y_coff), (w, h))


class Shop:
    def __init__(self, bought=None):
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

        self.backgrounds = {}

        self.boosters = {}
        if bought is not None:
            self.bought = bought
        else:
            self.bought = []

        self.items = []
        for k, v in self.skins.items():
            self.items.append(ItemCell(v, k, self.is_bought(k)))
        self.colors = []
        for k, v in self.colors_dict.items():
            self.colors.append(ColorCell(v, k, self.is_bought(k)))

    def buy(self, money, obj, category):
        if obj in self.bought:
            return True, money
        if category[obj] <= money:
            self.bought.append(obj)
            return True, money - category[obj]
        return False, money

    def is_bought(self, name):
        return name in self.bought


class ItemCell:
    def __init__(self, price, ico_name, is_bought):
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

    # def install_event_filter(self):
    #     """EventFilter, в котором происходит обработка событий"""
    #     global x, y
    #     if check_button_enter((self.x, self.y,
    #                            self.x + self.width,
    #                            self.y + self.height)):
    #         self.coeff_x = WINDOW_WIDTH // (WINDOW_WIDTH // 25)
    #         self.coeff_y = WINDOW_WIDTH // (WINDOW_WIDTH // 10)
    #         self.x -= self.coeff_x
    #         self.y -= self.coeff_y
    #         self.width += self.coeff_x * 2
    #         self.height += self.coeff_y * 2
    #         self.font_size = self.font_size + self.coeff_x // 5
    #         if event.type == pygame.MOUSEBUTTONDOWN:
    #             self.active_clr = (255, 255, 255, self.alpha)
    #             self.font_color = (42, 82, 190, self.alpha)
    #         if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
    #             self.font_color = (255, 255, 255)
    #             self.active_clr = (42, 82, 190, self.alpha)


class ColorCell(ItemCell):
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


def click_timer():
    """ Таймер, предотворяющий залипание клавиш"""
    result = True if clock.tick() / 1000 > 0.1 else False
    result = True
    return result


def check_button_enter(button_pos):
    """Функция проверяет наличие над кнопкой курсора"""
    x1, y1, x2, y2 = button_pos
    if x in range(int(x1), int(x2)) and y in range(int(y1), int(y2)):
        return True
    return False


if __name__ == '__main__':
    pygame.init()
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Clicker')

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

    image2 = False

    take_pause = False
    x, y = 0, 0
    image = pygame.image.load('Skins\cursor_blue.png')
    clock = pygame.time.Clock()
    intro = True
    intr = pygame.image.load('BackGrounds\INTRO.png')
    intro_image = pygame.transform.scale(intr, (
        min(WINDOW_WIDTH, WINDOW_HEIGHT), min(WINDOW_WIDTH, WINDOW_HEIGHT)))
    v = 1500
    flag = True
    c = 0
    while running:
        if intro:
            # screen.fill((0, 0, 0))
            #
            # intro_image.set_alpha(a)
            # if flag:
            #     a += v * clock.tick() / 1000
            # else:
            #     a -= v * clock.tick() / 1000
            # screen.blit(intro_image, ((WINDOW_WIDTH - min(WINDOW_WIDTH, WINDOW_HEIGHT)) // 2,
            #                           (WINDOW_HEIGHT - min(WINDOW_WIDTH, WINDOW_HEIGHT)) // 2))
            # pygame.display.flip()
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         exit()
            # if a > 160 or a < 0:
            #     flag = not flag
            #     c += 1
            # if c >= 2:
            #     intro = not intro
            intro = not intro
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
                    image2 = pygame.image.load("Skins\click_effect.png")
                    click = True
                if event.type == pygame.MOUSEBUTTONUP:
                    # image = pygame.image.load("Skins\cursor_green.png")
                    # image = pygame.image.load("Skins\cursor_blue.png")
                    image = pygame.image.load('Skins\cursor_blood.png')

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
            right_menu = RightMenu()
            points = right_menu.show(shop.items, shop.colors)
            if not clicker.is_paused:
                shop_button = Button(screen, (
                    WINDOW_WIDTH / 38, WINDOW_HEIGHT / 1.14, int(WINDOW_WIDTH / 9),
                    int(WINDOW_HEIGHT / 14)), 'Магазин')
                if check_button_enter((shop_button.x, shop_button.y,
                                       shop_button.x + shop_button.width,
                                       shop_button.y + shop_button.height)) and click:
                    right_menu_is_open = not right_menu_is_open
                for elem in points:
                    if check_button_enter((elem[0], elem[1],
                                           elem[0] + elem[2],
                                           elem[1] + elem[3])) and \
                            click and clicker.money >= elem[5]:
                        if len(elem[4].split('.')) == 1:
                            flag, money = shop.buy(clicker.money, elem[4], shop.colors_dict)
                            if flag:
                                clicker.set_skin()
                                clicker.color = elem[4]
                                clicker.money = money
                                shop = Shop(shop.bought)
                        else:
                            flag, money = shop.buy(clicker.money,
                                                   elem[4].split('/')[-1], shop.skins)
                            if flag:
                                clicker.set_skin(elem[4])
                                clicker.money = money
                                shop = Shop(shop.bought)
            if clicker.is_paused:
                if take_pause:
                    screen.blit(pause.render(), (0, 0))
                else:
                    screen.blit(pause.render(), (0, 0))
            if right_menu_is_open:
                A = min(A + v * clock.tick() / 1000, 0)
            else:
                A = max(A - v * clock.tick() / 1000, -WINDOW_WIDTH // 2)
            if image:
                image = pygame.transform.scale(image, (WINDOW_WIDTH // 26, WINDOW_HEIGHT // 20))
                screen.blit(image, (x - WINDOW_WIDTH // 26 // 3, y - WINDOW_HEIGHT // 20 // 3))
            if image2:
                image2 = pygame.transform.scale(image2, (WINDOW_WIDTH // 26, WINDOW_HEIGHT // 20))
                screen.blit(image2, (x - WINDOW_WIDTH // 26 // 3, y - WINDOW_HEIGHT // 20 // 3))
            pygame.display.flip()
    clicker.is_paused = False
    # dbSaver.upload('data/save_data_1.db', clicker.to_save_info())
    with open('data/shop.json', 'w') as file:
        json.dump(shop.bought, file)
    with open('data/clicker.json', 'w') as file:
        json.dump(clicker.to_save_info(), file)
    pygame.quit()
