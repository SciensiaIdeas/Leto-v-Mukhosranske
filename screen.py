import pygame
from abc import ABC, abstractmethod
import core
from text import read_description
import numpy as np


class Screen(ABC):
    def __init__(self, game, timeouit=0, music=False):
        self.game = game
        self.screen = game.screen
        self.running = True
        self.clock = pygame.time.Clock()
        self.temp = None

        self.size = self.screen.get_size()
        self.x_100 = int(0.06 * self.size[0])
        self.y_100 = int(0.097 * self.size[1])
        self._win_size_before_fs = self.size
        self.paused = False
        self.timeout = timeouit
        self.music = music

        pygame.mouse.set_visible(True)

    def _apply_resize(self, w, h):
        # пересоздаём окно и заново читаем ссылки
        self.game.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.screen = self.game.screen
        self.size = (w, h)
        self.x_100 = int(0.06 * w)
        self.y_100 = int(0.097 * h)
        self.game.init_font(w)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game.exit_game()
            self.running = False
            return
        elif event.type == pygame.VIDEORESIZE:
            self._apply_resize(event.w, event.h)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            if not self.game.fullscreen:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.game.fullscreen = True
            else:
                self.screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
                self.game.fullscreen = False

            self.screen = self.game.screen
            self.size = self.screen.get_size()
            self.x_100 = int(0.06 * self.size[0])
            self.y_100 = int(0.097 * self.size[1])

        if event.type == pygame.WINDOWMINIMIZED:
            if not self.paused:
                self.paused = True
                if self.music:
                    pygame.mixer.music.pause()
        elif event.type in (pygame.WINDOWRESTORED, pygame.WINDOWSHOWN):
            if self.paused:
                self.paused = False
                if self.music:
                    pygame.mixer.music.unpause()

    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    def loop(self):
        self.draw()
        pygame.display.flip()

        while self.running:
            if self.paused:
                evt = pygame.event.wait()  # блокирующее ожидание
                self.handle_event(evt)
                # обработаем возможный «хвост» событий
                for e in pygame.event.get():
                    self.handle_event(e)
                # при паузе ничего не обновляем/не рисуем
                continue

            evt = pygame.event.wait(self.timeout)  # 50ms for animation
            if evt.type != pygame.NOEVENT:
                self.handle_event(evt)
                for e in pygame.event.get():
                    self.handle_event(e)

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
            self.update()

    def stop(self):
        self.running = False

    @staticmethod
    def draw_button_static(rect, label, screen, font, color_b=None, color_t=None):
        if color_b is None:
            color_b = core.constants.color_menuwidget
        if color_t is None:
            color_t = core.constants.color_back
        pygame.draw.rect(screen, color_b, rect)
        emoji_size = font.size('O')
        emoji_map = core.constants.EMOJI_IMAGES
        # Разбиваем текст на части
        parts = label.split(' ')
        rendered_parts = []
        total_width = 0
        max_height = 0

        for part in parts:
            if emoji_map and part in emoji_map:
                emoji_img = pygame.transform.smoothscale(emoji_map[part], emoji_size)
                rendered_parts.append(('emoji', emoji_img))
                total_width += emoji_img.get_width() + 5
                max_height = max(max_height, emoji_img.get_height())
            else:
                text_surf = font.render(part, True, color_t)
                rendered_parts.append(('text', text_surf))
                total_width += text_surf.get_width() + 5
                max_height = max(max_height, text_surf.get_height())

        if rendered_parts:
            total_width -= 5  # убираем последний пробел

        # Вычисляем начальную координату X для центрирования всей строки
        x = rect.x + (rect.width - total_width) // 2
        y = rect.y + (rect.height - max_height) // 2

        for kind, surf in rendered_parts:
            screen.blit(surf, (x, y))
            x += surf.get_width() + 5
        return x, y

    def draw_button(self, rect, label, mode, var, color_b=None, color_t=None):
        if color_b is None:
            color_b = core.constants.color_menuwidget
        if color_t is None:
            color_t = core.constants.color_back

        if mode and not var:
            surf = pygame.Surface(rect.size)
            surf.fill(color_b)
            surf.set_alpha(128)
            self.screen.blit(surf, rect)
        else:
            pygame.draw.rect(self.screen, color_b, rect)

        emoji_size = self.game.font.size('O')
        emoji_map = core.constants.EMOJI_IMAGES
        # Разбиваем текст на части
        parts = label.split(' ')
        rendered_parts = []
        total_width = 0
        max_height = 0

        for part in parts:
            if emoji_map and part in emoji_map:
                emoji_img = pygame.transform.smoothscale(emoji_map[part], emoji_size)
                rendered_parts.append(('emoji', emoji_img))
                total_width += emoji_img.get_width() + 5
                max_height = max(max_height, emoji_img.get_height())
            else:
                text_surf = self.game.font.render(part, True, color_t)
                rendered_parts.append(('text', text_surf))
                total_width += text_surf.get_width() + 5
                max_height = max(max_height, text_surf.get_height())

        if rendered_parts:
            total_width -= 5  # убираем последний пробел

        # Вычисляем начальную координату X для центрирования всей строки
        x = rect.x + (rect.width - total_width) // 2
        y = rect.y + (rect.height - max_height) // 2

        for kind, surf in rendered_parts:
            self.screen.blit(surf, (x, y))
            x += surf.get_width() + 5

    def draw_badge(self, anchor_rect, count):
        game = self.game
        if count <= 0:
            return
        text = str(count)
        ts = game.font_text.render(text, True, core.constants.color_back)

        pad = min(0.04 * self.x_100, 0.04 * self.y_100)
        r = max(ts.get_width(), ts.get_height()) + pad
        # позиция бейджа — правый верхний угол anchor_rect
        cx = anchor_rect.right - pad
        cy = anchor_rect.top + pad
        badge_rect = pygame.Rect(0, 0, r, r)
        badge_rect.midleft = (cx, cy)

        pygame.draw.circle(self.screen, core.constants.color_title, badge_rect.center, r // 2)
        ts_rect = ts.get_rect(center=badge_rect.center)
        self.screen.blit(ts, ts_rect)

    def draw_badge_internal(self, x, y):
        ts = self.game.font.render("new*", True, core.constants.color_pr)
        pad = int(0.2 * self.y_100)
        ts_rect = ts.get_rect(bottomleft=(x,y+pad))
        self.screen.blit(ts, ts_rect)
        return ts_rect.topright


class SettingsScreen(Screen):
    def __init__(self, game, last_frame, _type: int):
        super().__init__(game)
        if isinstance(last_frame, pygame.Surface):
            base = last_frame
        else:
            base = pygame.surfarray.make_surface(last_frame.swapaxes(0, 1))

        self.frame_surface = base.convert()

        self.buttons = np.array([None]*4, dtype=pygame.Rect)
        self.button_labels = [None] * 4
        # навигация/состояние
        self.hover_idx = None
        self.event_pos = None
        self.N = 6
        self._type = _type
        self.update()

    def update(self):
        x_100 = self.x_100
        y_100 = self.y_100
        s1 = 0.4 * y_100
        tmenu = self.game.locale.tmenu

        self.buttons[0] = pygame.Rect(x_100, 3.9*y_100, 3*x_100, s1)
        self.button_labels[0] = tmenu[15]
        self.buttons[1] = pygame.Rect(x_100, 4.5 * y_100, 3 * x_100, s1)
        self.button_labels[1] = tmenu[16]
        self.buttons[2] = pygame.Rect(x_100, 5.1 * y_100, 3 * x_100, s1)
        self.button_labels[2] = tmenu[36]
        self.buttons[3] = pygame.Rect(x_100, 5.7 * y_100, 3 * x_100, s1)
        self.button_labels[3] = tmenu[17]

    def _commit(self, pos):
        i = self.hover_idx
        if i == 0:
            x_100 = self.x_100
            self.game.settings['volume'] = (pos[0] - x_100) / (2 * x_100)
            if self.game.fight_ss and self.game.fight_ss.get_busy():
                core.constants.fight_s.set_volume(self.game.settings['volume'] / 2)
            core.constants.click.play()
        elif i == 1:
            self.game.settings['subtitles'] = not self.game.settings['subtitles']
            core.constants.click.play()
        elif i == 2:    # Продолжить
            core.constants.click.play()
            self.stop()
        elif i == 3:    # Сохраниться
            link = self.game.frame.link
            if link not in core.constants.saves_range:
                self.game.frame.time_s = self.game.time_s
                self.game.frame.temp_s = self.game.temp
                self.game.saves['load'] = self.game.frame
            else:
                # save when last possibility is
                self.game.saves['load'] = self.game.saves['continue']
            core.constants.click.play()
            self.stop()
        elif i == 4:    # Подсказка
            title = self.game.locale.tmenu[36+self._type]
            content = core.res(f'subs/{self.game.settings['lang']}/tip{self._type}')
            sc = Information(self.game, self.frame_surface, title, content)
            sc.loop()
        else:   # Выход в меню
            if self.game.fight_ss and self.game.fight_ss.get_busy():
                self.game.fight_ss.stop()
            core.constants.click.play()
            self.temp = True
            self.stop()

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            x_100 = self.x_100
            y_100 = self.y_100

            if event.pos != self.event_pos:
                self.event_pos = event.pos
                self.hover_idx = None

            if x_100 < x < 3 * x_100 and 2.5 * y_100 < y < 2.7 * y_100:
                self.hover_idx = 0
            elif 2.8 * x_100 < x < 3.1 * x_100 and 3 * y_100 < y < 3.3 * y_100:
                self.hover_idx = 1
            else:
                for i, r in enumerate(self.buttons, 2):
                    if r.collidepoint(event.pos):
                        self.hover_idx = i
                        break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover_idx is not None:
                self._commit(event.pos)

        if event.type == pygame.KEYDOWN:
            # выбор по цифрам 1..6
            if pygame.K_1 <= event.key <= pygame.K_6:
                idx = event.key - pygame.K_1
                if idx < self.N:
                    self.hover_idx = idx

            elif event.key in (pygame.K_w, pygame.K_s):
                if self.hover_idx is not None:
                    if event.key == pygame.K_s:
                        self.hover_idx = (self.hover_idx + 1) % self.N
                    else:
                        self.hover_idx = (self.hover_idx - 1) % self.N
                else:
                    self.hover_idx = 0

            elif event.key in (pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT) and self.hover_idx == 0:
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    new = self.game.settings['volume'] - 0.05
                    self.game.settings['volume'] = max(0, new)
                else:
                    new = self.game.settings['volume'] + 0.05
                    self.game.settings['volume'] = min(1, new)

                if self.game.fight_ss and self.game.fight_ss.get_busy():
                    core.constants.fight_s.set_volume(self.game.settings['volume'] / 2)

            elif event.key == pygame.K_RETURN:
                if self.hover_idx is not None:
                    self._commit(None)

            elif event.key == pygame.K_ESCAPE:
                self.stop()

    def draw(self):
        self.screen.blit(pygame.transform.scale(self.frame_surface, self.size), (0, 0))
        tmenu = self.game.locale.tmenu

        x_100 = self.x_100
        y_100 = self.y_100
        width = 2*x_100; height = 0.2*y_100

        # Полупрозрачный фон
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        overlay.fill((0,0,0, 128))
        self.screen.blit(overlay, (0, 0))
        overlay = pygame.Surface((self.size[0] // 3, self.size[1]), pygame.SRCALPHA)
        overlay.fill((*core.constants.color_back, 128))
        self.screen.blit(overlay, (0, 0))

        self.screen.blit(self.game.font.render(tmenu[12], True, core.constants.color_front), (1.2*x_100, y_100))
        self.screen.blit(self.game.font.render(tmenu[13], True, core.constants.color_front), (x_100, 2*y_100))

        x = x_100; y = 2.5*y_100
        pygame.draw.rect(self.screen, core.constants.color_menuwidget, (x, y, width, height))
        if self.hover_idx == 0:
            c = core.constants.color_title
        else:
            c = core.constants.color_back
        pygame.draw.rect(self.screen, c, (x, y, self.game.settings['volume'] * width, height))

        # Чекбокс субтитров
        x = 2.8*x_100; y = 3*y_100; s = 0.3*x_100
        self.screen.blit(self.game.font.render(tmenu[14], True, core.constants.color_front), (x_100, y - 3))
        if self.hover_idx == 1:
            c = core.constants.color_menuwidget_clicked
        else:
            c = core.constants.color_menuwidget
        pygame.draw.rect(self.screen, c, (x, y, s, s))
        if self.game.settings['subtitles']:
            pygame.draw.line(self.screen, core.constants.color_back, (x, y), (x + s, y + s), 3)
            pygame.draw.line(self.screen, core.constants.color_back, (x, y + s), (x + s, y), 3)

        # Кнопки
        for i, (rect, label) in enumerate(zip(self.buttons, self.button_labels), 2):
            is_hover = (self.hover_idx == i)
            if is_hover:
                color_b = core.constants.color_menuwidget_clicked
            else:
                color_b = core.constants.color_menuwidget
            self.draw_button(rect, label, False, None, color_b=color_b)

        k = 1.5 * y_100
        self.screen.blit(pygame.transform.scale(core.constants.clock_icon, (k, k)), (1.8*x_100, 7.6*y_100))
        self.screen.blit(self.game.font_title.render(self.game.time.strftime('%H:%M:%S'), True, core.constants.color_front), (1.3*x_100, 9.5*y_100))

    def stop(self):
        pygame.mixer.music.set_volume(self.game.settings['volume'])
        core.constants.click.set_volume(0.3 * self.game.settings['volume'])
        super().stop()


class EndingScreen(Screen):
    def __init__(self, game, link, n=None):
        super().__init__(game, music=bool(n is None))
        self.link = link
        self.image = pygame.image.load(core.res(f'media/end{link}.jpg'))
        self.description = core.res(f'subs/{game.settings['lang']}/end{link}')
        if n is None:
            pygame.mixer.music.load(core.res('media/end.mp3'))
            pygame.mixer.music.set_volume(0.5 * game.settings['volume'])
            pygame.mixer.music.play(loops=-1)
        self.N = n

        self.buttons = np.array([None]*2, dtype=pygame.Rect)
        self.button_labels = [None] * 2
        self.update()

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.buttons[0].collidepoint(event.pos):
                core.constants.click.play()
                self._left_action()
            elif self.buttons[1].collidepoint(event.pos):
                core.constants.click.play()
                self._right_action()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self._left_action()
            elif event.key == pygame.K_d:
                self._right_action()
            elif event.key == pygame.K_ESCAPE:
                if self.N is not None:
                    self.temp = 0
                self.stop()

    def _left_action(self):
        if self.N is not None:
            self.temp = -1
        self.stop()

    def _right_action(self):
        if self.N is not None:
            self.temp = 1
        else:
            self.temp = True
        self.stop()

    def update(self):
        x_100 = self.x_100
        y_100 = self.y_100
        w = 2.5 * x_100
        h = y_100 // 2
        tmenu = self.game.locale.tmenu

        self.buttons[0] = pygame.Rect(x_100 // 2, self.size[1] - y_100, w, h)
        if self.N is None:
            t = tmenu[18]
        else:
            t = tmenu[7] if self.N == 0 or self.N == 3 else tmenu[9]
        self.button_labels[0] = t
        self.buttons[1] = pygame.Rect(self.size[0] - 3 * x_100, self.size[1] - y_100, w, h)
        if self.N is None:
            t = tmenu[7]
        else:
            t = tmenu[7] if self.N == 2 or self.N == 3 else tmenu[10]
        self.button_labels[1] = t

    def draw(self):
        x_100 = self.x_100
        y_100 = self.y_100

        h1 = int(self.size[1] * 0.45)
        w1 = (self.size[0] - 16*h1/9) // 2
        ending_image = pygame.transform.scale(self.image, (16*h1//9, h1))

        self.screen.fill(core.constants.color_back)
        name = self.game.cache['endings'][self.link].text(self.game.locale.txt)
        title_surface = self.game.font_title.render(name, True, core.constants.color_title)
        title_rect = title_surface.get_rect(center=(self.size[0] // 2, 0.6*y_100))
        self.screen.blit(title_surface, title_rect)
        if self.N is not None and self.link in self.game.unseen['endings']:
            self.draw_badge_internal(*title_rect.topright)
            self.mark = True
        else:
            self.mark = False
        self.screen.blit(ending_image, (w1, 1.2*y_100))

        read_description(self.description, (self.size[0]-0.4*x_100, h1-3*y_100), (0.2*x_100, h1+1.5*y_100), self.screen, self.game.font_text)
        for rect, label in zip(self.buttons, self.button_labels):
            self.draw_button(rect, label, False, None)

    def stop(self):
        if self.N is None:
            pygame.mixer.music.stop()
        elif self.mark:
            self.game.unseen['endings'].remove(self.link)
        super().stop()


class Information(Screen):
    def __init__(self, game, last_frame, title: str, content):
        super().__init__(game)
        if isinstance(last_frame, pygame.Surface):
            base = last_frame
        else:
            base = pygame.surfarray.make_surface(last_frame.swapaxes(0, 1))

        self.frame_surface = base.convert()
        self.buttons = None
        self.button_labels = None
        self.title = title
        self.content = content
        self.update()

    def update(self):
        x_100 = self.x_100
        y_100 = self.y_100
        self.cord = (self.size[0] // 4, self.size[1] // 4)
        self.pad = int(0.05 * x_100)

        w = 1.8 * x_100
        h = y_100 // 2
        self.buttons = pygame.Rect((self.cord[0]*2 - w//2), self.cord[1]*3 - y_100*0.8, w, h)
        self.button_labels = "OK"

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.buttons.collidepoint(event.pos):
                core.constants.click.play()
                self.stop()
        if event.type == pygame.KEYDOWN:
            self.stop()

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

        # заголовок
        title_surf = self.game.font.render(self.title, True, core.constants.color_front)
        s = 2 * self.cord[0]
        text_rect = title_surf.get_rect(center=(s, 2.9 * self.y_100))
        self.screen.blit(title_surf, text_rect)
        y = text_rect.bottom + int(0.04 * self.y_100)
        pygame.draw.line(self.screen, core.constants.color_front, (self.cord[0], y), (self.cord[0]*3, y), width=3)

        # текст
        py = 3.2 * self.y_100
        pad_y = 2 * self.cord[1] - py - self.y_100 * 1.5
        read_description(self.content, (s - self.pad * 2, pad_y), (self.cord[0] + self.pad, py),
                         self.screen, self.game.font_text)

        # кнопка "OK"
        self.draw_button(self.buttons, self.button_labels, False, None)