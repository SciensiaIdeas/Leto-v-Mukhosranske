import moment
import pygame
import numpy as np
from collections.abc import Iterable
from sortedcontainers import SortedKeyList
from datetime import time, timedelta
import sys
import os
import weakref
from operator import attrgetter
from dataclasses import dataclass
from branch import MyWidget
import json


class Prob:
    const_exp = np.log(0.05) / np.log(0.5)
    d = None
    @staticmethod
    def update_d(N):
        Prob.d = 0.95 * N / Prob.const_exp

    __slots__ = ("high", "open", "_pr", "x")
    def __init__(self):
        self.high = False
        self.open = False
        self._pr = None
        self.x = None

    def update(self, x):
        self._pr = 1 - 0.5 ** (x / Prob.d)
        if self.high:
            self._pr += (1 - self._pr) * self._pr
        self.x = x

    def dotry(self):
        self.open = np.random.random() < self._pr
        return self.open

    def display(self):
        return int(self._pr * 100)

@dataclass
class Choice:
    text_id: int | str
    link: int
    extra: int
    dialog: bool | Prob
    selected: bool = False

    def __init__(self, text_id, link: int = None, extra = 0, dialog = True):
        self.text_id = text_id
        self.dialog = dialog
        self.link = link
        self.extra = extra

    def text(self, T: Iterable[str]) -> str:
        return T[self.text_id] if isinstance(self.text_id, int) else self.text_id


@dataclass
class Frame:
    link: int
    time: time
    atimes: Iterable[tuple[int, timedelta]]
    time_s: moment.date = None
    temp_s: int = None
    choices: Iterable[Choice] = None
    next_link: int = None

    def __init__(self, link: int, choices=None, atimes=None, _time: time = None):
        self.link = link
        self.time = _time
        self.atimes = atimes

        if isinstance(choices, Iterable):
            self.choices = choices
        else:
            self.next_link = choices

    def __str__(self):
        return (f"link={self.link}; choices={len(self.choices) if self.choices is not None else 'null'}; "
                f"next_link={self.next_link if self.next_link else 'null'}")


@dataclass
class Ending:
    link: int
    name_id: int
    next_link: int

    def text(self, T: Iterable[str]) -> str:
        return T[self.name_id]


@dataclass(frozen=True)
class Character:
    link: int
    name_id: int
    age: int

    def text(self, T: Iterable[str]) -> tuple[str, str]:
        return T[self.name_id], T[self.name_id + 1]


class FrameArray:
    __slots__ = "_list"
    def __init__(self, arr):
        self._list = SortedKeyList(arr, key=attrgetter('link'))

    def __getitem__(self, link: int):
        i = self._list.bisect_key_left(link)
        if i < len(self._list) and self._list[i].link == link:
            return self._list[i]
        return None

    def remove(self, link: int):
        i = self._list.bisect_key_right(link)
        if i < len(self._list) and self._list[i].link == link:
            self._list.pop(i)

    def __iter__(self):
        return iter(self._list)


def get_geometry(choices, font, surf, text, initial_w=0):
    if isinstance(surf, pygame.Rect):
        size = (surf.w, surf.h)
        button_h = int(0.13 * size[1])
        button_gap = int(0.035 * size[0])
    else:
        size = surf.get_size()
        button_h = int(0.065 * size[1])
        button_gap = int(0.0175 * size[0])

    n = len(choices)
    # Расчет ширины каждой кнопки в зависимости от текста
    button_width = max(font.size(choice.text(text)+'(100%)O')[0] + button_gap for choice in choices) + initial_w
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
                change = bool(np.random.choice(acts['d_change']))
            else:
                change = True
        elif acts['win_']:
            if acts['w_change']:
                change = bool(np.random.choice(acts['w_change']))
            else:
                change = False
        else:
            if acts['l_change']:
                change = bool(np.random.choice(acts['l_change']))
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
        x = np.random.randint(0, 3)
    else:
        x = np.random.choice([beat(elem) for elem in pr])

    link = 89+x*3+cur_act
    if link in (90, 94, 95):
        win = True
    elif link in (91, 92, 96):
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


class Constants:
    def __init__(self):
        self.question_range = range(71, 85)
        self.fight_range = range(88, 98)
        self.checkpoints = (4, 25, 35, 66, 101, 105)
        self.search_range = (101, 105)
        self.search_range_after = range(107, 112)
        self.games_range = set(self.question_range) | set(self.fight_range) | set(self.search_range_after)
        self.saves_range = self.games_range - {71, 88}

        self.EMOJI_IMAGES = None
        self.emoji_size = (32, 32)

        pygame.mixer.init()
        self.click = pygame.mixer.Sound(res('media/click.wav'))
        self.fight_s = pygame.mixer.Sound(res('media/fight.wav'))
        self.wrong = pygame.mixer.Sound(res('media/wrong.wav'))
        self.clock = pygame.mixer.Sound(res('media/clock.wav'))

        self.menu_video = res('media/menu.mp4')
        self.menu_audio = res('media/menu.wav')
        self.logo_icon = pygame.image.load(res('media/logo.png'))
        self.clock_icon = pygame.image.load(res('media/clock.png'))
        self.disclaimer_audio = res('media/guide.wav')
        self.searching = res('media/searching.mp3')

        user_os = sys.platform
        if user_os.startswith('win'):
            # Windows
            self.sub_font = "arial.ttf"
            self.bold_font = 'Courier'
            self.text_font = pygame.font.match_font('timesnewroman')
        elif user_os.startswith('linux'):
            # Linux
            self.sub_font = pygame.font.match_font('dejavusans')
            self.bold_font = 'Liberation Serif'
            self.text_font = pygame.font.match_font('ubuntu')

    def change_theme(self, theme_name: str):
        with open(res(f"themes/{theme_name}.json"), 'r', encoding='utf-8') as file:
            theme = json.load(file)
            for key, value in theme.items():
                setattr(self, f"color_{key}", tuple(value))

constants = Constants()

def update_choice(cls, txt):
    cls.colors = []
    cls.button_labels = []

    for choice in cls.choices:
        if isinstance(choice.dialog, Prob):
            if choice.selected:
                color1 = constants.color_pr_clicked
            else:
                color1 = constants.color_pr
        else:
            if choice.selected:
                color1 = constants.color_dialog_clicked if choice.dialog else constants.color_action_clicked
            else:
                color1 = constants.color_dialog if choice.dialog else constants.color_action

        title = choice.text(txt)
        if isinstance(choice.dialog, Prob):
            if choice.dialog.open or cls.type == -3:
                texti = f'{title} ({choice.dialog.display()}%)'
                if cls.type == -3:
                    val = round(choice.dialog.x, 1)
                    texti += f'{val} :fly:'
                color2 = constants.color_front
            else:
                texti = title
                color2 = constants.color_txtused
        else:
            texti = title
            color2 = constants.color_front

        category = get_category(choice)
        # display emoji
        if category and not choice.dialog:
            texti += f' :{category}:'

        cls.colors.append((color1, color2))
        cls.button_labels.append(texti)

def reward_player(choice, game, choices, link, frame_surface):
    if choice.dialog:
        choice.dialog = False
        # reward player
        category = get_category(choice)
        if category:
            if category in ('ending', 'biography'):
                if category == 'biography':
                    x = choice.extra
                    game.collection[category].add(x)
                    game.unseen[category].add(x)
            else:
                game.collection[category] += 1
                game.unseen[category] += 1
            game.saves['credits'] += game.plus_factor[category]
        # open new frame
        if all(not ch.dialog for ch in choices) and link not in constants.games_range:
            w = MyWidget(choices, frame_surface, game.time.copy(), game.temp)
            game.frame_s.add(w)
            game.unseen['frames'].add(w.thumb_key)
            return True
    return False

def get_category(choice):
    if choice.extra == 0:
        category = None
    elif choice.extra == -1:
        category = 'speedrun'
    elif choice.extra == -2:
        category = 'ending'
    elif choice.extra == -3:
        category = 'death'
    else:
        category = 'biography'

    return category


class ThumbCache:
    __slots__ = "_store"
    def __init__(self):
        # слабые ссылки, чтобы GC мог забирать неиспользуемые Surface
        self._store = weakref.WeakValueDictionary()

    def get(self, key, base_surface, size):
        """
        key: любой хэшируемый ключ, например ('media42', 12.0) или ('frame', frame_id)
        base_surface: Surface исходника (или уже уменьшенный Surface)
        size: (w, h) желаемый размер
        """
        cache_key = (key, *size)
        surf = self._store.get(cache_key)
        if surf:
            return surf

        # создаём миниатюру один раз
        thumb = pygame.transform.smoothscale(base_surface, size).convert()
        self._store[cache_key] = thumb
        return thumb

    def __getstate__(self): return {}

    def __setstate__(self, state): self.__init__()

THUMBS = ThumbCache()