import core
from screen import Screen
import pygame
from core import res, constants
from moviepy import VideoFileClip
import moment
from screen import EndingScreen
from text import read_description
from branch import TreeChoiceScreen
import numpy as np


class MainMenu(Screen):
    def __init__(self, game):
        super().__init__(game, 50, True)
        self.clip = VideoFileClip(constants.menu_video)
        pygame.mixer.music.set_volume(game.settings['volume'] / 2)
        pygame.mixer.music.load(constants.menu_audio)
        pygame.mixer.music.play()

        self.current_time = 0
        self.text_ = '--:--'
        self.time = moment.date(2019, 6, 13)

        self.buttons = np.array([None]*10, dtype=pygame.Rect)
        self.button_labels = [None] * 10
        self.selected_button = None
        self.slide = 0
        self.event_pos = None
        self.update()

    def is_locked(self, index):
        if index == 1:
            return self.game.saves['load'] is None
        if index == 2:
            return self.game.saves['continue'] is None
        if index == 7:
            return not self.game.collection['endings']
        if index == 8:
            return not self.game.frame_s
        return False

    def update(self):
        x_100 = self.x_100
        y_100 = self.y_100
        s1 = 0.5 * y_100
        self.s1 = s1
        self.x = 2.5 * x_100
        self.x2 = 8 * x_100
        self.w = 3.2 * x_100
        self.w2 = 3.7 * x_100

        tmenu = self.game.locale.tmenu

        rects = [2.8, 3.6, 4.4, 5.2, 6.0]

        for i, y_mult in enumerate(rects):
            x = self.x
            w = self.w
            self.buttons[i] = pygame.Rect(x, y_mult * y_100, w, s1)

        for i, y_mult in enumerate(rects, len(rects)):
            x = self.x2
            w = self.w2
            self.buttons[i] = pygame.Rect(x, y_mult * y_100, w, s1)

        self.button_labels[0] = tmenu[0]
        self.button_labels[1] = tmenu[1]
        self.button_labels[2] = tmenu[2]
        self.button_labels[3] = f"{tmenu[42]}: [{self.game.settings['lang']}]"
        theme_name = self.game.themes[self.game.settings['theme']].removesuffix(".json")
        self.button_labels[4] = f"{tmenu[41]}: [{theme_name}]"
        self.button_labels[5] = tmenu[3] if 141 in self.game.collection['endings'] else tmenu[4]
        self.button_labels[6] = f"{tmenu[5]} ({len(self.game.collection['biography'])}/11)"
        self.button_labels[7] = f"{tmenu[6]} ({len(self.game.collection['endings'])}/12)"
        self.button_labels[8] = f"{tmenu[19]} ({len(self.game.frame_s)}/28)"
        self.button_labels[9] = tmenu[7]

    def _press_button(self):
        i = self.selected_button
        if i is None or self.is_locked(i):
            return

        click = constants.click.play
        if i == 0:
            click(); self.temp = 1; self.stop()
        elif i == 1:
            click(); frame = self.game.saves['load']; self._load_game(frame)
        elif i == 2:
            click(); frame = self.game.saves['continue']; self._load_game(frame)
        elif i == 3:
            self._navigate_language(1)
        elif i == 4:
            self._navigate_theme(1)
        elif i == 5:
            click(); pygame.mixer.music.pause(); GuideScreen(self.game).loop(); pygame.mixer.music.unpause()
        elif i == 6:
            click(); pygame.mixer.music.pause(); show_cards(self.game, self.game.collection['biography'], BioScreen); pygame.mixer.music.unpause()
        elif i == 7:
            click(); pygame.mixer.music.pause(); show_cards(self.game, self.game.collection['endings'], EndingScreen); pygame.mixer.music.unpause()
        elif i == 8:
            click()
            pygame.mixer.music.pause()
            sc = TreeChoiceScreen(self.game)
            sc.loop()
            if sc.result:
                pygame.mixer.music.stop()
                frame, link = sc.result
                self.temp = link
                self.game.time = frame.time
                self.game.temp = frame.temp
                self.stop()
            else:
                pygame.mixer.music.unpause()
        else:
            self.temp = 0; self.stop()

    def _load_game(self, frame):
        if frame:
            self.temp = frame.link
            self.game.time = frame.time_s
            self.game.temp = frame.temp_s
            self.stop()

    def _navigate_selection(self, direction):
        if self.selected_button is None:
            self.selected_button = 0 if direction > 0 else len(self.buttons) - 1

        index = self.selected_button
        while True:
            index = (index + direction) % len(self.buttons)
            if not self.is_locked(index):
                self.selected_button = index
                break

        self._hover_button()

    def _hover_button(self):
        i = self.selected_button
        if i == 0:
            self._set_time_display('07:00')
        elif i in [1, 2]:
            save = self.game.saves['load' if i == 1 else 'continue']
            if save:
                self._set_time_display(save.time_s.strftime('%H:%M'), save.time_s)
        else:
            self._set_time_display('--:--', moment.date(2019, 6, 13))

    def _set_time_display(self, text, time=None):
        if self.text_ != text:
            constants.clock.play()
        self.text_ = text
        self.time = time or self.time

    def _navigate_theme(self, direction):
        themes = self.game.themes
        self.game.settings['theme'] = (self.game.settings['theme'] + direction) % len(themes)
        name = self.game.themes[self.game.settings['theme']]
        constants.change_theme(name)

    def _navigate_language(self, direction):
        self.game.settings['lang'] = self.game.locale.change_lang(direction)
        pygame.display.set_caption(self.game.locale.tmenu[34])
        self.game.block[1:] = [False] * 3

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEMOTION:
            if event.pos != self.event_pos:
                self.event_pos = event.pos
                self.selected_button = None
            for i, rect in enumerate(self.buttons):
                if rect.collidepoint(event.pos) and not self.is_locked(i):
                    self.selected_button = i
                    self._hover_button()
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._press_button()

        elif event.type == pygame.KEYDOWN:
            key = event.key
            if pygame.K_1 <= key <= pygame.K_9:
                index = key - pygame.K_1
                if index < len(self.buttons) and not self.is_locked(index):
                    self.selected_button = index
                    self._hover_button()

            elif key == pygame.K_w:
                self._navigate_selection(-1)
                self.slide = 1 if self.selected_button >= 5 else 0
            elif key == pygame.K_s:
                self._navigate_selection(1)
                self.slide = 1 if self.selected_button >= 5 else 0
            elif key == pygame.K_a:
                if self.slide == 1:
                    self.slide = 0
                    self.selected_button = 0
                    self._hover_button()
            elif key == pygame.K_d:
                if self.slide == 0:
                    self.slide = 1
                    self.selected_button = 5
                    self._hover_button()
            elif key in (pygame.K_LEFT, pygame.K_RIGHT):
                if self.selected_button == 3:
                    n = 1 if key == pygame.K_RIGHT else -1
                    self._navigate_language(n)
                elif self.selected_button == 4:
                    n = 1 if key == pygame.K_RIGHT else -1
                    self._navigate_theme(n)
            elif key == pygame.K_RETURN:
                self._press_button()

    def draw(self):
        # Видео и фон
        if pygame.mixer.music.get_pos() == -1:
            pygame.mixer.music.play()
        self.current_time = pygame.mixer.music.get_pos() / 1000.0
        frame = self.clip.get_frame(self.current_time)
        surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        self.screen.blit(pygame.transform.scale(surface, self.size), (0, 0))

        # Логотип и часы
        s = (12 * self.x_100, 1.75 * self.y_100)
        x1 = (self.size[0] - s[0]) // 2
        self.screen.blit(pygame.transform.scale(constants.logo_icon, s), (x1, 0))
        k = 1.2 * self.x_100
        self.screen.blit(pygame.transform.scale(constants.clock_icon, (k, k)), (0.8 * self.x_100, 3.2 * self.y_100))
        self.screen.blit(self.game.font.render(self.text_, True, constants.color_front), (0.9 * self.x_100, 3.4 * self.y_100 + k))

        # Кнопки
        for i, (rect, label) in enumerate(zip(self.buttons, self.button_labels)):
            var = None
            mode = True
            if i == 1:
                var = self.game.saves['load']
            elif i == 2:
                var = self.game.saves['continue']
            elif i == 7:
                var = self.game.collection['endings']
            elif i == 8:
                var = self.game.frame_s
            else:
                mode = False

            clicked = (i == self.selected_button)
            color = constants.color_menuwidget_clicked if clicked else constants.color_menuwidget
            self.draw_button(rect, label, mode, var, color_b=color)

            if i == 6:
                self.draw_badge(rect, len(self.game.unseen['biography']))
            elif i == 7:
                self.draw_badge(rect, len(self.game.unseen['endings']))
            elif i == 8:
                k = len(self.game.unseen['frames'])
                n = 0 if k==0 else k + self.game.unseen['death'] + self.game.unseen['speedrun']
                self.draw_badge(rect, n)

        # Credits
        y = self.size[1] - self.y_100 * 0.7
        text1, rect1 = self.game.font_b.render("© Sciensia Ideas 2025 (v1.1)", fgcolor=constants.color_front,
                                               style=pygame.freetype.STYLE_STRONG)
        self.screen.blit(text1, (self.x_100, y))

        y = self.size[1] - self.y_100 * 1.05
        w = self.x_100 * 1.8
        r = pygame.Rect(self.size[0] - self.x_100 - w, y, w, self.s1 * 1.8)
        val = round(self.game.saves["credits"], 1)
        Screen.draw_button_static(r, f':fly: {val}', self.screen, self.game.font_title,
                                  color_b=constants.color_front)

    def stop(self):
        pygame.mixer.music.stop()
        super().stop()



class BioScreen(Screen):
    def __init__(self, game, link, n):
        super().__init__(game)
        self.link = link
        self.image = pygame.image.load(res(f'media/chr{link}.png'))
        self.description = res(f'subs/{game.settings['lang']}/chr{link}')
        self.N = n

        self.buttons = np.array([None]*2, dtype=pygame.Rect)
        self.button_labels = [None] * 2
        self.update()

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.buttons[0].collidepoint(event.pos):
                constants.click.play()
                self._action(-1)
            elif self.buttons[1].collidepoint(event.pos):
                constants.click.play()
                self._action(1)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self._action(-1)
            elif event.key == pygame.K_d:
                self._action(1)
            elif event.key == pygame.K_ESCAPE:
                self.temp = 0
                self.stop()

    def _action(self, k):
        self.temp = k
        self.stop()

    def update(self):
        x_100 = self.x_100
        y_100 = self.y_100
        tmenu = self.game.locale.tmenu
        w = 2.5 * x_100
        h = y_100 // 2

        self.buttons[0] = pygame.Rect(x_100 // 2, self.size[1] - y_100, w, h)
        self.button_labels[0] = tmenu[7] if self.N == 0 or self.N == 3 else tmenu[9]
        self.buttons[1] = pygame.Rect(self.size[0] - 3 * x_100, self.size[1] - y_100, w, h)
        self.button_labels[1] = tmenu[7] if self.N == 2 or self.N == 3 else tmenu[10]

    def draw(self):
        tmenu = self.game.locale.tmenu
        x_100 = self.x_100
        y_100 = self.y_100

        h1 = int(self.size[1] * 0.45)
        w1 = (self.size[0] - 16*h1/9) // 2
        ending_image = pygame.transform.scale(self.image, (16*h1//9, h1))
        self.screen.fill(constants.color_back)
        self.screen.blit(ending_image, (w1, 0))

        ch = self.game.cache['biography'][self.link]
        name, subtitle = ch.text(self.game.locale.txt)
        text1, rect1 = self.game.font_b.render(name, fgcolor=constants.color_front, style=pygame.freetype.STYLE_STRONG)
        text2, rect2 = self.game.font_b.render(subtitle, fgcolor=constants.color_front, style=pygame.freetype.STYLE_OBLIQUE)
        text3, rect3 = self.game.font_b.render(f'({ch.age} {tmenu[8]})', fgcolor=constants.color_front, style=pygame.freetype.STYLE_NORMAL)
        y = h1 + 0.2 * y_100
        x = 0.2 * x_100
        self.screen.blit(text1, (x, y))
        if self.link in self.game.unseen['biography']:
            x += rect1.w + 0.1 * x_100
            self.draw_badge_internal(x, y)
            x += x_100
            self.mark = True
        else:
            x += rect1.w + 0.2 * x_100
            self.mark = False
        self.screen.blit(text3, (x, y))
        y += rect1.h + 0.1 * y_100
        x = 0.2 * x_100
        self.screen.blit(text2, (x, y))
        y += rect2.h + 0.3 * y_100

        read_description(self.description, (self.size[0]-0.4*x_100, h1-3*y_100), (0.2*x_100, h1+1.5*y_100), self.screen, self.game.font_text)
        for rect, label in zip(self.buttons, self.button_labels):
            self.draw_button(rect, label, False, None)

    def stop(self):
        if self.mark:
            self.game.unseen['biography'].remove(self.link)
        super().stop()


class GuideScreen(Screen):
    def __init__(self, game):
        music = game.collection['endings'].__contains__(141)
        super().__init__(game, music=music)
        if music:
            pygame.mixer.music.load(constants.disclaimer_audio)
            pygame.mixer.music.set_volume(0.3 * game.settings['volume'])
            pygame.mixer.music.play(loops=-1)

        self.buttons = None
        self.button_labels = None
        self.update()

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.buttons.collidepoint(event.pos):
                constants.click.play()
                self.stop()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.stop()

    def update(self):
        x_100 = self.x_100
        y_100 = self.y_100
        w = 2.5 * x_100
        h = y_100 // 2

        self.buttons = pygame.Rect((self.size[0] - w) // 2, self.size[1] - y_100, w, h)
        self.button_labels =  self.game.locale.tmenu[7]

    def draw(self):
        tmenu = self.game.locale.tmenu
        x_100 = self.x_100
        y_100 = self.y_100

        self.screen.fill(constants.color_back)
        if self.game.collection['endings'].__contains__(141):
            t = tmenu[11]
        else:
            t = tmenu[4]
        title_surface = self.game.font_title.render(t, True, constants.color_title)
        title_rect = title_surface.get_rect(center=(self.size[0] // 2, y_100))
        self.screen.blit(title_surface, title_rect)

        texti = res(f'subs/{self.game.settings['lang']}/guide')
        read_description(texti, (self.size[0] - 0.8 * x_100, self.size[1] - 1.9 * y_100), (0.4 * x_100, 1.8 * y_100),
                              self.screen, self.game.font_text)

        self.draw_button(self.buttons, self.button_labels, False, None)

    def stop(self):
        if self.game.collection['endings'].__contains__(141):
            pygame.mixer.music.stop()
            pygame.mixer.music.load(constants.menu_audio)
            pygame.mixer.music.play()
        super().stop()


class DisclaimerScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.description = res(f'subs/{self.game.settings['lang']}/disclaimer')
        self.game = game

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            self.stop()

    def draw(self):
        self.screen.fill(constants.color_front)
        title_surface = self.game.font_title.render(self.game.locale.tmenu[35], True, constants.color_title)
        title_rect = title_surface.get_rect(center=(self.size[0] // 2, self.y_100))
        self.screen.blit(title_surface, title_rect)

        h1 = 1.7 * self.y_100
        read_description(self.description, (self.size[0] - 0.4 * self.x_100, self.size[1] - h1 - self.y_100), (0.2 * self.x_100, h1),
                              self.screen,
                              self.game.font_text, color=constants.color_back)

    def stop(self):
        super().stop()


def show_cards(game, cards, Screen):
    i = 0
    n = len(cards)
    biography = list(cards)
    while 0 <= i < n:
        if n == 1:
            k = 3
        else:
            if i == 0:
                k = 0
            elif i == n - 1:
                k = 2
            else:
                k = 1
        screen = Screen(game, biography[i], k)
        screen.loop()
        res = screen.temp
        if res == 0:
            break
        i += res


class ChooseAbility(Screen):
    def __init__(self, game, last_frame):
        super().__init__(game)
        self.last_frame = last_frame
        if isinstance(last_frame, pygame.Surface):
            self.frame_surface = last_frame
        else:
            self.frame_surface = pygame.surfarray.make_surface(last_frame.swapaxes(0, 1))

        self.buttons = np.array([None]*4, dtype=pygame.Rect)
        self.button_labels = [None] * 4
        self.cord = None
        self.s = None

        # навигация/состояние
        self.hover_idx = None
        self._done = False               # чтобы не было повторного удвоения
        self.event_pos = None

        # соответствие кнопок ключам множителей
        self._keys = ('speedrun', 'biography', 'ending', 'death')
        pygame.mixer.music.stop()
        self.update()

    def update(self):
        x_100 = self.x_100
        y_100 = self.y_100
        self.cord = (self.size[0] // 4, self.size[1] // 4)

        self.pad = int(0.05 * x_100)
        pad = self.pad
        sz = (self.cord[0]*2 - pad*2, int(0.8 * y_100))
        top = 1.6 * y_100
        gap = 0.9 * y_100
        tmenu = self.game.locale.tmenu

        self.buttons[0] = pygame.Rect(self.cord[0]+pad, self.cord[1]+int(top + 0 * gap), *sz)
        self.buttons[1] = pygame.Rect(self.cord[0]+pad, self.cord[1]+int(top + 1 * gap), *sz)
        self.buttons[2] = pygame.Rect(self.cord[0]+pad, self.cord[1]+int(top + 2 * gap), *sz)
        self.buttons[3] = pygame.Rect(self.cord[0]+pad, self.cord[1]+int(top + 3 * gap), *sz)

        for i in range(len(self.buttons)):
            x = self.game.plus_factor[self._keys[i]]
            is_hover = (self.hover_idx == i)
            if is_hover:
                x *= 2
            self.button_labels[i] = f":{self._keys[i]}: {tmenu[25+i]}: +{x} {tmenu[30+i]}"

    def _commit(self, idx: int):
        if self._done:
            return
        key = self._keys[idx]
        # удвоение множителя
        self.game.plus_factor[key] *= 2
        self._done = True
        self.stop()

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == pygame.MOUSEMOTION:
            if event.pos != self.event_pos:
                self.event_pos = event.pos
                self.hover_idx = None
            for i, r in enumerate(self.buttons):
                if r.collidepoint(event.pos):
                    self.hover_idx = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover_idx is not None:
                self._commit(self.hover_idx)

        elif event.type == pygame.KEYDOWN:
            # выбор по цифрам 1..4
            if pygame.K_1 <= event.key <= pygame.K_4:
                idx = event.key - pygame.K_1
                if idx < len(self.buttons):
                    self.hover_idx = idx

            elif event.key in (pygame.K_w, pygame.K_s):
                if self.hover_idx is not None:
                    if event.key == pygame.K_s:
                        self.hover_idx = (self.hover_idx + 1) % len(self.buttons)
                    else:
                        self.hover_idx = (self.hover_idx - 1) % len(self.buttons)
                else:
                    self.hover_idx = 0

            elif event.key == pygame.K_RETURN:
                if self.hover_idx is not None:
                    self._commit(self.hover_idx)

    def draw(self):
        # фон — кадр
        self.screen.blit(pygame.transform.scale(self.frame_surface, self.size), (0, 0))

        tmenu = self.game.locale.tmenu
        # Полупрозрачный общий фон
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        overlay.fill((0,0,0, 128))
        self.screen.blit(overlay, (0, 0))
        # Светлая панель по центру
        panel = pygame.Surface((self.size[0] // 2, self.size[1] // 2), pygame.SRCALPHA)
        panel.fill((*core.constants.color_back, 128))
        self.screen.blit(panel, self.cord)

        # Заголовки
        text_surf = self.game.font.render(tmenu[29], True, constants.color_front)
        s = 2 * self.cord[0]
        text_rect = text_surf.get_rect(center=(s, 2.9 * self.y_100))
        self.screen.blit(text_surf, text_rect)
        description = res(f'subs/{self.game.settings['lang']}/1d_ability')
        read_description(description, (s-self.pad*2, self.y_100), (self.cord[0]+self.pad, 3.2 * self.y_100), self.screen, self.game.font_text)

        # Кнопки + правые подписи «+X …»
        for i, (rect, label) in enumerate(zip(self.buttons, self.button_labels)):
            is_hover = (self.hover_idx == i)
            # при наведении мышью — красная кнопка, белый текст
            # при выборе клавой — тоже подсветим красным
            if is_hover:
                color_b = constants.color_title
                color_t = constants.color_back
            else:
                color_b = constants.color_back
                color_t = constants.color_front

            self.draw_button(rect, label, False, None, color_b=color_b, color_t=color_t)

    def stop(self):
        pygame.mouse.set_visible(False)
        super().stop()
