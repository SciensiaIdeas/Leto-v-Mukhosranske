import pygame
import random
from collections.abc import Iterable
from sortedcontainers import SortedList
from datetime import time
import sys
import os


class Choice:
    def __init__(self, text: str, dialog, link: int = None):
        self.text = text
        self.dialog = dialog
        self.link = link


class Prob:
    def __init__(self, high=False):
        self.high = high
        self.open = True
        self._pr = None

    def update(self, n: int):
        self._pr = (n + 1) / 12
        if self._pr > 1:
            self._pr = 1
        if self.high:
            self._pr += (1 - self._pr) * self._pr

    def dotry(self):
        self.open = random.random() < self._pr
        return self.open

    def display(self):
        return int(self._pr * 100)


class Frame:
    def __init__(self, link: int, choices=None, atimes=None, _time: time = None):
        self.link = link
        self.time = _time
        self.atimes = atimes
        self.characters = None

        if isinstance(choices, Iterable):
            self.choices = choices
            self.next_link = None
        else:
            self.choices = None
            self.next_link = choices

    def __lt__(self, other):
        if isinstance(other, Frame):
            return self.link < other.link
        elif isinstance(other, int):
            return self.link < other


class Ending:
    def __init__(self, link: int, name: str, checkpoint: int):
        self.link = link
        self.name = name
        self.next_link = checkpoint

    def __lt__(self, other):
        if isinstance(other, Ending):
            return self.link < other.link
        elif isinstance(other, int):
            return self.link < other


class Character:
    def __init__(self, link: int, name: str, subtitle: str, age: int):
        self.link = link
        self.name = name
        self.subtitle = subtitle
        self.age = age


class FrameArray:
    def __init__(self, arr):
        self._container = SortedList(arr)

    def __getitem__(self, item):
        index = self._container.bisect_left(item)
        if index < len(self._container):
            return self._container[index]
        return None

    def update(self, arr):
        self._container.update(arr)


def get_geometry(choices, font, screen):
    size = screen.get_size()
    button_h = int(0.065 * size[1])
    button_gap = int(0.0175 * size[0])
    n = len(choices)
    # Расчет ширины каждой кнопки в зависимости от текста
    button_width = max(font.size(choice.text + '(100%)')[0] + button_gap for choice in choices)
    button_height = button_h * n + button_gap * (n-1)

    # Начальная позиция первой кнопки (по центру экрана)
    start_x = (size[0] - button_width) // 2
    current_y = (size[1] - button_height) // 2
    buttons = []
    for i in range(len(choices)):
        button_rect = pygame.Rect(start_x, current_y, button_width, button_h)
        buttons.append(button_rect)
        current_y += button_h + button_gap
    return buttons


def create_buttons(choices, buttons, font, screen):
    for button_rect, choice in zip(buttons, choices):
        if isinstance(choice.dialog, Prob):
            color = (203, 0, 255)
        else:
            color = (112, 173, 71) if choice.dialog else (255, 0, 0)
        pygame.draw.rect(screen, color, button_rect)
        if isinstance(choice.dialog, Prob):
            if choice.dialog.open:
                s = f'{choice.text} ({choice.dialog.display()}%)'
                text_surface = font.render(s, True, (0, 0, 0))
            else:
                text_surface = font.render(choice.text, True, (163, 0, 0))
        else:
            text_surface = font.render(choice.text, True, (0, 0, 0))
        screen.blit(text_surface, (button_rect.x + (button_rect.width - text_surface.get_width()) // 2,
                                   button_rect.y + (button_rect.height - text_surface.get_height()) // 2))


def add_button_events(cls, choices, buttons, last_frame):
    for event in pygame.event.get():
        cls.general_events(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button_rect, choice in zip(buttons, choices):
                if button_rect.collidepoint(event.pos):
                    if isinstance(choice.dialog, Prob):
                        prob = choice.dialog
                        if prob.open:
                            if prob.dotry():
                                choice.dialog = False
                                return choice.link
                            else:
                                return -1
                        else:
                            return -1
                    return choice.link
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if cls.show_settings(last_frame):
                    return
                pygame.mixer.music.set_volume(cls.volume)


def predict_act(acts: dict):
    h = acts['stats']
    var = {0, 1, 2}
    if not h:
        return var
    if len(h) == 1:
        change = not acts['win_']
    else:
        if acts['win'] is None:
            if h[-1] == h[-2]:
                acts['d_change'].append(0)
            else:
                acts['d_change'].append(1)
        elif acts['win']:
            if h[-1] == h[-2]:
                acts['w_change'].append(0)
            else:
                acts['w_change'].append(1)
        else:
            if h[-1] == h[-2]:
                acts['l_change'].append(0)
            else:
                acts['l_change'].append(1)
        if acts['win_'] is None:
            if acts['d_change']:
                change = bool(random.choice(acts['d_change']))
            else:
                change = True
        elif acts['win_']:
            if acts['w_change']:
                change = bool(random.choice(acts['w_change']))
            else:
                change = False
        else:
            if acts['l_change']:
                change = bool(random.choice(acts['l_change']))
            else:
                change = True

    if change:
        res1 = var - {h[-1]}
    else:
        res1 = {h[-1]}

    return res1


def fighting(cur_act: int, acts: dict):
    def beat(act: int):
        x = act + 1
        if x == 3:
            return 0
        return x

    pr = predict_act(acts)
    if len(pr) == 3:
        x = random.randint(0, 2)
    else:
        x = random.choice([beat(elem) for elem in pr])

    link = 84+x*3+cur_act
    if link in (85, 89, 90):
        win = True
    elif link in (86, 87, 91):
        win = False
    else:
        win = None

    acts['win'] = acts['win_']
    acts['win_'] = win
    acts['stats'].append(cur_act)
    return link


def res(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # Temp directory when running from PyInstaller
    else:
        base_path = os.path.abspath(".")  # Normal script execution path

    return os.path.join(base_path, relative_path)
